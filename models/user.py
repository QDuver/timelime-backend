import sys
import time
from firebase_admin import auth
from flask import jsonify
from models.exceptions import CustomException
from utils.constants import DEFAULT_QUOTAS
import config as c

class User:
    DEFAULT_USER_SETTINGS = {
        'uid': None,
        'isPremium': False,
        'isDarkMode': False,
        'isScaled': False,
        'lastLongPressHint': None,
        'quotas': DEFAULT_QUOTAS,
        'generating': {},
        'quizResults': [], 
        'joinedOn': None,
        'lastLogin': None,
        'displayName': None,
        'email': None,
        'photoUrl': None,
        'isAnonymous': False,
        'exp': None,
        'expiresIn': None,
        'lastPaymentFailed': None,
        'stripeCustomerId': None,
        'language': 'en'
    }


    def __init__(self, request=None, uid=None):
        self.uid = self.parse_token(request) if uid is None else uid
        user = c.db.get("users", where=('uid', '==', self.uid))[0]
        if not(user):
            user = self.create_new_user()
        self.set_(user)


    def set_(self, user):
        for key, default in self.DEFAULT_USER_SETTINGS.items():
                setattr(self, key, user.get(key, default))
        c.user = self
        self.update_user()
        
    def create_new_user(self):
        user = self.DEFAULT_USER_SETTINGS
        user['uid'] = self.uid
        user['isAnonymous'] = self.isAnonymous
        user['joinedOn'] = time.time()
        if not(self.isAnonymous):
            user['email'] = self.firebaseUser['email'] if 'email' in self.firebaseUser else None
            user['displayName'] = self.firebaseUser['displayName'] if 'displayName' in self.firebaseUser else None
            user['photoUrl'] = self.firebaseUser['photoUrl'] if 'photoUrl' in self.firebaseUser else None
        self.c.db.add("users", user, doc_id=user['uid'])            
        return user

    def parse_token(self, request):
        if('X-Allow-Unauthorized' in request.headers):
            uid = request.headers['X-Allow-Unauthorized']
            self.firebaseUser = {'uid': uid, 'isAnonymous': True}
            self.isAnonymous = True
            return uid
        token = request.headers.get("Authorization").split(" ")[1]
        firebaseResp = auth.verify_id_token(token)
        self.expiresIn = firebaseResp['exp'] - time.time()
        self.isAnonymous = False
        self.firebaseUser = auth.get_user(firebaseResp['uid']).__dict__['_data']
        return firebaseResp['uid']
        
    def to_dict(self):
        user_dict = {}
        for attr in list(self.DEFAULT_USER_SETTINGS.keys()):
            user_dict[attr] = getattr(self, attr)
        return user_dict

    def update_quotas_status(self, type):
        self.quotas[type] -= 1
        self.update_user()

    def update_user(self):
        c.db.edit("users", self.uid, self.to_dict())

    def is_quotas_exceeded(self, type_, event=None):
        if(self.isPremium):
            return False
        if(type_=='events'):
            n = len(c.db.get('events', where=('tid', '==', event['tid'])))
            quotas = DEFAULT_QUOTAS['events_free']
            error = 'backend.freeEventsQuotaReached'
        if(type_=='timelines'):
            n = len(c.db.get('timelines', where=('uid', '==', c.db.uid)))
            quotas = DEFAULT_QUOTAS['timelines_free']
            error = f'backend.freeTimelinesQuotaReached.{quotas}'
        if(n >= quotas):
            raise CustomException(error)
        return False
    
