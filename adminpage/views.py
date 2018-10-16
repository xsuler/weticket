from codex.baseview import APIView
from codex.baseerror import InputError, LogicError, ValidateError, NotExistError

from wechat.models import Activity, Ticket

from django.db.models import Q
import time

class AdminLogin(APIView):
    def get(self):

        return 0

class ActivityList(APIView):

    # convert an Activity instance to a dict instance
    def activity_to_dict(self, activity):
        activity_dict = {}
        activity_dict['id'] = activity.id
        activity_dict['name'] = activity.name
        activity_dict['description'] = activity.description
        activity_dict['startTime'] = activity.start_time.timestamp()
        activity_dict['endTime'] = activity.end_time.timestamp()
        activity_dict['place'] = activity.place
        activity_dict['bookStart'] = activity.book_start.timestamp()
        activity_dict['bookEnd'] = activity.book_end.timestamp()
        activity_dict['currentTime'] = int(time.time())
        activity_dict['status'] = activity.status
        return activity_dict

    # return activity_list in which activity.status >= 0
    def get(self):
        total_activity_set = Activity.objects.exclude(status=Activity.STATUS_DELETED)
        activity_list = []
        for item in total_activity_set:
            activity_list.append(self.activity_to_dict(item))
        return activity_list

class ActivityDelete(APIView):

    def post(self):
        self.check_input('id')
        try:
            activity = Activity.objects.get(id=self.input['id'])
        except Activity.DoesNotExist:
            raise NotExistError("activity delete error: not exist")
        if activity.status == Activity.STATUS_DELETED:
            raise LogicError("activity delete error: already deleted")
        activity.status = Activity.STATUS_DELETED
        activity.save()



class ActivityDetail(APIView):

    # count used tickets
    def count_used_tickets(self, activity):
        used_tickets = Ticket.objects.filter(Q(activity=activity, status=Ticket.STATUS_USED))
        return len(used_tickets)

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
        activity_dict['bookedTickets'] = activity.total_tickets - activity.remain_tickets
        activity_dict['usedTickets'] = self.count_used_tickets(activity)
        activity_dict['currentTime'] = int(time.time())
        activity_dict['status'] = activity.status
        return activity_dict

    # change an activity detail
    def dict_to_exist_activity(self, activity):
        # 虽然前端已经考虑了这些条件 这里依然考虑条件限制
        if activity.status != Activity.STATUS_PUBLISHED:
            activity.name = self.input['name']                  # 已发布的活动不可修改
            activity.place = self.input['place']                # 已发布的活动不可修改
            activity.book_start = self.input['bookStart']       # 已发布的活动不可修改 时间戳
        else:
            activity.status = self.input['status']              # 已发布的活动只能修改为1（发布） 不能修改为0（暂存）

        activity.description = self.input['description']
        activity.pic_url = self.input['picUrl']

        if time.time() <= activity.end_time.timestamp():
            activity.start_time = self.input['startTime']       # 活动结束后不可修改 时间戳
            activity.end_time = self.input['endTime']           # 活动结束后不可修改 时间戳
            activity.book_end = self.input['bookEnd']           # 活动结束后不可修改 时间戳

        if time.time() <= activity.book_start.timestamp():
            activity.total_tickets = self.input['totalTickets'] # 抢票开始后不可修改

        activity.save()

    def get(self):
        self.check_input('id')
        try:
            activity = Activity.objects.get(id=self.input['id'])
        except Activity.DoesNotExist:
            raise NotExistError("activity detail error: not exist")
        if activity.status == Activity.STATUS_DELETED:
            raise LogicError("activity detail error: deleted")
        return self.activity_to_dict(activity)

    def post(self):
        self.check_input('id', 'name', 'place', 'description', 'picUrl', 'startTime', 'endTime',
                         'bookStart', 'bookEnd', 'totalTickets', 'status')
        try:
            activity = Activity.objects.get(id=self.input['id'])
        except Activity.DoesNotExist:
            raise NotExistError("activity detail change error: not exist")
        self.dict_to_exist_activity(activity)