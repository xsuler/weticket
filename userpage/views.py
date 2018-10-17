from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import User


class UserBind(APIView):
    def validate_user(self):
        pass

    def get(self):
        self.check_input('openid')
        openid=self.input['openid']
        if User.objects.filter(open_id=self.input['openid']).exists():
            return user.student_id
        else:
            user=User.objects.create(open_id=self.input['openid'],student_id="")
            user.save()

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()
