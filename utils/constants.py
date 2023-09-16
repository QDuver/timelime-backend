import time


QUOTAS = {
    'search': 300,
    'quiz': 200,
    'aiTimelines': 200,
    'timelines': 5,
    'events': 30,
    'images': 50,
    'premium': 4.5
}


DEFAULT_USER_SETTINGS = {
    'isPremium': False,
    'isDarkMode': False,
    'isScaled': False,
    'lastLongPressHint': None,
    'quotas': QUOTAS,
    'generating': {},
    'quizResults': [],
    'joinedOn': time.time(),
    'lastLogin': time.time(),
    'displayName': None,
    'email': None,
    'photoUrl': None,
    'isAnonymous': False
}