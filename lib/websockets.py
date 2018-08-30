"""
Websockets client for micropython

Based off https://github.com/danni/uwebsockets
"""


import ure as re
import ubinascii as binascii
import ustruct as struct
import urandom as random
import usocket as socket
from ucollections import namedtuple

# Opcodes
OP_CONT = const(0x0)
OP_TEXT = const(0x1)
OP_BYTES = const(0x2)
OP_CLOSE = const(0x8)
OP_PING = const(0x9)
OP_PONG = const(0xa)

# Close codes
CLOSE_OK = const(1000)
CLOSE_GOING_AWAY = const(1001)
CLOSE_PROTOCOL_ERROR = const(1002)
CLOSE_DATA_NOT_SUPPORTED = const(1003)
CLOSE_BAD_DATA = const(1007)
CLOSE_POLICY_VIOLATION = const(1008)
CLOSE_TOO_BIG = const(1009)
CLOSE_MISSING_EXTN = const(1010)
CLOSE_BAD_CONDITION = const(1011)

URL_RE = re.compile(r'ws://([A-Za-z0-9\-\.]+)(?:\:([0-9]+))?(/.+)?')
URI = namedtuple('URI', ('hostname', 'port', 'path'))

DEBUG = False

# Call this to spew the headers etc
def enable_debug():
    global DEBUG
    DEBUG = True

def debug_log(*args, **kwargs):
    if DEBUG:
        print(args)

def urlparse(uri):
    """Parse ws:// URLs"""
    match = URL_RE.match(uri)
    if match:
        hostname = match.group(1)
        port = int(match.group(2)) if match.group(2) else 80
        path = match.group(3)
        return URI(hostname, port, path)


class Websocket:
    """
    Basis of the Websocket protocol.

    This can probably be replaced with the C-based websocket module, but
    this one currently supports more options.
    """
    is_client = False

    def __init__(self, sock):
        self._sock = sock
        self.open = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        debug_log("exited context manager")
        self.close()

    def settimeout(self, timeout):
        self._sock.settimeout(timeout)

    def read_frame(self, max_size=None):
        """
        Read a frame from the socket.
        See https://tools.ietf.org/html/rfc6455#section-5.2 for the details.
        """

        # Frame header
        byte1, byte2 = struct.unpack('!BB', self._sock.recv(2))

        debug_log("read a frame header: {} {}".format(byte1, byte2))

        # Byte 1: FIN(1) _(1) _(1) _(1) OPCODE(4)
        fin = bool(byte1 & 0x80)
        opcode = byte1 & 0x0f


        # Byte 2: MASK(1) LENGTH(7)
        mask = bool(byte2 & (1 << 7))
        length = byte2 & 0x7f

        if length == 126:  # Magic number, length header is 2 bytes
            debug_log("length is 126")
            length, = struct.unpack('!H', self._sock.recv(2))
        elif length == 127:  # Magic number, length header is 8 bytes
            debug_log("length is 127")
            length, = struct.unpack('!Q', self._sock.recv(8))
        else:
            debug_log("length is something else: {}".format(length))

        if mask:  # Mask is 4 bytes
            mask_bits = self._sock.recv(4)

        if length:
            debug_log("Trying to receive {} bytes".format(length))
            try:
                data = self._sock.recv(length)
            except MemoryError:
                # We can't receive this many bytes, close the socket
                debug_log("Frame of length %s too big. Closing",
                                        length)
                self.close(code=CLOSE_TOO_BIG)
                return True, OP_CLOSE, None
        else:
            data = b''

        if mask:
            data = bytes(b ^ mask_bits[i % 4]
                         for i, b in enumerate(data))

        return fin, opcode, data

    def write_frame(self, opcode, data=b''):
        """
        Write a frame to the socket.
        See https://tools.ietf.org/html/rfc6455#section-5.2 for the details.
        """
        fin = True
        mask = self.is_client  # messages sent by client are masked

        length = len(data)

        # Frame header
        # Byte 1: FIN(1) _(1) _(1) _(1) OPCODE(4)
        byte1 = 0x80 if fin else 0
        byte1 |= opcode

        # Byte 2: MASK(1) LENGTH(7)
        byte2 = 0x80 if mask else 0

        if length < 126:  # 126 is magic value to use 2-byte length header
            byte2 |= length
            self._sock.send(struct.pack('!BB', byte1, byte2))

        elif length < (1 << 16):  # Length fits in 2-bytes
            byte2 |= 126  # Magic code
            self._sock.send(struct.pack('!BBH', byte1, byte2, length))

        elif length < (1 << 64):
            byte2 |= 127  # Magic code
            self._sock.send(struct.pack('!BBQ', byte1, byte2, length))

        else:
            raise ValueError()

        if mask:  # Mask is 4 bytes
            mask_bits = struct.pack('!I', random.getrandbits(32))
            self._sock.send(mask_bits)

            data = bytes(b ^ mask_bits[i % 4]
                         for i, b in enumerate(data))

        self._sock.send(data)

    def recv(self):
        """
        Receive data from the websocket.

        This is slightly different from 'websockets' in that it doesn't
        fire off a routine to process frames and put the data in a queue.
        If you don't call recv() sufficiently often you won't process control
        frames.
        """
        assert self.open

        while self.open:
            try:
                fin, opcode, data = self.read_frame()
            except ValueError:
                debug_log("Failed to read frame. Socket dead.")
                self._close()
                return

            debug_log("Got a frame with opcode {}".format(opcode))
            if not fin:
                raise NotImplementedError()

            if opcode == OP_TEXT:
                return data.decode('utf-8')
            elif opcode == OP_BYTES:
                return data
            elif opcode == OP_CLOSE:
                debug_log("got a close frame")
                self._close()
                return
            elif opcode == OP_PONG:
                # Ignore this frame, keep waiting for a data frame
                continue
            elif opcode == OP_PING:
                # We need to send a pong frame
                debug_log("Sending PONG")
                self.write_frame(OP_PONG, data)
                # And then wait to receive
                continue
            elif opcode == OP_CONT:
                # This is a continuation of a previous frame
                raise NotImplementedError(opcode)
            else:
                raise ValueError(opcode)

    def send(self, buf):
        """Send data to the websocket."""

        assert self.open

        if isinstance(buf, str):
            opcode = OP_TEXT
            buf = buf.encode('utf-8')
        elif isinstance(buf, bytes):
            opcode = OP_BYTES
        else:
            raise TypeError()

        self.write_frame(opcode, buf)

    def close(self, code=CLOSE_OK, reason=''):
        """Close the websocket."""
        if not self.open:
            return

        buf = struct.pack('!H', code) + reason.encode('utf-8')

        self.write_frame(OP_CLOSE, buf)
        self._close()

    def _close(self):
        debug_log("Connection closed")
        self.open = False
        self._sock.close()

