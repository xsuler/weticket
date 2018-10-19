# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler, WeChatLib, WeChatView
from wechat.models import Activity,Ticket,User
from django.db.models import Q
import datetime, time
from WeChatTicket.settings import WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET
import uuid
from codex.baseerror import BookFailedError, NotExistError,ReturnFailedError

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


class CheckTicketHandler(WeChatHandler):

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
    # 抢票
    def check(self):
        return (self.is_msg_type('event') and (self.input['Event'] == 'CLICK') and (self.input['EventKey'][:17] == self.view.event_keys['book_header'])) or self.is_text_command("抢票")

    def handle(self):
        if self.is_event('CLICK'):
            activity_id = int(self.input['EventKey'][len(self.view.event_keys['book_header']):])
            try:
                activity = Activity.objects.get(id=activity_id)
            except Activity.DoesNotExist:
                raise NotExistError
        else:
            try:
                activity_name = self.get_first_param_in_command()
            except:
                return self.reply_text((self.get_message('book_format_wrong')))
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
            ticket=Ticket.objects.get(Q(student_id=self.user.student_id) & Q(activity=activity))
            if ticket.status==Ticket.STATUS_VALID:
                return self.reply_text(self.get_message('already_book_tickets'))
            else:
                ticket.status=Ticket.STATUS_VALID
                activity.remain_tickets = activity.remain_tickets - 1
                ticket.save()
                activity.save()
                return self.reply_text(self.get_message('book_success'))


        activity.remain_tickets = activity.remain_tickets - 1
        activity.save()
        uniqueid=uuid.uuid3(uuid.NAMESPACE_DNS, self.user.student_id).hex+uuid.uuid3(uuid.NAMESPACE_DNS, activity.name).hex

        try:
            Ticket.objects.create(student_id=self.user.student_id, unique_id=uniqueid,
                                  activity=activity, status=Ticket.STATUS_VALID)
        except:
            raise BookFailedError("Book ticket handler error: ticket creation failed")

        return self.reply_text(self.get_message('book_success'))

class ReturnTicketHandler(WeChatHandler):
    # 退票
    def check(self):
        return self.is_text_command("退票")

    def handle(self):
        activity_name = self.get_first_param_in_command()
        activity = Activity.objects.get(name=activity_name)

        # user
        if self.user.student_id == "":
            # 未绑定学号
            return self.reply_text(self.get_message('student_id_not_bind'))

        # activity
        if not activity:
            # 活动不存在或活动名输入错误
            return self.reply_text(self.get_message('activity_not_exist'))
        if time.time() < activity.book_start.timestamp():
            # 票尚未放出
            return self.reply_text(self.get_message('book_not_start'))
        if time.time() > activity.start_time.timestamp():
            # 活动已经开始
            return self.reply_text(self.get_message('activity_already_start'))

        # ticket
        if Ticket.objects.filter(Q(student_id=self.user.student_id) & Q(activity=activity)).exists():
            # 本学号有票
            activity.remain_tickets = activity.remain_tickets + 1
            activity.save()
        else:
            return self.reply_text(self.get_message('ticket_not_exist'))


        try:
            ticket = Ticket.objects.get(Q(student_id=self.user.student_id) & Q(activity=activity))
            if ticket.status==Ticket.STATUS_CANCELLED:
                return self.reply_text("该票已被取消，不能重复退票")
            else:
                ticket.status = Ticket.STATUS_CANCELLED
                ticket.save()
        except:
            raise ReturnFailedError("Return ticket handler error: ticket return failed")

        return self.reply_text(self.get_message('return_success'))

class GetTicketHandler(WeChatHandler):

    def check(self):
        return self.is_text_command("取票")

    def handle(self):
        activity_name = self.get_first_param_in_command()
        activity = Activity.objects.get(name=activity_name)
        # user
        if self.user.student_id == "":
            # 未绑定学号
            return self.reply_text(self.get_message('student_id_not_bind'))

        # activity
        if not activity:
            # 活动不存在或活动名输入错误
            return self.reply_text(self.get_message('activity_not_exist'))
        if time.time() < activity.book_start.timestamp():
            # 票尚未放出
            return self.reply_text(self.get_message('book_not_start'))

        # ticket
        if Ticket.objects.filter(Q(student_id=self.user.student_id) & Q(activity=activity)).exists():
            # 本学号有票
            ticket = Ticket.objects.get(Q(student_id=self.user.student_id) & Q(activity=activity))
            return self.reply_single_news(self.ticket_to_new(ticket))
        else:
            return self.reply_text(self.get_message('ticket_not_exist'))


