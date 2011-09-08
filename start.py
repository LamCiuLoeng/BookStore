# -*- coding: utf-8 -*-
'''
###########################################
#  Created on 2011-9-1
#  @author: cl.lam
#  Description:
###########################################
'''

import os, logging, sys
import tornado.httpserver
import tornado.ioloop
import tornado.locale

from sys2do import application, setting

def start_server():
    tornado.locale.load_translations(setting.app_setting["addition_setting"]["i18n_dir"])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(setting.app_setting["addition_setting"]["port"], setting.app_setting["addition_setting"]["server_ip"])
    logging.info("Server is running >>>>")
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    start_server()
