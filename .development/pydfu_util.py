from pydfu import *
import urllib.request, tempfile, os, shutil, ssl

def firmware_update(verbose):
    global __verbose
    __verbose = verbose

    temp_path = tempfile.mktemp("firmware.dfu")
    url = "https://update.badge.emfcamp.org/firmware.dfu"

    print("Hello - Welcome to the automated TiLDA Mk4 firmware updater")
    print("Finding badge: ", end="")
    try:
        init()
        print("DONE")

        print("Downloading newest firmware: ", end="")
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(url, context=context) as response:
            with open(temp_path, 'wb') as tmp_file:
                shutil.copyfileobj(response, tmp_file)
        print("DONE")

        elements = read_dfu_file(temp_path)
        if not elements:
            return

        print("Resetting Badge: ", end="")
        mass_erase()
        print("DONE")

        print("Updating...")
        write_elements(elements, True, progress=cli_progress)
        exit_dfu()

        print("")
        print("You can now restart your badge by pressing the reset button on the back. Please follow the instructions on the screen to finish the setup")
        print("Have a nice day!")

    except ValueError as e:
        print("FAIL")
        print("")
        print("We couldn't find your badge. You need to make sure it's plugged in and in DFU mode.")
        print("To put your badge into DFU mode you need to press the joystick in the middle while pressing the reset button at the back.")
        print("After that, please try this script again.")
        print()
        print("Error: %s" %(e))
    finally:
        if os.path.isfile(temp_path): os.remove(temp_path)
