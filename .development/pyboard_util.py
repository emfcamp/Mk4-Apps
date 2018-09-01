from pyboard import Pyboard, PyboardError
import glob, sys, pyboard, json, binascii, os, hashlib

_pyb = None

def get_pyb(args):
    global _pyb
    if not _pyb:
        print("Connected to badge:", end="", flush=True)
        if not args.device:
            args.device = find_tty()

         # open the connection to the pyboard
        try:
            _pyb = Pyboard(args.device, args.baudrate, None, None, args.wait)
        except PyboardError as er:
            print(" FAIL")
            print(er)
            sys.exit(1)
        print(" DONE")
    return _pyb

def close_pyb():
    global _pyb
    if _pyb:
        _pyb.close()

def stop_badge(args, verbose):
    pyb = get_pyb(args)
    print("Stopping running app:", end="", flush=True)
    write_command(pyb, b'\r\x03\x03') # ctrl-C twice: interrupt any running program
    n = pyb.serial.inWaiting()
    while n > 0:
        pyb.serial.read(n)
        n = pyb.serial.inWaiting()
    print(" DONE")

def write_command(pyb, command):
    flush_input(pyb)
    pyb.serial.write(command)
    flush_input(pyb)

def flush_input(pyb):
    n = pyb.serial.inWaiting()
    while n > 0:
        pyb.serial.read(n)
        n = pyb.serial.inWaiting()

def soft_reset(args, verbose = True):
    pyb = get_pyb(args)
    if verbose:
        print("Soft reboot:", end="", flush=True)
    write_command(pyb, b'\x04') # ctrl-D: soft reset
    data = pyb.read_until(1, b'soft reboot\r\n')
    if data.endswith(b'soft reboot\r\n'):
        if verbose:
            print(" DONE")
    else:
        if verbose:
            print(" FAIL")
        raise PyboardError('could not soft reboot')

def find_tty():
    # Todo: test in linux, let user pick if multiple ports are available
    for pattern in ['/dev/ttyACM*', '/dev/tty.usbmodemTiLDA*', '/dev/tty.usbmodem*']:
        for path in glob.glob(pattern):
            return path

    if sys.platform.startswith('win'):
        import serial
        for port in ['COM%s' % (i + 1) for i in range(256)]:
            try:
                s = serial.Serial(port)
                s.close()
                return port
            except (OSError, serial.SerialException):
                pass

    print("Couldn't find badge tty - Please make it's plugged in and reset it if necessary")
    sys.exit(1)

def check_run(paths):
    for filename in paths:
        with open(filename, 'r', encoding='utf8') as f:
            pyfile = f.read()
            compile(pyfile + '\n', filename, 'exec')

def execbuffer(pyb, buf):
    try:
        ret, ret_err = pyb.exec_raw(buf, timeout=None, data_consumer=pyboard.stdout_write_bytes)
    except PyboardError as er:
        print(er)
        pyb.close()
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)
    if ret_err:
        pyb.exit_raw_repl()
        pyb.close()
        pyboard.stdout_write_bytes(ret_err)
        sys.exit(1)

def returnbuffer(pyb, buf):
    res = b''
    def add_to_res(b):
        nonlocal res
        res += b
    try:
        ret, ret_err = pyb.exec_raw(buf, timeout=None, data_consumer=add_to_res)
    except PyboardError as er:
        print(er)
        pyb.close()
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)
    if ret_err:
        pyb.exit_raw_repl()
        pyb.close()
        pyboard.stdout_write_bytes(ret_err)
        sys.exit(1)
    return res.decode('ascii').strip()

def run(args, paths, verbose=True):
    pyb = get_pyb(args)

    if verbose:
        print("Preparing execution:", end=" ", flush=True)
    # run any command or file(s) - this is mostly a copy from pyboard.py
    if len(paths):
        # we must enter raw-REPL mode to execute commands
        # this will do a soft-reset of the board
        try:
            pyb.enter_raw_repl()
        except PyboardError as er:
            if verbose:
                print(" FAIL")
            print(er)
            pyb.close()
            sys.exit(1)
        if verbose:
            print(" DONE")

        try:
            # run any files
            for filename in paths:
                with open(filename, 'rb') as f:
                    print("-------- %s --------" % filename)
                    pyfile = f.read()
                    execbuffer(pyb, pyfile)

            # exiting raw-REPL just drops to friendly-REPL mode
            pyb.exit_raw_repl()
        except OSError as e:
            if "Device not configured" in str(e):
                print("Connection to badge lost") # This can happen on a hard rest
            else:
                raise e

# Please don't judge me too harshly for this hack, I had lots of problems with the
# USB mass storage protocol and at some point it looked simpler to just avoid it
# altogether. This _seems_ to work, so maybe it isn't that terrible after all.

def init_copy_via_repl(args):
    pyb = get_pyb(args)
    print("Init copy via repl:", end=" ", flush=True)
    try:
        pyb.enter_raw_repl()
        with open(os.path.join(os.path.dirname(__file__), "copy_via_repl_header.py"), "rt") as f:
            execbuffer(pyb, f.read())

    except PyboardError as er:
        print("FAIL")
        print(er)
        pyb.close()
        sys.exit(1)

    print("DONE")

def copy_via_repl(args, path, rel_path):
    with open(path, "rb") as f:
        return write_via_repl(args, f.read(), rel_path)

def write_via_repl(args, content, rel_path):
    pyb = get_pyb(args)
    h = hashlib.sha256()
    h.update(content)
    content = binascii.b2a_base64(content).decode('ascii').strip()
    if os.sep != '/':
        rel_path = rel_path.replace(os.sep, '/')
    rel_path_as_string = json.dumps(rel_path) # make sure quotes are escaped
    cmd = "h(%s)" % rel_path_as_string
    badge_hash = returnbuffer(pyb,cmd).splitlines()[0]
    local_hash = str(binascii.hexlify(h.digest()), "utf8")[:10]
    if badge_hash == local_hash:
        # we don't need to update those files
        return False

    cmd = "w(%s, \"%s\")\n" % (rel_path_as_string, content)
    result = returnbuffer(pyb,cmd)
    if "OK" in result:
        return True
    raise Exception("Couldn't write %s to badge: %s" % (rel_path, result))

def end_copy_via_repl(args):
    # do we need to do anything?
    pass

def clean_via_repl(args):
    init_copy_via_repl(args)
    print("Cleaning:", end=" ", flush=True)
    try:
        execbuffer(get_pyb(args), "clean()")
    except PyboardError as er:
        print("FAIL")
        print(er)
        pyb.close()
        sys.exit(1)
    print("DONE")

def hard_reset(args):
    pyb = get_pyb(args)
    print("Hard reset:", end=" ", flush=True)
    try:
        pyb.enter_raw_repl()
        execbuffer(pyb, "import machine\nmachine.reset()\n")
        print("UNEXPECTED")
    except PyboardError as er:
        print("FAIL")
        print(er)
        pyb.close()
        sys.exit(1)
    except Exception as e:
        if "Errno 6" in str(e):
            print("DONE")
        else:
            raise e

