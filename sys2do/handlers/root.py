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
import traceback
import tornado


from sqlalchemy.sql import and_
from sqlalchemy.orm.exc import  NoResultFound

from sys2do.model import Attachment, User, DBSession
from sys2do.util.common import makeException

__all__ = ["Handler", "DownloadHandler", "PostHandler", "UserHandler", "AuthHandler"]


class Handler(base.BaseHandler):

    def get(self):
        logging.info(self.locale)
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



class AuthHandler(base.MasterHander):
    dbObj = User
    url_prefix = "/auth"
    template_prefix = "auth"


    action_mapping = {
                      #name  : (function,permission)
                      "login" : ("_login", None),
                      "check" : ("_check", None),
                      "logout" : ("_logout", None),
                      "register"  : ("_register", None),
                      "save_register" : ("_save_register", None),
                      "save_update" : ("_save_update", None),
                      }

    def _login(self):
        if self.is_user_login(): self.redirect("/index")
        self.render(self.template_prefix + "_login.html")

    def _check(self):
        if self.is_user_login(): self.redirect("/index")
        try:
            user = DBSession.query(User).filter(and_(User.active == 0, User.user_name == self.get_argument("user_name", None))).one()
            if user.password != self.get_argument("password", None): raise makeException("The password is worng!")
        except Exception as e:
            if isinstance(e, NoResultFound) : self.flash("The user is not exist!")
            elif getattr(e, "is_customize") : self.flash(str(e))
            logging.info(traceback.format_exc())
            self.redirect(self.get_login_url())
        else:
            self.session["is_user_login"] = True
            self.session["user"] = user
            self.session["permissions"] = [str(permission) for permission in user.permissions]
            self.session["groups"] = [str(group) for group in user.groups]
            self.session.save()
            self.locale #set the user's locale
            self.redirect("/index")



    def _logout(self):
        if not self.is_user_login(): self.redirect("/index")
        for key in ["is_user_login", "user", "permissions", "groups"]:
            if key in self.session : del self.session[key]
        self.session.save()
        self.redirect("/index")





    def _register(self):
        pass

    def _save_register(self):
        pass

    def _save_update(self):
        pass







class UserHandler(base.MasterHander):
    dbObj = User
    url_prefix = "/user"
    template_prefix = "user"
