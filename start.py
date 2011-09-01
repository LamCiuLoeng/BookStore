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

from sys2do import application

def start_server():
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888, "192.168.20.41")
    logging.info("Server is running >>>>")
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    start_server()
