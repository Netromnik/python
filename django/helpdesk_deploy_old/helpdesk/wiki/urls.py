from django.urls import path
from .wiki import WikiPage ,WikiPageEdit ,wiki_dasbord
from .wiki_create import WikiNews ,WikiUpdate
app_name = 'views'

urlpatterns = [
    path('newarticle/', WikiNews.as_view(), name="wiki_create"),
    path('<int:pk>/update/',WikiUpdate.as_view(),name="wiki_update"),
    path('<int:pk>/edit/',WikiPageEdit.as_view(),name="wiki_edit"),
    path('<int:pk>/',WikiPage.as_view(),name="wiki_page"),
    path('',wiki_dasbord,name="wiki_dasbord"),
]