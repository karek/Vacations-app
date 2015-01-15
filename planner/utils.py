from time import strptime, strftime
from datetime import date

class InternalError(Exception):
    def __init__(self, message):
        self.message = message
    def __unicode__(self):
        return repr(self.message)


def stringToDate(obj):
    """ changes string 'YYYY-MM-DD' to date object """
    try:
        timestruct = strptime(obj, '%Y-%m-%d')
        return date(*timestruct[:3])
    except ValueError as e:
        raise InternalError(e.message)


def dateToString(obj):
    """ changes date object to 'YYYY-MM-DD' string """
    return obj.strftime('%Y-%m-%d')