def readline(sock):
    # Micropython on the Mk3 doesn't have socket.readline
    try:
        line = sock.readline()[:-2]
        debug_log("readline:")
        debug_log(line)
        return line
    except AttributeError:
        line = b''
        while True:
            chunk = sock.recv(2)
            if chunk == b'\r\n':
                debug_log("Read line:")
                debug_log(line)
                return line
            else:
                line += chunk


class WebsocketClient(Websocket):
    is_client = True

def connect(uri):
    """
    Connect a websocket.
    """

    uri = urlparse(uri)
    assert uri

    debug_log("open connection %s:%s",
                                uri.hostname, uri.port)

    sock = socket.socket()
    debug_log("got a socket")
    try:
        addr = socket.getaddrinfo(uri.hostname, uri.port)
        debug_log("getaddrinfo result")
        debug_log(addr)
        sock.connect(addr[0][4])
        debug_log("connected using getaddrinfo method")
    except OSError:
        debug_log("getaddrinfo method failed")
        sock.connect((uri.hostname, uri.port))
        debug_log("connected using direct method")

    def send_header(header, *args):
        debug_log(str(header), *args)
        sock.send(header % args + '\r\n')

    # Sec-WebSocket-Key is 16 bytes of random base64 encoded
    key = binascii.b2a_base64(bytes(random.getrandbits(8)
                                    for _ in range(16)))[:-1]
    debug_log("set key to:")
    debug_log(key)

    send_header(b'GET %s HTTP/1.1', uri.path or '/')
    send_header(b'Host: %s:%s', uri.hostname, uri.port)
    send_header(b'Connection: Upgrade')
    send_header(b'Upgrade: websocket')
    send_header(b'Sec-WebSocket-Key: %s', key)
    send_header(b'Sec-WebSocket-Version: 13')
    send_header(b'Origin: http://localhost')
    send_header(b'')

    header = readline(sock)
    assert header[:13] == b'HTTP/1.1 101 ', header

    # We don't (currently) need these headers
    # FIXME: should we check the return key?
    while header:
        debug_log(str(header))
        header = readline(sock)

    return WebsocketClient(sock)
