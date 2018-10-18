# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler, WeChatLib, WeChatView
from wechat.models import Activity,Ticket,User
from django.db.models import Q
import datetime, time
from WeChatTicket.settings import WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET
from codex.baseerror import BookFailedError, NotExistError

__author__ = "Epsirom"


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        self.user.student_id = ''
        self.user.save()
        return self.reply_text(self.get_message('unbind_account'))

class BindAccountHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        return self.reply_text(self.get_message('bind_account'))


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))

class BookWhatHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_what'])


    def handle(self):
        activity_list = Activity.objects.filter(Q(status=Activity.STATUS_PUBLISHED) & Q(book_start__lt=datetime.datetime.now()) & Q(book_end__gt=datetime.datetime.now()))
        news=[]
        for activity in activity_list:
            news.append(self.activity_to_new(activity))
        return self.reply_news(news)


class GetTicketHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        tickets = []
        if User.objects.filter(open_id=self.user.open_id).exists():
            user = User.objects.get(open_id=self.user.open_id)
            tickets = Ticket.objects.filter(Q(student_id=user.student_id))
        news = []
        for ticket in tickets:
            news.append(self.ticket_to_new(ticket))
        return self.reply_news(news)

class BookHeaderHandler(WeChatHandler):

    def check(self):
        if self.is_msg_type('event') and (self.input['Event'] == 'CLICK') and (self.input['EventKey'][:17] == self.view.event_keys['book_header']):
            return True
        return False

    def handle(self):
        activity = Activity.objects.get(pk=int(self.input['EventKey'][17:]))
        return self.reply_single_news(self.activity_to_new(activity))

class BookTicketHandler(WeChatHandler):
    # 抢票
    def check(self):
        lib = WeChatLib(WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET)
        menu_list = lib.get_wechat_menu()[-1]['sub_button']
        event_keys = [book_btn['key'] for book_btn in menu_list]
        return self.is_text_command("抢票") or self.is_event_click(*event_keys)

    def handle(self):
        if self.is_event('CLICK'):
            activity_id = int(self.input['EventKey'][len(WeChatView.CustomWeChatView.event_keys['book_header']):])
            try:
                activity = Activity.objects.get(id=activity_id)
            except Activity.DoesNotExist:
                raise NotExistError
        else:
            activity_name = self.get_first_param_in_command()
            try:
                activity = Activity.objects.get(name=activity_name)
            except Activity.DoesNotExist:
                raise NotExistError

        # user
        if self.user.student_id == "":
            # 未绑定学号
            return self.reply_text(self.get_message('student_id_not_bind'))

        # activity
        if not activity:
            # 活动不存在或活动名输入错误
            return self.reply_text(self.get_message('activity_not_exist'))
        if time.time() < activity.book_start.timestamp():
            # 还未到抢票开始时间
            return self.reply_text(self.get_message('book_not_start'))
        if time.time() > activity.book_end.timestamp():
            # 已经超过了抢票开始时间
            return self.reply_text(self.get_message('book_already_finish'))
        if activity.remain_tickets <= 0:
            # 票已抢光
            return self.reply_text(self.get_message('tickets_out'))

        # ticket
        if Ticket.objects.filter(Q(student_id=self.user.student_id) & Q(activity=activity)).exists():
            # 本学号已经抢过票
            return self.reply_text(self.get_message('already_book_tickets', self.user))

        activity.remain_tickets = activity.remain_tickets - 1
        activity.save()

        try:
            Ticket.objects.create(student_id=self.user.student_id, unique_id=self.user.student_id+activity_name,
                                  activity=activity, status=Ticket.STATUS_VALID)
        except:
            raise BookFailedError("Book ticket handler error: ticket creation failed")

        return self.reply_text(self.get_message('book_success'))