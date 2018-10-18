from codex.baseerror import *
import datetime, time
from codex.baseview import APIView
from wechat.models import Activity, Ticket
from wechat.models import User


class UserBind(APIView):
    def validate_user(self):
        pass

    def get(self):
        self.check_input('openid')
        openid=self.input['openid']
        if User.objects.filter(open_id=self.input['openid']).exists():
            return User.objects.get(open_id=self.input['openid']).student_id
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
    # convert an Activity instance to a dict instance
    def activity_to_dict(self, activity):
        activity_dict = {}
        activity_dict['name'] = activity.name
        activity_dict['key'] = activity.key
        activity_dict['description'] = activity.description
        activity_dict['startTime'] = activity.start_time.timestamp()
        activity_dict['endTime'] = activity.end_time.timestamp()
        activity_dict['place'] = activity.place
        activity_dict['bookStart'] = activity.book_start.timestamp()
        activity_dict['bookEnd'] = activity.book_end.timestamp()
        activity_dict['totalTickets'] = activity.total_tickets
        activity_dict['picUrl'] = activity.pic_url
        activity_dict['remainTickets'] = activity.remain_tickets
        activity_dict['currentTime'] = int(time.time())
        return activity_dict

    def get(self):
        self.check_input('id')
        activity = Activity.objects.get(pk=self.input['id'])
        if activity.status==Activity.STATUS_PUBLISHED:
            return self.activity_to_dict(activity)
        raise NotExistError('activity not exist or not published')


class TicketDetail(APIView):
    def ticket_to_dict(self, ticket):
        ticket_dict = {}
        activity=ticket.activity
        ticket_dict['activityName'] = activity.name
        ticket_dict['place'] = activity.place
        ticket_dict['activityKey'] = activity.key
        ticket_dict['uniqueId'] =ticket.unique_id
        ticket_dict['startTime'] =activity.start_time.timestamp()
        ticket_dict['endTime'] =activity.end_time.timestamp()
        ticket_dict['currentTime'] = int(time.time())
        ticket_dict['status'] =ticket.status
        return ticket_dict

    def get(self):
        self.check_input('openid','ticket')
        if not Ticket.objects.filter(unique_id=self.input['ticket']).exists():
            raise NotExistError('ticket not exist')
        ticket =Ticket.objects.get(unique_id=self.input['ticket'])
        user=User.objects.get(open_id=self.input['openid'])
        if user.student_id!=ticket.student_id:
            raise LookupError('error match of studnet_id')
        return self.ticket_to_dict(ticket)
