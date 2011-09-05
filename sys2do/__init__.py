# -*- coding: utf-8 -*-
'''
###########################################
#  Created on 2011-9-1
#  @author: cl.lam
#  Description:
###########################################
'''
import os
import logging
import tornado

from sys2do.setting import app_setting
from sys2do.util.session import TornadoSessionManager
from sys2do.handlers import *

__all__ = ["application"]


logging.getLogger().setLevel(app_setting["addition_setting"]["logger_level"])


application = tornado.web.Application([
    (r"^/$|^/index$", Handler),
    (r"/p", PostHandler),
    (r"/download", DownloadHandler),
    (UserHandler.url_prefix, UserHandler),
    (AuthHandler.url_prefix, AuthHandler),
], **app_setting["tornado_setting"])


application.session_manager = TornadoSessionManager(**app_setting["session_setting"])
