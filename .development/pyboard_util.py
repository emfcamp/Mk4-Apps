from pyboard import Pyboard, PyboardError
import glob, sys, pyboard

_pyb = None

def get_pyb(args):
    global _pyb
    if not _pyb:
        if not args.device:
            args.device = find_tty()

         # open the connection to the pyboard
        try:
            _pyb = Pyboard(args.device, args.baudrate, None, None, args.wait)
        except PyboardError as er:
            print(er)
            sys.exit(1)
        print("Connected to badge.")

    return _pyb

def close_pyb():
    global _pyb
    if _pyb:
        _pyb.close()

def stop_badge(args):
    pyb = get_pyb(args)
    print("stopping running app")
    write_command(pyb, b'\r\x03\x03') # ctrl-C twice: interrupt any running program

def write_command(pyb, command):
    flush_input(pyb)
    pyb.serial.write(command)
    flush_input(pyb)

def flush_input(pyb):
    n = pyb.serial.inWaiting()
    while n > 0:
        pyb.serial.read(n)
        n = pyb.serial.inWaiting()

def soft_reset(args):
    pyb = get_pyb(args)
    print("trying to soft reboot badge")
    write_command(pyb, b'\x04') # ctrl-D: soft reset
    #print("1")
    data = pyb.read_until(1, b'soft reboot\r\n')
    #print("2")
    if data.endswith(b'soft reboot\r\n'):
        print("Soft reboot was successful.")
    else:
        raise PyboardError('could not soft reboot')

def find_tty():
    # Todo: find solution for windows, test in linux
    for pattern in ['/dev/ttyACM*', '/dev/tty.usbmodem*']:
        for path in glob.glob(pattern):
            return path
    print("Couldn't find badge tty - Please make it's plugged in and reset it if necessary")
    sys.exit(1)

def run(args):
    pyb = get_pyb(args)
    print("executing %s" % args.paths)
    print("----------------")
    # run any command or file(s) - this is mostly a copy from pyboard.py
    if args.command is not None or len(args.paths):
        # we must enter raw-REPL mode to execute commands
        # this will do a soft-reset of the board
        try:
            pyb.enter_raw_repl()
        except PyboardError as er:
            print(er)
            pyb.close()
            sys.exit(1)

        def execbuffer(buf):
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

        # run any files
        for filename in args.paths:
            with open(filename, 'rb') as f:
                pyfile = f.read()
                execbuffer(pyfile)

        # exiting raw-REPL just drops to friendly-REPL mode
        pyb.exit_raw_repl()
