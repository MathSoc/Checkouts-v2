import datetime
import pytz
from tzlocal import get_localzone

EPOCH_YEAR = 1970
EPOCH_MONTH = 1
EPOCH_DAY = 1

def unix_time(dt):
    """
    Converts a datetime object to the seconds since epoch.  Converts to
    UTC as a preventative measure.
    """
    dt = dt.astimezone(pytz.utc)
    epoch = datetime.datetime(EPOCH_YEAR, EPOCH_MONTH, EPOCH_DAY,
                              tzinfo=pytz.utc)
    return int((dt - epoch).total_seconds())

def current_time():
    """
    Returns the current number of seconds since epoch.
    """
    dt = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    return unix_time(dt)

def timestamp_to_iso(timestamp):
    """
    Converts a timestamp representating seconds since epoch in UTC to an
    equivalent datetime object.
    """
    utc = pytz.utc
    datetime_utc = datetime.datetime.utcfromtimestamp(int(timestamp))
    datetime_utc = datetime_utc.replace(tzinfo=utc)
    return datetime_utc

def timestamp_to_local(timestamp):
    """
    Converts a timestamp representing seconds since epoch in UTC to an
    equivalent datetime object in the local time.
    """
    utc = pytz.utc
    datetime_utc = datetime.datetime.utcfromtimestamp(int(timestamp))
    datetime_utc = datetime_utc.replace(tzinfo=utc)
    return datetime_utc.astimezone(get_localzone())

def register_api_resource(api, version, resource, *paths):
    """
    Registers a list of endpoints on the API for the given resource.
    """
    _paths = []
    for path in paths:
        frags = ['api', version, path]
        _paths.append('/%s' % '/'.join(map(lambda x: x.strip('/'), frags)))
    api.add_resource(resource, *_paths)
