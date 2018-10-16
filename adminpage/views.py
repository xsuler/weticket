from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import User
from django.contrib.auth import authenticate,login

class AdminLogin(APIView):
    def get(self):
        if self.request.user.is_authenticated:
            return 0;
        else:
            raise AdminNotLogin('admin not login in')

    def post(self):
        self.check_input('username', 'password')
        user = authenticate(username=self.input['username'], password=self.input['password'])
        if user is not None:
            login(self.request,user)
            return 0
        else:
            raise AdminAuthError('admin auth error')
