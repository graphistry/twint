import datetime
import logging as logme
from .token import InvalidGuestTokenException


class SuspendedUser(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class user:
    type = "user"

    def __init__(self):
        pass


User_formats = {
    'join_date': '%Y-%m-%d',
    'join_time': '%H:%M:%S %Z'
}


# ur object must be a json from the endpoint https://api.twitter.com/graphql
def User(ur):
    logme.debug(__name__ + ':User')
    if 'data' not in ur or 'user' not in ur['data']:
        try:
            nfo = str(ur)
        except:
            nfo = '(failed to stringify user)'
        msg = 'malformed json! cannot be parsed to get user data for payload: ' + nfo
        if 'Bad guest token' in nfo:
            raise InvalidGuestTokenException('User data request failed: bad guest token - ' + nfo)
        logme.fatal(msg)
        raise KeyError(msg)
    if 'legacy' not in ur['data']['user']:
        try:
            nfo = str(ur)
        except:
            nfo = '(failed to stringify user)'
        if 'User has been suspended' in nfo:
            raise SuspendedUser('User has been suspended')
        logme.fatal('malformed json! legacy not in user payload: ' + str(ur))
        raise KeyError('malformed json! legacy not in user payload: ' + str(ur))
    _usr = user()
    _usr.id = ur['data']['user']['rest_id']
    _usr.name = ur['data']['user']['legacy']['name']
    _usr.username = ur['data']['user']['legacy']['screen_name']
    _usr.bio = ur['data']['user']['legacy']['description']
    _usr.location = ur['data']['user']['legacy']['location']
    _usr.url = ""
    if 'url' in ur['data']['user']['legacy']:
        _usr.url = ur['data']['user']['legacy']['url']
    # parsing date to user-friendly format
    _dt = ur['data']['user']['legacy']['created_at']
    _dt = datetime.datetime.strptime(_dt, '%a %b %d %H:%M:%S %z %Y')
    # date is of the format year,
    _usr.join_date = _dt.strftime(User_formats['join_date'])
    _usr.join_time = _dt.strftime(User_formats['join_time'])

    # :type `int`
    _usr.tweets = int(ur['data']['user']['legacy']['statuses_count'])
    _usr.following = int(ur['data']['user']['legacy']['friends_count'])
    _usr.followers = int(ur['data']['user']['legacy']['followers_count'])
    _usr.likes = int(ur['data']['user']['legacy']['favourites_count'])
    _usr.media_count = int(ur['data']['user']['legacy']['media_count'])

    _usr.is_private = ur['data']['user']['legacy']['protected']
    _usr.is_verified = ur['data']['user']['legacy']['verified']
    _usr.avatar = ur['data']['user']['legacy']['profile_image_url_https']
    _usr.background_image = ""
    if 'profile_banner_url' in ur['data']['user']['legacy']:
        _usr.background_image = ur['data']['user']['legacy']['profile_banner_url']
    # TODO : future implementation
    # legacy_extended_profile is also available in some cases which can be used to get DOB of user
    return _usr
