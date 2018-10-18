from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import User
from wechat.models import Activity
from wechat.models import Ticket

import time


class UserBind(APIView):
    def validate_user(self):
        pass

    def get(self):
        self.check_input('openid')
        openid=self.input['openid']
        if User.objects.filter(open_id=self.input['openid']).exists():
            return User.objects.filter(open_id=self.input['openid']).student_id
        else:
            user=User.objects.create(open_id=self.input['openid'],student_id="")
            user.save()

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()


class ActivityDetail(APIView):
    def return_activity_to_dict(self, act):
        act_dict = {}
        act_dict['name'] = act.name
        act_dict['key'] = act.key
        act_dict['description'] = act.description
        act_dict['startTime'] = act.start_time.timestamp()
        act_dict['endTime'] = act.end_time.timestamp()
        act_dict['place'] = act.place
        act_dict['bookStart'] = act.book_start.timestamp()
        act_dict['bookEnd'] = act.book_end.timestamp()
        act_dict['totalTickets'] = act.total_tickets
        act_dict['picURL'] = act.pic_url
        act_dict['remainTickets'] = act.remain_tickets
        act_dict['currentTime'] = int(time.time())
        return act_dict


    def get(self, Activity):
        self.check_input('id')
        try:
            activity = Activity.objects.get(pk=self.input['id'])
        except Activity.DoesNotExist:
            raise NotExistError("get activity detail error: not exist")
        if activity.status == Activity.STATUS_DELETED:
            raise LogicError("get activity detail error: deleted")
        elif activity.status == Activity.STATUS_SAVED:
            raise LogicError("get activity detail error: saved")
        else:
            return self.return_activity_to_dict(activity)


class TicketDetail(APIView):
    def return_ticket_to_dict(self, tck):
        tck_dict = {}
        tck_dict['activityName'] = tck.activity.name
        tck_dict['place'] = tck.activity.place
        tck_dict['activityKey'] = tck.activity.key
        tck_dict['uniqueId'] = tck.unique_id
        tck_dict['startTime'] = tck.activity.start_time.timestamp()
        tck_dict['endTime'] = tck.activity.end_time.timestamp()
        tck_dict['currentTime'] = int(time.time())
        tck_dict['status'] = tck.status

    def get(self):
        self.check_input('openid', 'ticket')
        try:
            ticket = Ticket.objects.get(pk=self.input['ticket'])
        except Ticket.DoesNotExist:
            raise NotExistError("get ticket detail error: not exist")
        return self.return_ticket_to_dict(ticket)


