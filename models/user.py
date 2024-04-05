import sys
import time
from firebase_admin import auth
from flask import jsonify
from utils.constants import DEFAULT_QUOTAS
from utils.utils import first_day_of_next_month
from firestore.firestore_db import FirestoreDB
import config
user = None
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
        'nextQuotaRefresh': None,
        'lastPaymentFailed': None,
        'stripeCustomerId': None,
        'language': 'en'
    }


    def __init__(self, request=None, uid=None):
        global user
        self.uid = self.set_token(request) if(request) else uid
        self.populate_user_data()
        user = self

    def get_user(self):
        global user
        return user


    def populate_user_data(self):
        user = config.db.get("users", where=('uid', '==', self.uid))[0]
        user = self.fill_in_missing_attributes(user) if user else self.create_new_user()

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
        self.nextQuotaRefresh = first_day_of_next_month()
        self.lastPaymentFailed = user.get('lastPaymentFailed ', None)
        self.stripeCustomerId = user.get('stripeCustomerId', None)
        self.language = user.get('language', 'en')
    
    def create_new_user(self):
        user = self.DEFAULT_USER_SETTINGS
        user['uid'] = self.uid
        user['isAnonymous'] = self.isAnonymous
        user['joinedOn'] = time.time()
        if not(self.isAnonymous):
            user['email'] = self.firebaseUser['email'] if 'email' in self.firebaseUser else None
            user['displayName'] = self.firebaseUser['displayName'] if 'displayName' in self.firebaseUser else None
            user['photoUrl'] = self.firebaseUser['photoUrl'] if 'photoUrl' in self.firebaseUser else None
        self.db.add("users", user, doc_id=user['uid'])            
        return user

    def set_token(self, request):
        if('X-Allow-Unauthorized' in request.headers):
            uid = request.headers['X-Allow-Unauthorized']
            self.firebaseUser = {'uid': uid, 'isAnonymous': True}
            self.isAnonymous = True
            return uid
        token = request.headers.get("Authorization").split(" ")[1]
        firebaseResp = auth.verify_id_token(token)
        self.exp = firebaseResp['exp']
        self.expiresIn = firebaseResp['exp'] - time.time()
        self.isAnonymous = False
        self.firebaseUser = auth.get_user(self.uid).__dict__['_data']
        return firebaseResp['uid']
        
    def to_dict(self):
        user_dict = {}
        for attr in list(self.DEFAULT_USER_SETTINGS.keys()):
            try:
                user_dict[attr] = getattr(self, attr)
            except:
                pass
        return user_dict
    
    def fill_in_missing_attributes(self, user):
        changed = False
        for attr in list(self.DEFAULT_USER_SETTINGS.keys()):
            if(attr not in user):
                changed = True
                user[attr] = self.DEFAULT_USER_SETTINGS[attr]
        if(changed):
            self.db.edit("users", user['uid'], user)
        return user
    
    def update_ai_tracking_status(self, type_, loading, generated=None):
        self.generating[type_] = {
            'loading': loading,
            'started': time.time() if loading else None,
            'generated': generated
        }

        self.update_user()

    def update_quotas_status(self, type):
        self.quotas[type] -= 1
        self.update_user()

    def update_user(self):
        self.db.edit("users", self.uid, self.to_dict())

    def update_premium_status(self, isPremium):
        self.isPremium = isPremium
        self.update_user()

    def abort_if_already_ai_generating(self):
        try:
            if(self.generating['quiz']['loading'] or self.generating['timeline']['loading']):
                return jsonify({"message": "loadingTracker.quizOrTimelineAlreadyGenerating"}), 400
        except KeyError:
            pass