import time
from flask import current_app as app, jsonify
from firebase_admin import auth

from models.exceptions import TokenExpired
from utils.constants import QUOTAS

class User:
    DEFAULT_USER_SETTINGS = {
        'uid': None,
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
    firebaseUser = None

    def __init__(self, request):

        self.db = app.config['db']
        self.request = request
        self.set_token()

    def populate_user_data(self):
        try:
            user = self.db.get("users", where=('uid', '==', self.firebaseId))[0]
            user = self.fill_in_missing_attributes(user)
        except:
            user = self.create_new_user()

        self.name = user.get('displayName', None)
        self.email = user.get('email', None)
        self.photoUrl = user.get('photoUrl', None)
        self.isPremium = user.get('isPremium', False)
        self.joinedOn = user.get('joinedOn', None)
        self.lastLogin = user.get('lastLogin', time.time())
        self.quotas = user.get('quotas', {})
        self.generating = user.get('generating', {})
        self.quizResults = user.get('quizResults', {})
        self.isDarkMode = user.get('isDarkMode', False)
        self.isScaled = user.get('isScaled', False)
        self.lastLongPressHint = user.get('lastLongPressHint', None)
        self.isPremium = user.get('isPremium', False)
        app.config['user'] = self

    # remove_loading_if_too_long(user)
    
    def create_new_user(self):
        user = self.DEFAULT_USER_SETTINGS
        user['uid'] = self.uid
        user['isAnonymous'] = self.isAnonymous
        if not(self.isAnonymous):
            user['email'] = self.firebaseUser['email']
            user['displayName'] = self.firebaseUser['displayName']
            user['photoUrl'] = self.firebaseUser['photoUrl']
            self.db.add("users", user, doc_id=user['uid'])
        self.db.add("users", user, doc_id=user['uid'])            
        return user

    def set_token(self):
        print('set_token', flush=True)
        if('X-Allow-Unauthorized' in self.request.headers):
            tempId = self.request.headers['X-Allow-Unauthorized']
            self.firebaseUser = {'uid': tempId, 'isAnonymous': True}
            self.uid = tempId
            self.db.uid = self.uid
            self.isAnonymous = True
            self.populate_user_data()
            return
        try:
            token = self.request.headers.get("Authorization").split(" ")[1]
            self.firebaseId = auth.verify_id_token(token)['uid']
            self.uid = self.firebaseId
            self.db.uid = self.uid
            self.isAnonymous = True
            self.firebaseUser = auth.get_user(self.firebaseId).__dict__['_data']
            self.populate_user_data()
        except Exception as e:
            if('Token expired' in str(e)):
                raise TokenExpired('Token expired')
            else:
                raise e
            
    def to_dict(self):
        user_dict = {}
        for attr in list(self.DEFAULT_USER_SETTINGS.keys()):
            try:
                user_dict[attr] = getattr(self, attr)
            except:
                pass
        return user_dict
    
    def fill_in_missing_attributes(self, user):
        for attr in list(self.DEFAULT_USER_SETTINGS.keys()):
            if(attr not in user):
                user[attr] = getattr(self, attr)
        self.db.edit("users", user['uid'], user)
        return user

    # def is_anonymous_user(self):
    #     return len(self.user['uid']) < 12

# def remove_loading_if_too_long(user):
#     trackers = ['image', 'quiz', 'timeline']
#     for tracker in trackers:
#         try:
#             if(user['generating'][tracker]['loading'] and time.time() - user['generating'][tracker]['started'] > 360):
#                 user['generating'][tracker]['loading'] = False
#                 user['generating'][tracker]['started'] = None
#                 user['generating'][tracker]['generated'] = None
#                 app.config['db'].edit('users', user['uid'], user)
#         except:
#             pass