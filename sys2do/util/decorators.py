# -*- coding: utf-8 -*-
from webhelpers.paginate import Page

from common import partial, Bunch





class mypaginate(object):
    def __init__(self, name, use_prefix = False,
        items_per_page = 10, max_items_per_page = 0):
        self.name = name
        prefix = use_prefix and name + '_' or ''
        self.page_param = prefix + 'page'
        self.items_per_page_param = prefix + 'items_per_page'
        self.items_per_page = items_per_page
        self.max_items_per_page = max_items_per_page


    def __call__(self, fun):
        def _f():
            output = fun()
            if not isinstance(output, dict) or not self.name in output: pass

            collection = output[self.name]

            request = fun.im_self.request
            page = Page(collection, request.paginate_page, request.paginate_items_per_page, controller = '/')
            page.kwargs = request.paginate_params

            if self.page_param != 'name':
                page.pager = partial(page.pager, page_param = self.page_param)
            if not getattr(request, 'paginators', None):
                request.paginators = Bunch()
            request.paginators[self.name] = output[self.name] = page
        return _f
