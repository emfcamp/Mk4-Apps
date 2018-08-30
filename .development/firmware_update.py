import urllib.request, tempfile, os, shutil, subprocess

def firmware_update(verbose):
    global __verbose
    __verbose = verbose

    temp_path = tempfile.mktemp("firmware.dfu")
    url = "https://s3.amazonaws.com/tilda-badge/mk4/firmware.dfu"
    device = "1cbe:00ff"

    print("Hello - Welcome to the automated TiLDA Mk4 firmware updater")
    try:
        response = subprocess.run(["dfu-util", "--list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if response.returncode != 0:
            print(response)
            return

        if ("Found DFU: [%s]" % device) not in response.stdout.decode('utf-8'):
            print(response.stdout.decode('utf-8'))
            print("We couldn't find a DFU enabled badge. Please check the following:")
            print("")
            print("1) Your badge is plugged into this computer via USB")
            print("2) The switch underneath the screen at the back of the badge is set to 'on'")
            print("3) Your badge is in DFU mode. You can tell by a small, red flashing light at the back")
            print("")
            print("To put your badge into DFU mode (or if you're unsure whether it really is) you need to")
            print("press the joystick to the right while pressing the reset button at the back.")
            print("")
            print("After that, please try this script again.")
            return

        print("Downloading newest firmware: ", end="", flush=True)
        with urllib.request.urlopen(url) as response:
            with open(temp_path, 'wb') as tmp_file:
                shutil.copyfileobj(response, tmp_file)
        print("DONE")

        response = subprocess.run(["dfu-util", "--download", temp_path])
        if response.returncode != 0:
            print("Something went wrong during DFU updload :(")
            print("")
            print(response)
            return

        print("")
        print("You can now restart your badge by pressing the reset button on the back. Please follow the instructions on the screen to finish the setup")
        print("Have a nice day!")

    except FileNotFoundError as e:
        if "No such file or directory: 'dfu-utils'" in str(e):
            print("We couldn't find dfu-util. You might have to install it.")
            print("You can find instructions here: http://dfu-util.sourceforge.net/")
            print("Please try again after you've installed dfu-util.")
        else:
            raise e

    finally:
        if os.path.isfile(temp_path): os.remove(temp_path)
