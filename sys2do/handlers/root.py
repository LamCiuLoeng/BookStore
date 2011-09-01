# -*- coding: utf-8 -*-
'''
###########################################
#  Created on 2011-9-1
#  @author: cl.lam
#  Description:
###########################################
'''
import logging
import base

__all__ = ["Handler", "PostHandler"]


class Handler(base.BaseHandler):

    def get(self):

        self.render("index.html")


class PostHandler(base.BaseHandler):

    def post(self):
        result = self.upload("name")
        if result[0] == 0 :
            self.flash("OK")
            logging.info(result)
        else:
            self.flash("Error")
        self.redirect("/index")



