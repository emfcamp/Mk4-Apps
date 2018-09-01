"""View images from the EMF 2018 time-lapse camera
"""
___name___         = "Lobster Vision"
___license___      = "MIT"
___dependencies___ = ["app", "dialogs", "wifi", "buttons", "http", "ugfx_helper"]
___categories___   = ["Other"]

import ugfx, wifi, dialogs, utime, ugfx_helper, buttons
import gc
from http import *
from tilda import Buttons

IMAGE_PROXY     = 'http://imageproxy.lobsterdev.com/api/'
ACCESS_KEY      = 'ZW1mMjAxODplbWYyMDE4'
FULL_MONTHS     = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November',
                   'December']
DAYS            = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                   'Saturday', 'Sunday']

PHOTO_FILE      = 'lobstervision/photo.gif'
projects = []
selectedProject = 0
selectedCamera = 0
selectedDate = None
selectedTime = None
imageList = []
imageIndexWithinDate = None
filename = None

def loading_screen():
    logo = 'lobstervision/lobsterpictures.gif'
    ugfx.area(0,0,ugfx.width(),ugfx.height(),0xFFFF)
    ugfx.display_image(0,50,logo)
    ugfx.set_default_font(ugfx.FONT_SMALL)
    ugfx.text(15, 305, "lobstervision.tv/emf2018", ugfx.GREY)
    display_loading()

def display_error(message):
    dialogs.notice(message, title='Error')

def display_loading():
    ugfx.area(0,215,320,25,0xFFFF)
    ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
    ugfx.text(90,220, "Loading...", ugfx.GREY)

def display_datetime():
    ugfx.area(0,215,320,25,0xFFFF)
    ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
    (date, day) = format_selected_date()
    time = format_selected_time()
    ugfx.text(5,220, time, ugfx.RED)
    ugfx.text(60,220, "%s, %s" % (day, date), ugfx.GREY)

def display_image():
    gc.collect()
    global selectedProject, selectedCamera, filename
    display_loading()
    endpoint = 'images/project/%d/camera/%d/%s' % \
            (selectedProject, selectedCamera, filename)
    try:
        headers = {'Authorization': 'Basic '+ACCESS_KEY}
        url = IMAGE_PROXY+endpoint
        get(url, headers = headers).raise_for_status().download_to(PHOTO_FILE)
    except OSError as e:
        display_error('Unable to download image %s' % e)
        return
    utime.sleep_ms(200)
    ugfx.display_image(0,0,PHOTO_FILE)
    display_datetime()

def format_selected_date():
    date = None
    day = None
    global selectedDate
    (year, month, day, hour, minute, second, dayofweek,
     dayinyear) = utime.localtime(selectedDate - 946684800)
    date = '%d %s %d' % (day, FULL_MONTHS[month-1], year)
    day = DAYS[dayofweek]
    return (date, day)

def format_selected_time():
    global selectedTime
    time = str(selectedTime)
    return '%s:%s' % (time[:2], time[2:4])

def list_cameras():
    global selectedProject
    cameraCount = len(projects[selectedProject]['camera'])
    cameras = []
    for i in range(0, cameraCount):
        cameras.append({'index': i, 'title': 'Camera %d' % (i + 1)})
    return cameras

def get_from_api(path):
    headers = {'Authorization': 'Basic '+ACCESS_KEY}
    url = IMAGE_PROXY+path
    with get(url, headers = headers) as response:
        return response.json()

def load_account_details():
    gc.collect()
    rsp = get_from_api('account')
    global projects
    if not 'result' in rsp:
        raise OSError('Could not load account data')
    if 'client' in rsp['result']:
        projects = rsp['result']['client']['project']

def load_camera_dates():
    gc.collect()
    for p, project in enumerate(projects):
        for c, camera in enumerate(project['camera']):
            endpoint = 'dates/project/%d/camera/%d' % (p, c)
            try:
                rsp = get_from_api(endpoint)
            except OSError:
                continue
            if not 'result' in rsp:
                continue
            camera['start'] = rsp['result']['start']
            camera['finish'] = rsp['result']['finish']
            camera['missing'] = rsp['result']['disabled']

