from django.db import models
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase


from wagtail.core.models import Page, Orderable
from wagtail.core.fields import StreamField
from wagtail.search import index
from wagtail.admin import  blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtailstreamforms.blocks import WagtailFormBlock
from wagtail.snippets.models import register_snippet
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.embeds.blocks import EmbedBlock

from wagtailautocomplete.edit_handlers import AutocompletePanel
from wagtail_blocks.blocks import HeaderBlock, ListBlock, ImageTextOverlayBlock, CroppedImagesWithTextBlock, \
    ListWithImagesBlock, ChartBlock, MapBlock

class AbsBlogPageTag(TaggedItemBase):
    model_name = 'BlogPage'
    content_object = ParentalKey(
        model_name,
        related_name='tagged_items',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class PersonBlock(blocks.StructBlock):
    name = blocks.StreamBlock(

    )

    class Meta:
        icon = 'user'



class CustomPage(Page):
    show_in_menus = False # delete support auto add to menu
    tags = ClusterTaggableManager(through=AbsBlogPageTag, blank=True)

    search_fields = [
        index.SearchField('title', partial_match=True, boost=2),
        index.SearchField('tags', partial_match=False, boost=2),
        index.AutocompleteField('title'),
        index.AutocompleteField('tags'),
        index.FilterField('title'),
        index.FilterField('tags'),


        index.FilterField('id'),
        index.FilterField('live'),
        index.FilterField('owner'),
        index.FilterField('content_type'),
        index.FilterField('path'),
        index.FilterField('depth'),
        index.FilterField('locked'),
        index.FilterField('show_in_menus'),
        index.FilterField('first_published_at'),
        index.FilterField('last_published_at'),
        index.FilterField('latest_revision_created_at'),
        index.FilterField('locale'),
        index.FilterField('translation_key'),
    ]

    class Meta:
        abstract = True

class AbstractArticlePage(CustomPage):
    features = [
                'h2', 'h3', 'bold', 'italic', 'link',
                'ol', 'ul',
                'hr'  # horizontal rules
                'link',  # page, external and email links
                'document'  # link - links to documents
                'image',
                'strikethrough',
                'blockquote'
                ]
    image_preview = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    date = models.DateField(_("Post date"), help_text='Отображаемое время при создании.')


    promote_panels = Page.promote_panels + [
        FieldPanel('slug', classname="Full"),
        AutocompletePanel('tags', classname="Full"),
    ]
    #  Content panels
    content = StreamField([
        ('header', HeaderBlock(form_classname="full title")),
        ('paragraph', blocks.RichTextBlock(
            # features=features
        )),
        ('form', WagtailFormBlock()),
        ('list', ListBlock()),
        ('image_text_overlay', ImageTextOverlayBlock()),
        ('cropped_images_with_text', CroppedImagesWithTextBlock()),
        ('list_with_images', ListWithImagesBlock()),
        ('chart', ChartBlock()),
        ('map', MapBlock()),
        ('pooling', blocks.StreamBlock([
            ('text', blocks.StructBlock([
                ('name', blocks.TextBlock()),
                ('start_vote', blocks.IntegerBlock()),
            ]))
        ],icon='icon-ticket'),),
        ('carousel', blocks.StreamBlock(
            [
                ('image', ImageChooserBlock()),
                ('quotation', blocks.StructBlock([
                    ('text', blocks.TextBlock()),
                    ('author', blocks.CharBlock()),
                ])),
                ('video', EmbedBlock()),
            ],
            icon='cogs'
        )),
        ('video', EmbedBlock()),

    ])


    content_panels = [
        FieldPanel('title', classname="Full"),
        StreamFieldPanel("content", classname="Full"),
    ]


    # Search index configuration

    search_fields = Page.search_fields + [
        index.SearchField('content'),
        index.FilterField('date'),
    ]

    class Meta:
        abstract = True
