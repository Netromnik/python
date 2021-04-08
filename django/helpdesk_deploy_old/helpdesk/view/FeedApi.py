from django.contrib.syndication.views import Feed
from django.http import Http404
from django.urls import reverse


class LatestEntriesFeed(Feed):
    title = "unsignet task"
    link = "/"
    description = "All stream unsignet task"

    def get_feed(self, obj, request):
        if not request.user.is_authenticated:
            return Http404
        self.request = request
        return super().get_feed(obj,request)

    def items(self):
        return self.request.user.get_unsignet_q()

    def item_title(self, item):
        return "[{}] {} [{}]".format(item.stream,item.title,item.autors)

    def item_description(self, item):
        return item.description

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return reverse('view:detail_ticket', args=[item.pk])
