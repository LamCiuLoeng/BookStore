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

__all__ = ["app_setting", ]

app_setting = {
               "tornado_setting" : {
                                    "static_path": os.path.join(os.path.dirname(__file__), "public"),
                                    "static_url_prefix" : "/public/",
                                    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
                                    "login_url": "/login",
                                    "template_path" : os.path.join(os.path.dirname(__file__), "templates"),
                                    "debug" : True,
                                    "xsrf_cookies": True,
                                    "upload_path" : os.path.join(os.path.dirname(__file__), "public", "upload"),
                                    },
               "addition_setting" : {
                                    "template_path_cache" : os.path.join(os.path.dirname(__file__), "templates_cache"),
                                    "logger_level" : logging.INFO,
                                     },

               "session_setting" : {
                                   "secret" : "123321",
                                   "session_dir" : os.path.join(os.path.dirname(__file__), "session"),
                                   },
               "db_setting" : {
                                "SQLALCHEMY_DATABASE_URI" : 'sqlite:///%s' % (os.path.join(os.path.dirname(__file__), "database.db"))
                               }
               }
