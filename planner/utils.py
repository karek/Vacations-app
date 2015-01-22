from datetime import date
import json
from time import strptime, strftime

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


def objListToJson(objs):
    obj_list = map(lambda o: o.toDict(), objs)
    return json.dumps(obj_list)
