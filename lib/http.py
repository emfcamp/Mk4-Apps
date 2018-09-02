"""HTTP library specially tied to TiLDAs functionality

Somewhat inspired by "request".

Current known issues:
* HTTPS is not supported
"""

___license___ = "MIT"
___dependencies___ = ["urlencode", "wifi"]

import usocket, ujson, os, time, gc, wifi, ussl
from urlencode import urlencode

"""Usage
from http_client import *
print(get("http://example.com").raise_for_status().content)
post("http://mydomain.co.uk/api/post", data="SOMETHING").raise_for_status().close() # If response is not consumed you need to close manually
# Or, if you prefer the with syntax:
with post("http://mydomain.co.uk/api/post", urlencoded="SOMETHING") as response:
    response.raise_for_error() # No manual close needed
"""

SUPPORT_TIMEOUT = hasattr(usocket.socket, 'settimeout')
CONTENT_TYPE_JSON = 'application/json'
BUFFER_SIZE = 1024

class Response(object):
    def __init__(self):
        self.encoding = 'utf-8'
        self.headers = {}
        self.status = None
        self.socket = None
        self._content = None

    # Hands the responsibility for a socket over to this reponse. This needs to happen
    # before any content can be inspected
    def add_socket(self, socket, content_so_far):
        self.content_so_far = content_so_far
        self.socket = socket

    @property
    def content(self, timeout=90):
        start_time = time.time()
        if not self._content:
            if not self.socket:
                raise OSError("Invalid response socket state. Has the content been downloaded instead?")
            try:
                if "Content-Length" in self.headers:
                    content_length = int(self.headers["Content-Length"])
                elif "content-length" in self.headers:
                    content_length = int(self.headers["content-length"])
                else:
                    raise Exception("No Content-Length")
                self._content = self.content_so_far
                del self.content_so_far
                while len(self._content) < content_length:
                    buf = self.socket.recv(BUFFER_SIZE)
                    self._content += buf
                    if (time.time() - start_time) > timeout:
                        raise Exception("HTTP request timeout")

            finally:
                self.close()
        return self._content;

    @property
    def text(self):
        return str(self.content, self.encoding) if self.content else ''

    # If you don't use the content of a Response at all you need to manually close it
    def close(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def json(self):
        try:
            return ujson.loads(self.text)
        except ValueError as e:
            print("Invalid JSON: %s" % self.text)
            raise(e)

    # Writes content into a file. This function will write while receiving, which avoids
    # having to load all content into memory
    def download_to(self, target, timeout=90):
        start_time = time.time()
        if not self.socket:
            raise OSError("Invalid response socket state. Has the content already been consumed?")
        try:
            if "Content-Length" in self.headers:
                remaining = int(self.headers["Content-Length"])
            elif "content-length" in self.headers:
                remaining = int(self.headers["content-length"])
            else:
                raise Exception("No Content-Length")

            with open(target, 'wb') as f:
                f.write(self.content_so_far)
                remaining -= len(self.content_so_far)
                del self.content_so_far
                while remaining > 0:
                    buf = self.socket.recv(BUFFER_SIZE)
                    f.write(buf)
                    remaining -= len(buf)

                    if (time.time() - start_time) > timeout:
                        raise Exception("HTTP request timeout")

                f.flush()
            os.sync()

        finally:
            self.close()

    def raise_for_status(self):
        if 400 <= self.status < 500:
            raise OSError('Client error: %s' % self.status)
        if 500 <= self.status < 600:
            raise OSError('Server error: %s' % self.status)
        return self

    # In case you want to use "with"
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

def open_http_socket(method, url, json=None, timeout=None, headers=None, data=None, params=None):
    # This will immediately return if we're already connected, otherwise
    # it'll attempt to connect or prompt for a new network. Proceeding
    # without an active network connection will cause the getaddrinfo to
    # fail.
    wifi.connect(
        wait=True,
        show_wait_message=False,
        prompt_on_fail=True,
        dialog_title='TiLDA Wifi'
    )

    urlparts = url.split('/', 3)
    proto = urlparts[0]
    host = urlparts[2]
    urlpath = '' if len(urlparts) < 4 else urlparts[3]

    if proto == 'http:':
        port = 80
    elif proto == 'https:':
        port = 443
    else:
        raise OSError('Unsupported protocol: %s' % proto[:-1])

    if ':' in host:
        host, port = host.split(':')
        port = int(port)

    if data is not None:
        if isinstance(data, str):
            content = data
            content_type = "text/plain; charset=UTF-8"
        else:
            content = urlencode(data)
            content_type = "application/x-www-form-urlencoded"
    elif json is not None:
        content = ujson.dumps(json)
        content_type = CONTENT_TYPE_JSON
    else:
        content = None

    # ToDo: Handle IPv6 addresses
    addr = get_address_info(host, port)

    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)

    if params:
        urlpath += "?" + urlencode(params)

    sock.connect(addr)

    if proto == 'https:':
        sock = ussl.wrap_socket(sock, ca_certs="DST Root CA X3", cert_reqs=ussl.CERT_OPTIONAL)

    sock.send('%s /%s HTTP/1.0\r\nHost: %s\r\n' % (method, urlpath, host))

    if headers is not None:
        for header in headers.items():
            sock.send('%s: %s\r\n' % header)

    if content is not None:
        sock.send('content-length: %s\r\n' % len(content))
        sock.send('content-type: %s\r\n' % content_type)
        sock.send('\r\n')
        sock.send(content)
    else:
        sock.send('\r\n')

    return sock

def get_address_info(host, port, retries_left = 20):
    try:
        return usocket.getaddrinfo(host, port)[0][4]
    except OSError as e:
        if ("-15" in str(e)) and retries_left:
            # [addrinfo error -15]
            # This tends to happen after startup and goes away after a while
            time.sleep_ms(200)
            return get_address_info(host, port, retries_left - 1)
        else:
            raise e

# Adapted from upip
def request(method, url, json=None, timeout=None, headers=None, data=None, params=None):
    sock = open_http_socket(method, url, json, timeout, headers, data, params)
    try:
        response = Response()
        state = 1
        hbuf = b""
        while True:
            buf = sock.recv(BUFFER_SIZE)
            if state == 1: # Status
                nl = buf.find(b"\n")
                if nl > -1:
                    hbuf += buf[:nl - 1]
                    response.status = int(hbuf.split(b' ')[1])
                    state = 2
                    hbuf = b"";
                    buf = buf[nl + 1:]
                else:
                    hbuf += buf

            if state == 2: # Headers
                hbuf += buf
                nl = hbuf.find(b"\n")
                while nl > -1:
                    if nl < 2:
                        buf = hbuf[2:]
                        hbuf = None
                        state = 3
                        break

                    header = hbuf[:nl - 1].decode("utf8").split(':', 3)
                    response.headers[header[0].strip()] = header[1].strip()
                    hbuf = hbuf[nl + 1:]
                    nl = hbuf.find(b"\n")

            if state == 3: # Content
                response.add_socket(sock, buf)
                sock = None # It's not our responsibility to close the socket anymore
                return response
    finally:
        if sock: sock.close()
        gc.collect()

def get(url, **kwargs):
    return request('GET', url, **kwargs)

def post(url, **kwargs):
    return request('POST', url, **kwargs)

def is_ipv4_address(address):
    octets = address.split('.')
    try:
        valid_octets = [x for x in octets if 0 <= int(x) and int(x) <= 255]
        return len(valid_octets) == 4
    except Exception:
        return False
