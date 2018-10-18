# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
from wechat.models import Activity,Ticket,User
from django.db.models import Q
import datetime, time
from WeChatTicket import settings

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
        tickets=[]
        if User.objects.filter(open_id=self.user.open_id).exists():
            user= User.objects.get(open_id=self.user.open_id)
            tickets =Ticket.objects.filter(Q(student_id=user.student_id))
        news=[]
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
