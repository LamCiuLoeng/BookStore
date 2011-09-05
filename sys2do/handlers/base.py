# -*- coding: utf-8 -*-
'''
###########################################
#  Created on 2011-9-1
#  @author: cl.lam
#  Description:
###########################################
'''
import os
import random
import string
import tornado.web
import logging
import traceback
import mako.lookup
from webhelpers.paginate import Page

from sys2do.setting import app_setting
from sys2do.util.session import TornadoSession
from sys2do.model import DBSession, Attachment
from sys2do.util.common import Date2Text, makeException

__all__ = ["BaseHandler", "MasterHander"]


class BaseHandler(tornado.web.RequestHandler):

    _lookup = mako.lookup.TemplateLookup(directories = [app_setting["tornado_setting"]["template_path"], ],
                                          module_directory = app_setting["addition_setting"]["template_path_cache"],
                                          input_encoding = 'utf-8',
                                          output_encoding = 'utf-8')


    def initialize(self, **kw):
        self.session = TornadoSession(self.application.session_manager, self)

    def render_string(self, template_name, **kwargs):
        mytemplate = self._lookup.get_template(template_name)
        args = dict(
            handler = self,
            request = self.request,
            current_user = self.current_user,
            locale = self.locale,
            _ = self.locale.translate,
            static_url = self.static_url,
            xsrf_form_html = self.xsrf_form_html,
            reverse_url = self.application.reverse_url,
            get_any_permissions = self.get_any_permissions,
            get_all_permissions = self.get_all_permissions,
            in_all_groups = self.in_all_groups,
            in_any_groups = self.in_any_groups,
        )
#        args.update(self.ui)
        args.update(kwargs)
        return mytemplate.render(**args)

    def render(self, template_name, **kwargs):
        self.finish(self.render_string(template_name, **kwargs))


    def flash(self, msg = None, status = "OK"):
        if msg:
            self.session["message"] = msg
            self.session.save()
        else:
            tmp = self.session.pop("message")
            self.session.save()
            return tmp

    def need_flash(self):
        return bool(self.session.get("message", False))


    def getOr404(self, obj, id, redirect_url = "/index", message = "The record deosn't exist!"):
        try:
            return DBSession.query(obj).filter(obj.id == id).one()
        except:
            self.flash(message)
            self.redirect(redirect_url)

    def upload(self, file_name):
        try:
            f = self.request.files[file_name][0]
            original_fname = f['filename']
            extension = os.path.splitext(original_fname)[1].lower()
            fname = Date2Text(dateTimeFormat = "%Y%m%d%H%M%S", defaultNow = True) + ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))
            final_filename = fname + extension

            d = os.path.join(self.application.settings.get("static_path"),
                             self.application.settings.get("upload_relative_path"))
            if not os.path.exists(d):
                os.makedirs(d)
            full_path = os.path.join(d, final_filename)
            output_file = open(full_path, 'wb')
            output_file.write(f['body'])
            output_file.close()

            DBSession.add(Attachment(name = final_filename, path = full_path, original_name = original_fname,
                                     url = self.static_url("/".join([self.application.settings.get("upload_relative_path"), final_filename]))))
            DBSession.commit()
            return (0, original_fname, final_filename, full_path)
        except:
            DBSession.rollback()
            logging.error(traceback.print_exc())
            return (1, None, None, None)


    def is_user_login(self):
        return self.session.get("is_user_login", False)

    def get_any_permissions(self, *permissions):
        user_permissions = self.session.get("permissions", [])
        for permission in permissions:
            if permission in user_permissions: return True
        return False

    def get_all_permissions(self, *permissions):
        user_permissions = self.session.get("permissions", [])
        for permission in permissions:
            if permission not in user_permissions: return False
        return True

    def in_any_groups(self, *groups):
        user_groups = self.session.get("groups", [])
        for group in groups:
            if group in user_groups : return True
        return False

    def in_all_groups(self, *groups):
        user_groups = self.session.get("groups", [])
        for group in groups:
            if group not in user_groups : return False
        return True

    def get_current_user(self):
        return self.session.get("user", None)

    def get_user_locale(self):
        try:
            return self.session["user"].locale
        except:
            return None


class MasterHander(BaseHandler):

    url_prefix = None
    template_prefix = None
    dbObj = None
    action_mapping = {
                      #name  : (function,permission)
                      "list" : ("_list", None),
                      "view" : ("_view", None),
                      "new"  : ("_new", None),
                      "update" : ("_update", None),
                      "delete" : ("_delete", None),
                      "save_new"   : ("_save_new", None),
                      "save_update" : ("_save_update", None),
                      }
    items_per_page = 20

    def _list(self):
        items = DBSession.query(self.dbObj).filter(self.dbObj.active == 0).all()
        try:
            page = int(self.get_argument("page", 1))
        except:
            page = 1

        my_page = Page(items, page = page, items_per_page = self.items_per_page,
                       url = lambda page:"%s?action=list&page=%d" % (self.request.path, page))
        pager = my_page.pager(symbol_first = "<<", show_if_single_page = True)
        self.render(self.template_prefix + "_list.html", my_page = my_page, pager = pager)


    def _view(self):
        obj = self.getOr404(self.dbObj, self.get_argument("id", None))
        self.render(self.template_prefix + "_view.html", values = obj.populate())

    def _new(self):
        self.render(self.template_prefix + "_new.html", values = {})

    def _update(self):
        obj = self.getOr404(self.dbObj, self.get_argument("id", None))
        self.render(self.template_prefix + "_update.html", values = obj.populate())

    def _delete(self):
        obj = self.getOr404(self.dbObj, self.get_argument("id", None))
        obj.active = 1
        DBSession.commit()
        self.flash("Delete the record successfully!")
        self.redirect("%s?action=list" % self.url_prefix)


    def _save_new(self):
        try:
            result = self.dbObj.save_new(self)
            DBSession.commit()
            self.flash("Save the record successfully!")
        except Exception as e:
            DBSession.rollback()
            self.flash(getattr(e, "msg", None) or "This operation is not available now.")
            self._new()
        self.redirect("%s?action=view&id=%d" % (self.url_prefix, result.id))


    def _save_update(self):
        try:
            result = self.dbObj.save_update(self.get_argument("id", None), self)
            DBSession.commit()
            self.flash("Save the record successfully!")
        except Exception as e:
            logging.error(traceback.print_exc())
            DBSession.rollbak()
            self.flash(getattr(e, "msg", None) or "This operation is not available now.")
            self._update()
        self.redirect("%s?action=view&id=%d" % (self.url_prefix, result.id))



    def _valiate_permission(self, permission):
        return True


    def get(self):
        action = self.get_argument("action", None)

        if action not in self.action_mapping :
            self.flash("No such action supply!")
            self.redirect("/index")

        fun, permission = self.action_mapping[action]
        if not self._valiate_permission(permission):
            self.flash("Permission insufficient!")
            self.redirect("/index")
        getattr(self, fun)()

    def post(self):
        self.get()
