# -*- coding: utf-8 -*-

from irk.utils.search import ModelSearch


class BaseMaterialSearch(ModelSearch):
    fields = (
        'stamp', 'title', 'author', 'caption', 'content', 'source_site', 'sites', 'views_cnt',
        'popularity', 'project__title',
    )
    boost = {
        'project__title': 1,
        'title': 1,
        'caption': 1,
        'content': 1,
        'author': 1,
    }

    def get_queryset(self):
        return super(BaseMaterialSearch, self).get_queryset().filter(is_hidden=False)


class NewsSearch(BaseMaterialSearch):
    pass


class ArticleSearch(BaseMaterialSearch):
    pass

class TildaArticleSearch(BaseMaterialSearch):
    fields = (
        'stamp', 'title', 'author', 'caption', 'tilda_content', 'source_site', 'sites', 'views_cnt',
        'popularity', 'project__title',
    )


class PhotoSearch(BaseMaterialSearch):
    pass


class VideoSearch(BaseMaterialSearch):
    pass


class InfographicSearch(BaseMaterialSearch):
    pass


class PodcastSearch(BaseMaterialSearch):
    pass
