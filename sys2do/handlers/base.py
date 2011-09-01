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

from sys2do.setting import app_setting
from sys2do.util.session import TornadoSession
from sys2do.model import DBSession
from sys2do.util.common import Date2Text

__all__ = ["BaseHandler"]


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
            reverse_url = self.application.reverse_url
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
            return DBSession.query(obj).get(id)
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

            d = self.application.settings.get("upload_path")
            if not os.path.exists(d):
                os.makedirs(d)
            full_path = os.path.join(d, final_filename)
            output_file = open(full_path, 'wb')
            output_file.write(f['body'])
            output_file.close()
            return (0, original_fname, final_filename, full_path)
        except:
            logging.error(traceback.print_exc())
            return (1, None, None, None)
