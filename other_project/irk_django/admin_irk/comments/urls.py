# -*- coding: utf-8 -*-

from django.conf.urls import url

from irk.comments.views import comment

app_name = 'comments'

urlpatterns = [
    url(r'list/(?P<ct_id>\d+)/(?P<target_id>\d+)/$', comment.CommentListView.as_view(), name='list'),
    url(r'children/(?P<comment_id>\d+)/$', comment.CommentChildrenListView.as_view(), name='children'),
    url(r'comment/create/$', comment.CommentCreateView.as_view(), name='create'),
    url(r'comment/(?P<comment_id>\d+)/delete/$', comment.CommentDeleteView.as_view(), name='delete'),
    url(r'comment/(?P<comment_id>\d+)/restore/$', comment.CommentRestoreView.as_view(), name='restore'),
    url(r'comment/(?P<comment_id>\d+)/history/$', comment.history, name='history'),
    url(r'comment/(?P<comment_id>\d+)/edit/$', comment.CommentEditView.as_view(), name='edit'),
    url(r'comment/(?P<comment_id>\d+)/text/$', comment.CommentTextView.as_view(), name='text'),
    url(r'comment/(?P<comment_id>\d+)/user_delete/$', comment.CommentUserDeleteView.as_view(), name='user_delete'),
]
