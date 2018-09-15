def is_red(service):
    return service['isCancelled'] or service['etd'] != 'On time'


def get_departure(service):
    if service['isCancelled']:
        return 'CANX'

    if service['etd'] == 'On time':
        return service['std']

    return service['etd']


def get_title(name, has_error):
    if has_error:
        return 'ERR ' + name

    return name
