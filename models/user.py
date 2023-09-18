import time
from flask import current_app as app, jsonify
from firebase_admin import auth

from models.exceptions import TokenExpired
from utils.constants import DEFAULT_QUOTAS
from utils.utils import first_day_of_next_month, print_full_exception

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
    }


    def __init__(self, request):

        self.db = app.config['db']
        self.request = request
        self.set_token()
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
        self.db.user = self
    
    def create_new_user(self):
        user = self.DEFAULT_USER_SETTINGS
        user['uid'] = self.uid
        user['isAnonymous'] = self.isAnonymous
        user['joinedOn'] = time.time()
        if not(self.isAnonymous):
            user['email'] = self.firebaseUser['email']
            user['displayName'] = self.firebaseUser['displayName']
            user['photoUrl'] = self.firebaseUser['photoUrl']
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
            return
        try:
            token = self.request.headers.get("Authorization").split(" ")[1]
            firebaseResp = auth.verify_id_token(token)
            self.exp = firebaseResp['exp']
            self.expiresIn = firebaseResp['exp'] - time.time()
            self.uid = firebaseResp['uid']
            self.db.uid = self.uid
            self.isAnonymous = False
            self.firebaseUser = auth.get_user(self.uid).__dict__['_data']
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
                user[attr] = self.DEFAULT_USER_SETTINGS[attr]
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
                if(self.generating[tracker]['loading'] and time.time() - self.generating[tracker]['started'] > 360):
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