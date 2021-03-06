# -*- coding: utf-8 -*-
#



__author__ = "Epsirom"


class BaseError(Exception):

    def __init__(self, code, msg):
        super(BaseError, self).__init__(msg)
        self.code = code
        self.msg = msg

    def __repr__(self):
        return '[ERRCODE=%d] %s' % (self.code, self.msg)


class InputError(BaseError):

    def __init__(self, msg):
        super(InputError, self).__init__(1, msg)


class LogicError(BaseError):

    def __init__(self, msg):
        super(LogicError, self).__init__(2, msg)


class ValidateError(BaseError):

    def __init__(self, msg):
        super(ValidateError, self).__init__(3, msg)

class NotExistError(BaseError):

    def __init__(self, msg):
        super(NotExistError, self).__init__(4, msg)

class AdminAuthError(BaseError):

    def __init__(self, msg):
        super(AdminAuthError, self).__init__(4, msg)

class AdminNotLogin(BaseError):

    def __init__(self, msg):
        super(AdminNotLogin, self).__init__(4, msg)

class BookFailedError(BaseError):

    def __init__(self, msg):
        super(BookFailedError, self).__init__(7, msg)

class ReturnFailedError(BaseError):

    def __init__(self, msg):
        super(ReturnFailedError, self).__init__(7, msg)