def load_image_list():
    gc.collect()
    global selectedProject, selectedCamera, selectedDate, selectedTime, imageList
    if not selectedDate:
        # Bodge as EMF camera seems to have stalled uploading due to lack of
        # signal
        if projects[selectedProject]['camera'][selectedCamera]['finish'] == 1535673600:
           selectedDate = 1535587200
           selectedTime = "150000"   
        else:
           selectedDate = projects[selectedProject]['camera']\
                            [selectedCamera]['finish']
    endpoint = 'dates/project/%d/camera/%d/%s' % \
                (selectedProject, selectedCamera, selectedDate)
    try:
        rsp = get_from_api(endpoint)
    except OSError:
        return
    if not 'result' in rsp:
        return
    imageList = rsp['result']
    select_from_image_list()

def select_from_image_list():
    global imageList, selectedTime, imageIndexWithinDate, filename
    selectedImage = None
    firstImage = imageList[0]
    lastImage = imageList[-1]
    if not selectedTime or selectedTime >= lastImage['time']:
        selectedImage =  lastImage
        imageIndexWithinDate = len(imageList) - 1
    elif selectedTime <= firstImage['time']:
        selectedImage = firstImage
        imageIndexWithinDate = 0
    else:
        previousDiff = 0
        for position, image in enumerate(imageList):
            diff = abs(int(image['time']) - int(selectedTime))
            if selectedTime < image['time']:
                if diff < previousDiff:
                    selectedImage = image
                    imageIndexWithinDate = position
                else:
                    selectedImage = imageList[position - 1]
                    imageIndexWithinDate= position - 1
                break
            previousDiff = diff
        if not selectedImage:
            selectedImage = lastImage
            imageIndexWithinDate = len(imageList) - 1
    selectedTime = selectedImage['time']
    filename = selectedImage['image']
    display_image()

def select_camera(camera):
    global selectedCamera, selectedDate, selectedTime
    selectedCamera = int(camera)
    selectedDate = None
    selectedTime = None
    load_image_list()

def select_date(date):
    global selectedDate
    selectedDate = int(date)
    load_image_list()

def previous_date():
    global selectedProject, selectedCamera, selectedDate
    camera = \
        projects[selectedProject]['camera'][selectedCamera]
    date = selectedDate - 86400 # 24 hours
    # Check not trying to go back before the camera's first day
    if date < camera['start']:
        return
    # Skip over any missing dates
    while date in camera['missing']:
        camera -= 86400
    print("Setting date to %s" % date)
    selectedDate = date
    load_image_list()

def next_date():
    global selectedProject, selectedCamera, selectedDate
    camera = \
        projects[selectedProject]['camera'][selectedCamera]
    date = selectedDate + 86400 # 24 hours
    # Check not trying to go back past the camera's last day
    if date > camera['finish']:
        return
    # Skip over any missing dates
    while date in camera['missing']:
        camera += 86400
    selectedDate = date
    load_image_list()

def previous_image():
    global selectedProject, selectedCamera, selectedDate, selectedTime
    global imageList, imageIndexWithinDate,  filename
    # If first image of current day, jump to last image of previous day
    if imageIndexWithinDate == 0:
        camera = \
            projects[selectedProject]['camera'][selectedCamera]
        if selectedDate != camera['start']:
            selectedTime = None
            previous_date()
        return
    imageIndexWithinDate -= 1
    image = imageList[imageIndexWithinDate]
    filename = image['image']
    selectedTime = image['time']
    display_image()

def next_image():
    global selectedProject, selectedCamera, selectedDate, selectedTime
    global imageList, imageIndexWithinDate, filename
    # If first image of current day, jump to first image of next day
    if imageIndexWithinDate == len(imageList)-1:
        camera = \
            projects[selectedProject]['camera'][selectedCamera]
        if selectedDate != camera['finish']:
            selectedTime = '000000'
            next_date()
        return
    imageIndexWithinDate += 1
    image = imageList[imageIndexWithinDate]
    filename = image['image']
    selectedTime = image['time']
    display_image()


def start():
    ugfx_helper.init()
    loading_screen()
    if not wifi.is_connected():
        try:
            wifi.connect()
        except OSError:
            display_error("Unable to connect to Wifi")
            return False
    try:
        load_account_details()
    except OSError as e:
        display_error("Unable to contact the server. Please try again later")
        return False
    if len(projects) == 0:
        display_error("Sorry, no projects are available to display")
        return False
    load_camera_dates()
    load_image_list()
    return True

running = start()
while running:
    if buttons.is_triggered(Buttons.JOY_Right):
        next_image()
    elif buttons.is_triggered(buttons.Buttons.JOY_Left):
        previous_image()
    elif buttons.is_triggered(Buttons.JOY_Up):
        previous_date()
    elif buttons.is_triggered(Buttons.JOY_Down):
        next_date()
    utime.sleep_ms(30)
