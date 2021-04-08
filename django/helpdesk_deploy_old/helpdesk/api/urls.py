from django.urls import path

from .views import upload_file, get_wiki_page, upload_image, fetch_url

app_name = 'api'

urlpatterns = [
    path('UploadImage/',upload_image,name="upload_image"),
    path('UploadFile/',upload_file,name="upload_file"),
    path('FetchUrl/',fetch_url,name="fetch_url"),
    path('GetJson/',get_wiki_page,name="get_wiki_page"),
]
