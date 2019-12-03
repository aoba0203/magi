import datetime


def get_today():
    return datetime.datetime.now().strftime('%Y.%m.%d')
