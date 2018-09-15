import http
import ujson
from tilda import LED

API_URL = "https://huxley.apphb.com/all/{}?expand=true&accessToken=D102521A-06C6-44C9-8693-7A0394C757EF"

def get_trains(station_code='LBG'):
    print('trains/api: Getting trains for {}'.format(station_code))
    station_data = None

    LED(LED.RED).on()  # Red for total get_trains
    try:
        station_json = http.get(API_URL.format(
            station_code)).raise_for_status().content
        LED(LED.GREEN).on()  # Green for parsing
        station_data = ujson.loads(station_json)
    except Exception as e:
        print('Error:')
        print(e)

    LED(LED.RED).off()
    LED(LED.GREEN).off()
    return station_data
