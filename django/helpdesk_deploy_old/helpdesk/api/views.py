import json

from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from base.models import File
from wiki.models import WikiArticleModel


# upload file editjs.
@csrf_exempt
@require_POST
def upload_image(request,**kwargs):
    if not request.user.is_authenticated:
        return Http404("")
    f = File()
    f.document = request.FILES['image']
    f.collect = request.user.get_wiki_collect()
    f.save()
    obj = {
        "success": 1,
        "file": {
            "url": "",
        }
    }
    obj["file"]["url"] = f.url()
    return JsonResponse(obj)

# return obj.
@csrf_exempt
@require_POST
def fetch_url(request,**kwargs):
    if not request.user.is_authenticated:
        return Http404("")
    obj = {
        "success": 1,
        "file": {
            "url": "",
        }
    }
    f = b'test'
    js = json.loads(request.body)
    obj["file"]["url"] = js["url"]
    return JsonResponse(obj)

# return obj.
@csrf_exempt
@require_POST
def upload_file(request,**kwargs):
    if not request.user.is_authenticated or request.FILES.get('file') == None:
        return Http404("")
    f = File()
    f.document = request.FILES['file']
    f.collect = request.user.get_wiki_collect()
    f.save()
    obj = {
    "success" : 1,
    "file": {
        "url": "https://www.tesla.com/tesla_theme/assets/img/_vehicle_redesign/roadster_and_semi/roadster/hero.jpg",
        "size": 91,
        "name": "hero.jpg",
        "extension": "jpg"
    },
        "title": "Hero"
    }
    obj["file"]["url"] = f.url()
    obj["file"]["size"] = f.document.size
    obj["file"]["name"] = f.document.name.split("/")[-1]
    obj["file"]["extension"] = f.document.name.split(".")[-1]
    return JsonResponse(obj)

# return obj.
@csrf_exempt
@require_POST
def get_wiki_page(request,**kwargs):
    pk_row = request.META["HTTP_REFERER"].split("/")[-1][4:]
    # if not id_row.isdigit():
    #     return Http404("")
    if not request.user.is_authenticated:
        return Http404("")
    obj = WikiArticleModel.node_manager.get(pk = pk_row)
    return JsonResponse(obj)
