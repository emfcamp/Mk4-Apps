#!/usr/bin/env python3

"""Toolchain for working with the TiLDA Mk4

Usage
------------------------------------

Reboot badge
$ tilda_tools reset

Soft reboot badge and start specific app
$ tilda_tools reset --boot my_app

Update files in folder(s) to match current local version
$ tilda_tools sync my_game shared
$ tilda_tools sync <pattern1> <pattern2> ...

Sync (as above), but execute my_app after reboot
$ tilda_tools sync --boot my_app [<other sync parameter>]

Sync (as above), but execute a single file afterwards without copying it to the badge
$ tilda_tools sync --run some_other_file.py

Sync a given app and execute it
$ tilda_tools app home_default

Executes a single file on the badge without copying anything (Using pyboard.py)
$ tilda_tools run my_app/main.py

Runs local validation (doesn't require a badge, but doesn't run unit tests)
$ tilda_tools validate

Runs local validation and badge-side tests
$ tilda_tools test

Update firmware on badge (warning, this will delete all settings etc. stored on the badge!)
$ tilda_tools firmware-update

Setup wifi.json to be copied to the badge on every sync
$ tilda_tools wifi

Common parameters
-----------------

-d --device  : serial interface (default: auto)
-s --storage : path to flash storage

"""

import glob
import sync, firmware_update, wifi, pyboard_util, sys
from resources import *

def main():
    import argparse
    cmd_parser = argparse.ArgumentParser(description='Toolchain for working with the TiLDA Mk4')
    cmd_parser.add_argument('command', nargs=1, help='command [test|reset|sync|run|validate|wifi|firmware-update|app|bootstrap]', choices=['test', 'reset', 'sync', 'validate', 'run', 'wifi', 'firmware-update', 'app', 'bootstrap'])
    cmd_parser.add_argument('-c', '--clean', action='store_true', help='clean mass storage before writing')
    cmd_parser.add_argument('-d', '--device', help='the serial device of the badge')
    cmd_parser.add_argument('-s', '--storage', help='the usb mass storage path of the badge')
    cmd_parser.add_argument('-b', '--baudrate', default=115200, help='the baud rate of the serial device')
    cmd_parser.add_argument('-v', '--verbose', action='store_true', help='adds more output')
    cmd_parser.add_argument('--skip-wifi', action='store_true', help='does not sync wifi.json')
    cmd_parser.add_argument('--bootstrapped-apps', action='store_true', help='[Sync] only bootstrapped apps by default')
    cmd_parser.add_argument('--print_resources', action='store_true', help='prints resources in json')
    cmd_parser.add_argument('--boot', help='defines which app to boot into after reboot')
    cmd_parser.add_argument('--run', help='like run, but after a sync')
    cmd_parser.add_argument('-w', '--wait', default=0, type=int, help='seconds to wait for USB connected board to become available')
    cmd_parser.add_argument('paths', nargs='*', help='input files')
    args = cmd_parser.parse_args()
    command = args.command[0]
    path = sync.get_root()
    run_tests = command == "test"

    if command not in ["validate"]:
        try:
            import serial
        except Exception as e:
            print("Please install pyserial first: https://pyserial.readthedocs.io/en/latest/pyserial.html")
            sys.exit(1)

    if command == "firmware-update":
        firmware_update.firmware_update(args.verbose)

    if command == "wifi":
        wifi.select_wifi()

    if command == "app":
        command = "sync"
        args.run = "%s/main.py" % args.paths[0]
        #args.boot = args.paths[0]

    if command in ["test", "validate", "sync", "bootstrap"]:
        resources = get_resources(path)
        add_metadata(path, resources)
        validate(path, resources)
        resolve_dependencies(resources)
        remove_upip(resources)
        if args.print_resources:
            print(pretty_print_resources(resources))
        errors = get_error_summary(resources)
        if errors:
            print("Problems found:\n")
            print(errors)
            sys.exit(1)
        print("Local Test: PASS")
        if command == "test":
            command = "sync"
            if len(args.paths) == 0:
                print("Please define an app or lib to sync: tilda_tools sync my_app\n")
                sys.exit(1)
            else:
                args.paths = ["lib/test_%s.py" % p for p in args.paths]

    if command in ["reset", "sync", "bootstrap"]:
        pyboard_util.stop_badge(args, args.verbose)

    if command == "bootstrap":
        sync.clean(args)
        sync.sync(args, ["bootstrap.py"], {}, args.verbose, args.skip_wifi)
        pyboard_util.hard_reset(args)

    if command == "sync":
        paths = args.paths if len(args.paths) else None
        if args.bootstrapped_apps:
            for k,val in list(resources.items()):
                requested = paths and k in paths
                bootstrapped = val.get("bootstrapped", False)
                if val.get("type", None) == "app":
                    if not (bootstrapped or (paths and requested)):
                        # App is not in the bootstrap list, and isn't explicitly requested
                        if args.verbose:
                            print("Removing app '{0}' from sync list".format(k))
                        del resources[k]

        if args.clean:
            sync.clean(args)
        synced_resources = sync.sync(args, paths, resources, args.verbose, args.skip_wifi)

    if (command in ["reset", "sync"]) or run_tests:
        sync.set_boot_app(args, args.boot or "")
        if args.run:
            command = "run"
            args.paths = [args.run]
            sync.set_no_boot(args)
        pyboard_util.soft_reset(args)


    if command == "run":
        pyboard_util.check_run(args.paths)
        pyboard_util.run(args, args.paths)

    if run_tests:
        for resource in synced_resources:
            pyboard_util.check_run([resource])
            pyboard_util.run(args, [resource], False)
            pyboard_util.soft_reset(args, False)

    pyboard_util.close_pyb()


if __name__ == "__main__":
    main()

