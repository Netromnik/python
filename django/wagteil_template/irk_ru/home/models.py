from main.models import AbstractArticlePage
from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from django.db import models



class BlogPanelTag(TaggedItemBase):
    content_object = ParentalKey(
        'ArticleEx',
        related_name='tagged_items2',
        on_delete=models.CASCADE,
    )


class ArticleEx(AbstractArticlePage):
    tags = ClusterTaggableManager(through='BlogPanelTag', blank=True)
