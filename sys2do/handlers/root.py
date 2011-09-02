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
import urllib

from sys2do.model import Attachment, User

__all__ = ["Handler", "DownloadHandler", "PostHandler", "UserHandler"]


class Handler(base.BaseHandler):

    def get(self):

        self.render("index.html")


class DownloadHandler(base.BaseHandler):

    def get(self):
        obj = self.getOr404(Attachment, self.get_argument("id", None), "/index")
        f = open(obj.path, 'rb')
        content = "".join(f.readlines())
        f.close()
        isIE = self.request.headers["User-Agent"].find("MSIE") > -1
        self.set_header("Content-type", "application/x-download")
        if isIE :
            self.set_header("Content-Disposition", "attachment;filename=%s" % urllib.quote(obj.original_name.encode('utf-8')))
        else:
            self.set_header('Content-Disposition', "attachment;filename=%s" % obj.original_name)
        self.write(content)



class PostHandler(base.BaseHandler):

    def post(self):
        result = self.upload("name")
        if result[0] == 0 :
            self.flash("OK")
            logging.info(result)
        else:
            self.flash("Error")
        self.redirect("/index")


class UserHandler(base.MasterHander):
    dbObj = User
    url_prefix = "/user"
    template_prefix = "user"
