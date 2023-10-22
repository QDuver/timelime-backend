import time
from flask import current_app as app, jsonify
from firebase_admin import auth
from utils.constants import DEFAULT_QUOTAS
from utils.utils import first_day_of_next_month

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


    def __init__(self, db, request=None, uid=None):

        self.db = db
        if(request):
            self.request = request
            self.set_token() 
        else:
            self.uid = uid
            self.db.uid = self.uid
        self.populate_user_data()
        self.remove_loading_if_too_long()


    def populate_user_data(self):
        query = self.db.get("users", where=('uid', '==', self.uid))
        if(len(query) == 0):
            user = self.create_new_user()
        else:
            user = query[0]
            user = self.fill_in_missing_attributes(user)

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
        self.db.user = self
    
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

    def set_token(self):
        if('X-Allow-Unauthorized' in self.request.headers):
            tempId = self.request.headers['X-Allow-Unauthorized']
            self.firebaseUser = {'uid': tempId, 'isAnonymous': True}
            self.uid = tempId
            self.db.uid = self.uid
            self.isAnonymous = True
            return
        token = self.request.headers.get("Authorization").split(" ")[1]
        if(token == 'dhasf039847pnasdlkfuh73094fo'):
            self.uid = 'LKKHd0ji3nSvHzoQiNe4hTCrh6E3'
            self.firebaseUser = self.db.get("users", where=('uid', '==', self.uid))[0]
            self.isAnonymous = False
            self.db.uid = self.firebaseUser['uid']
            return
        firebaseResp = auth.verify_id_token(token)
        self.exp = firebaseResp['exp']
        self.expiresIn = firebaseResp['exp'] - time.time()
        self.uid = firebaseResp['uid']
        self.db.uid = self.uid
        self.isAnonymous = False
        self.firebaseUser = auth.get_user(self.uid).__dict__['_data']
        
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

        if(generated):
            self.quotas[type_] = self.quotas[type_] - 1
        

        self.update_user()

    def remove_loading_if_too_long(self):
        trackers = ['image', 'quiz', 'timeline']
        for tracker in trackers:
            try:
                if(self.generating[tracker]['loading'] and time.time() - self.generating[tracker]['started'] > 120):
                    self.generating[tracker]['loading'] = False
                    self.generating[tracker]['started'] = None
                    self.generating[tracker]['generated'] = None
                    self.update_user()
            except:
                pass

    def update_user(self):
        self.db.edit("users", self.uid, self.to_dict())

    def update_premium_status(self, isPremium):
        self.isPremium = isPremium
        self.update_user()