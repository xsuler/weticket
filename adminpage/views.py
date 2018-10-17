from codex.baseview import APIView
from codex.baseerror import *
from wechat.models import User
from adminpage.models import *
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, login, logout
from wechat.models import Activity, Ticket
from wechat.views import CustomWeChatView
from wechat.wrapper import WeChatLib
from WeChatTicket.settings import WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET

from django.db.models import Q
import datetime, time


class AdminLoginOut(APIView):
    def post(self):
        if self.request.user.is_authenticated():
            logout(self.request)
        else:
            raise AdminNotLogin('admin not login in')


class AdminLoginIn(APIView):
    def get(self):
        if self.request.user.is_authenticated():
            return 0
        else:
            raise AdminNotLogin('admin not login in')

    def post(self):
        self.check_input('username', 'password')
        user = authenticate(
            username=self.input['username'], password=self.input['password'])
        if user is not None:
            login(self.request, user)
            return 0
        else:
            raise AdminAuthError('admin auth error')


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
        total_activity_set = Activity.objects.exclude(
            status=Activity.STATUS_DELETED)
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
        used_tickets = Ticket.objects.filter(
            Q(activity=activity, status=Ticket.STATUS_USED))
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
            activity.name = self.input['name']  # 已发布的活动不可修改
            activity.place = self.input['place']  # 已发布的活动不可修改
            activity.book_start = datetime.datetime.strptime(self.input['bookStart'], "%Y-%m-%dT%H:%M:%S.%fZ")  # 已发布的活动不可修改 时间戳
            activity.status = self.input['status']  # 已发布的活动只能修改为1（发布） 不能修改为0（暂存）

        activity.description = self.input['description']
        activity.pic_url = self.input['picUrl']

        if time.time() <= activity.end_time.timestamp():
            activity.start_time = datetime.datetime.strptime(self.input['startTime'], "%Y-%m-%dT%H:%M:%S.%fZ")  # 活动结束后不可修改 时间戳
            activity.end_time = datetime.datetime.strptime(self.input['endTime'], "%Y-%m-%dT%H:%M:%S.%fZ")  # 活动结束后不可修改 时间戳
            activity.book_end = datetime.datetime.strptime(self.input['bookEnd'], "%Y-%m-%dT%H:%M:%S.%fZ")  # 活动结束后不可修改 时间戳

        if time.time() <= activity.book_start.timestamp():
            activity.total_tickets = self.input['totalTickets']  # 抢票开始后不可修改

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
        self.check_input('id', 'name', 'place', 'description', 'picUrl',
                         'startTime', 'endTime', 'bookStart', 'bookEnd',
                         'totalTickets', 'status')
        try:
            activity = Activity.objects.get(id=self.input['id'])
        except Activity.DoesNotExist:
            raise NotExistError("activity detail change error: not exist")
        self.dict_to_exist_activity(activity)


class ActivityCreate(APIView):
    def dict_to_new_activity(self):
        Activity.objects.create(
            name=self.input['name'],
            key=self.input['key'],
            place=self.input['place'],
            description=self.input['description'],
            pic_url=self.input['picUrl'],
            start_time=datetime.datetime.strptime(self.input['startTime'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            end_time=datetime.datetime.strptime(self.input['endTime'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            book_start=datetime.datetime.strptime(self.input['bookStart'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            book_end=datetime.datetime.strptime(self.input['bookEnd'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            total_tickets=int(self.input['totalTickets']),
            status=self.input['status'],
            remain_tickets=int(self.input['totalTickets'])
        )

    def post(self):
        self.check_input('name', 'key', 'place', 'description', 'picUrl',
                         'startTime', 'endTime', 'bookStart', 'bookEnd',
                         'totalTickets', 'status')
        try:
            self.dict_to_new_activity()
        except:
            raise InputError(str(self.input))

class ActivityMenu(APIView):

    # convert an Activity instance to a dict instance
    def activity_to_dict(self, activity, menu_id_list):
        activity_dict = {}
        activity_dict['id'] = activity.id
        activity_dict['name'] = activity.name
        if activity.id in menu_id_list:
            activity['menuIndex'] = menu_id_list.index(activity.id) + 1
        else:
            activity['menuIndex'] = 0
        return activity_dict

    def get_menu_list(self):
        menu_list = CustomWeChatView.lib.get_wechat_menu()
        menu_book_list = []
        for btn in menu_list:
            if btn['name'] == '抢票':
                menu_book_list += btn.get('sub_button', list())
        menu_id_list = []
        for btn in menu_book_list:
            if 'key' in btn:
                activity_id = btn['key']
                if activity_id.startwith(CustomWeChatView.event_keys['book_header']):
                    activity_id = activity_id[len(CustomWeChatView.event_keys['book_header']):]
                if activity_id and activity_id.isdigit():
                    menu_id_list.append(int(activity_id))

    def get(self):
        pass

    def post(self):
        pass

class ActivityCheckin(APIView):

    def post(self):
        pass


class ImageUpload(APIView):
    def post(self):
        self.check_input('image')
        img = ActivityImage.objects.create(image=self.input['image'][0])
        file_content = ContentFile(img.image.read())
        img.save()
        hd = self.request.is_secure() and "https://" or "http://"
        print(hd)
        return hd+self.request.get_host()+'/'+img.image.url


