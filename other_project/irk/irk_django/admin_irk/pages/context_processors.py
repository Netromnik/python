# -*- coding: UTF-8 -*-

from models import Page


def getFlatPage(request):
    try:
        return Page.on_site.get(url=request.path)
    except:
        site_url = "%s%s" % (request.get_host(), request.path)

        try:
            url = "/%s" %site_url.replace(request.csite.url, "")
        except AttributeError:
            return None

        try:
            return Page.on_site.get(url=url)
        except:
            return None


def current_page(request):
    cpage = getFlatPage(request)
    return {'local_flatpage': cpage}
