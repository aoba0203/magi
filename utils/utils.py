import datetime


def get_today():
    return datetime.datetime.now().strftime('%Y.%m.%d')


def get_time():
    return datetime.datetime.now().strftime('%H%M')
