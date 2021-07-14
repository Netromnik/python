# coding=utf-8
import datetime
import json
import logging

from django.db import models
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from irk.gallery.models import Picture
from irk.news.forms import SocialPultUploadForm
from irk.news.models import (BaseMaterial, SocialPost, SocialPultDraft, SocialPultPost,
                             SocialPultUpload)
from irk.news.tasks import social_post_task
from irk.scheduler.tasks import SocpultScheduler
from irk.utils.http import ajax_request, JsonResponse

logger = logging.getLogger(__name__)


def index(request):
    """
    Соцпульт - единый интерфейс для публикации во все соцсети наших новостей
    """
    context = {
        'days_ahead': [],
        'hours': ['{:02}'.format(i) for i in range(24)],
        'minutes': ['{:02}'.format(i) for i in range(60)],
    }
    for i in range(10):
        context['days_ahead'].append(datetime.date.today() + datetime.timedelta(days=i))

    return render(request, 'admin/news/social_pult/index.html', context)


@csrf_exempt
@ajax_request
def upload(request, material_id):
    """
    URL для загрузки кастомного изображения для публикации
    """
    if not request.FILES:
        return HttpResponseBadRequest('No files attached!')

    if int(material_id) > 0:
        material = BaseMaterial.objects.get(pk=material_id).cast()
    else:
        material = None  # загрузка к новому чистому посту

    form = SocialPultUploadForm(request.POST, request.FILES)
    if form.is_valid():
        logger.debug('Form is valid, saving upload')
        upload = form.save(commit=False)
        upload.material = material
        upload.save()

        return {'ok': True, 'id': upload.id}

    logger.debug(u'Form has errors: %s', form.errors)
    return {'ok': False, 'error': form.errors, 'error_html': unicode(form.errors)}


@ajax_request
def list_scheduled(request):
    """
    Возвращает новости, к которым запланированы публикации
    """
    # задачи по публикации соцредактора из планировщика
    task_ids = SocpultScheduler.get_scheduled_tasks('publish').values_list('id', flat=True)

    # к каким соцпостам эти задачи относятся?
    posts = SocialPost.objects.filter(scheduled_task_id__in=task_ids)

    # а эти посты - публикация каких материалов?
    materials = []
    for post in posts:
        m = post.material
        item = {
            'material_id': m.id,
            'title': m.title,
            'editor_status': None,
            'some_other_value': 'something',
            'date': [m.stamp, m.published_time],
        }
        materials.append(item)

    return {'materials': materials, 'pagination': None}


def _scheduled_material_ids():
    """
    Возвращает айдишники материалов, для которых есть запланированные на будущее посты
    """
    task_ids = SocpultScheduler.get_scheduled_tasks('publish').values_list('id', flat=True)
    # к каким соцпостам эти задачи относятся?
    posts = SocialPost.objects.filter(scheduled_task_id__in=task_ids)
    return [p.material_id for p in posts]


@ajax_request
def list_news(request):
    """
    Возвращает список новостей для вывода в ленте слева
    """
    LENTA_LIMIT = 8
    pagination = {}

    query = BaseMaterial.objects.filter(is_hidden=False).order_by('-pk')

    # search
    q = request.GET.get('q', '')
    if q:
        query = query.filter(title__icontains=q)

    # в начало выдачи поставим запланированные посты
    # https://www.reddit.com/r/django/comments/4k2oyf/custom_ordering_question/d3bvhet
    scheduled_material_ids = _scheduled_material_ids()
    if scheduled_material_ids:
        cases = []
        extra = {'default': models.Value(1), 'output_field': models.IntegerField()}

        for material_id in scheduled_material_ids:
            cases.append(models.When(pk=material_id, then=models.Value(0)))

        query = query.annotate(custom_order=models.Case(*cases, **extra))\
            .order_by('custom_order', '-stamp', '-published_time')
    else:
        query = query.order_by('-stamp', '-published_time')

    # pagination
    total = query.count()
    pagination['total'] = total
    pagination['start'] =  start = int(request.GET.get('start', 0))
    pagination['limit'] = limit = int(request.GET.get('limit', LENTA_LIMIT))

    output = []
    materials = query[start:start+limit]
    for m in materials:
        item = {
            'material_id': m.id,
            'title': m.title,
            'editor_status': None,
            'date': [m.stamp, m.published_time],
        }
        if m.social_pult_post.last():
            # TODO: какой-то статус дать как отражение дел по публикации
            # может саммари
            # item['editor_status'] = m.social_pult_post.last().status
            # print(m.social_pult_post.last())
            social_pult_post = m.social_pult_post.last()
            social_post = social_pult_post.social_posts.last()

            # item['editor_status'] = 'publishing'
            item['editor_status'] = social_post.status if social_post else 'publishing'
        elif hasattr(m, 'social_pult_draft'):
            # если нет опубликованного поста, но есть черновик
            item['editor_status'] = 'draft'

        output.append(item)

    return {'materials': output, 'pagination': pagination}


@ajax_request
def load_editor(request, material_id):
    """
    Возвращает данные материала, для вставки в редактор

    Также возвращает данные сохраненного черновика, если для этого
    материала такой черновик был сохранен через метод save_draft.
    """
    m = material = BaseMaterial.objects.get(pk=material_id).cast()

    parts = []
    if m.title:
        parts.append(m.title)

    if hasattr(m, 'intro') and m.intro:
        parts.append(m.intro)
    elif hasattr(m, 'caption') and m.caption:
        parts.append(m.caption)

    text = '\n'.join(parts)

    # картинки
    images = []
    if hasattr(material, 'social_pult_uploads'):
        for instance in material.social_pult_uploads.all():
            images.append({
                'type': 'upload',
                'media_type': instance.media_type,  # image/video
                'original': instance.image.url,
                'id': str(instance.id),
            })

    if hasattr(m, 'social_card') and material.social_card:
        images.append({
            'type': 'social_card',
            'original': material.social_card.url,
            'id': 'social_card',
        })

    if material.gallery.main_gallery():
        for picture in material.gallery.main_gallery():
            images.append({
                'type': 'gallery',
                'original': picture.image.url,
                'id': str(picture.id),
            })

    if material.wide_image:
        images.append({
            'type': 'wide_image',
            'original': material.wide_image.url,
            'id': 'wide_image',
        })

    # сохраненный черновик из редактора, если есть
    draft = None
    if hasattr(material, 'social_pult_draft') and material.social_pult_draft:
        draft = material.social_pult_draft.data

    # ссылка на соц. пост, если есть
    # если такой пост есть, фронт загрузит его отдельно через /post/xxx/
    # и покажет вьюшку выделенную для просмотра прогресса
    social_pult_post = None
    if hasattr(material, 'social_pult_post'):
        post = material.social_pult_post.last()
        if post:
            social_pult_post = post.id

    # прогресс публикации
    # progress = {}
    # if editor_status == 'publishing':
    #     tasks = material.social_pult_post.social_posts.all()
    #     for task in tasks:
    #         progress[task.network] = {
    #             'social_post_id': task.id,
    #             'status': task.status,
    #             'result': task.sid,
    #         }

    return {
        'material_id': m.id,
        'title': m.title,
        'text': text,
        'url': m.get_absolute_url_with_domain(),
        'images': images,
        'draft': draft,
        'social_pult_post': social_pult_post,
    }


def parse_date(post):
    """
    Парсит дату, которая приходит в посте с фронтенда
    """
    format = '%Y-%m-%d %H:%M'
    date_string = '{day} {hour}:{minute}'.format(**post)
    return datetime.datetime.strptime(date_string, format)


class PublishView(View):
    def run_posting(self, network, material, social_pult_post, data, when=None):
        """
        Запускает задачу публикации и создает в базе объект SocialPost со статусом publishing

        Если when установлен в будущем, то планирует через планировщик.
        """
        result = {}
        now = datetime.datetime.now()
        safe_interval = datetime.timedelta(minutes=5)
        is_scheduled = when > now + safe_interval

        social_post = SocialPost()
        social_post.network = network
        social_post.material = material
        social_post.social_pult_post = social_pult_post
        social_post.status = 'scheduled' if is_scheduled else 'publishing'
        social_post.save()  # чтобы получить id

        if is_scheduled:
            scheduler = SocpultScheduler()
            meta = {'social_post': social_post.id, 'data': data}
            task = scheduler.add_task('publish', when, json.dumps(meta))

            # запомним, чтобы потом можно было найти дату планируемой публикации
            social_post.scheduled_task = task
            social_post.save()

            result = {
                'is_scheduled': True,
                'task_id': task.id,  # back comp.
                'scheduler_task_id': task.id,
                'when': str(when),
                'social_post_id': social_post.id,
            }
        else:
            # привяжем таск селери
            task = social_post_task.delay(network, material.id, social_post.id, data)
            social_post.task_id = task.id

            # Если стоит CELERY_ALWAYS_EAGER, то вызов delay выше уже выполнился
            # и в базе данных social_post_task уже обновился. Теперь сохраним только
            # поле task_id - чтобы не перезаписать поле status.
            social_post.save(update_fields=['task_id'])

            result = {
                'is_scheduled': False,
                'task_id': task.id,  # back comp.
                'celery_task_id': task.id,
                'social_post_id': social_post.id,
            }

        return result

    def get_images(self, image_list, material):
        """
        Преобразует id изображений, которые приходят с фронтенда,
        в список путей к файлам.
        {type: gallery, id: 1234} -> ['/var/www/../img.png']
        """

        result = []
        for item in image_list:
            if item['type'] == 'gallery':
                picture_id = item['id']
                pic = Picture.objects.get(pk=picture_id)
                result.append(pic.image.path)
            elif item['type'] == 'social_card':
                pic = material.social_card
                result.append(pic.path)
            elif item['type'] == 'wide_image':
                result.append(material.wide_image.path)
            elif item['type'] == 'upload':
                upload_id = item['id']
                pic = SocialPultUpload.objects.get(pk=upload_id)
                result.append(pic.image.path)

        return result

    def get_images2(self, image_list, material):
        """
        Вернуть URL изображения на нашем сервере
        """

        result = []
        for item in image_list:
            if item['type'] == 'gallery':
                picture_id = item['id']
                pic = Picture.objects.get(pk=picture_id)
                result.append(pic.image.url)
            elif item['type'] == 'social_card':
                pic = material.social_card
                result.append(pic.url)
            elif item['type'] == 'wide_image':
                result.append(material.wide_image.url)
            elif item['type'] == 'upload':
                upload_id = item['id']
                pic = SocialPultUpload.objects.get(pk=upload_id)
                result.append(pic.image.url)

        return result

    def post(self, request, material_id):
        """
        Опубликовать пост в соцсети (или запланировать)
        """
        result = {}
        material = BaseMaterial.objects.get(pk=material_id)
        material = material.cast()
        post = json.loads(request.body)

        # создадим объект, хранящий эту публикацию как целое
        social_pult_post = SocialPultPost()
        social_pult_post.material = material
        social_pult_post.text = post['text']
        social_pult_post.text_twitter = post.get('twitter_text', '')
        social_pult_post.url = post['url']
        social_pult_post.selected_images = json.dumps(post['selected_images'])
        social_pult_post.save()

        data = {'link': post['url']}
        publish_date = parse_date(post)

        # а эти данные уходят в соцсети
        if 'twitter' in post:
            data['text'] = post['twitter']['text']
            data['images'] = self.get_images(post['twitter']['images'], material)
            result['twitter'] = self.run_posting('twitter', material, social_pult_post, data, publish_date)

        if 'facebook' in post:
            data['text'] = post['facebook']['text']
            data['images'] = self.get_images(post['facebook']['images'], material)
            data['image_urls'] = self.get_images2(post['facebook']['images'], material)
            result['facebook'] = self.run_posting('facebook', material, social_pult_post, data, publish_date)

        if 'odnoklassniki' in post:
            data['text'] = post['odnoklassniki']['text']
            data['images'] = self.get_images(post['odnoklassniki']['images'], material)
            result['odnoklassniki'] = self.run_posting('odnoklassniki', material, social_pult_post, data, publish_date)

        if 'vkontakte' in post:
            data['text'] = post['vkontakte']['text']
            data['images'] = self.get_images(post['vkontakte']['images'], material)
            result['vkontakte'] = self.run_posting('vkontakte', material, social_pult_post, data, publish_date)

        result['ok'] = True
        result['material_id'] = material.id

        return JsonResponse(result)

publish_post = PublishView.as_view()

@ajax_request
def save_draft(request, material_id):
    """
    Сохранить черновик поста из редактора
    """

    material = BaseMaterial.objects.get(pk=material_id)
    data = request.POST['data']

    if hasattr(material, 'social_pult_draft'):
        draft = material.social_pult_draft
    else:
        draft = SocialPultDraft()

    draft.material = material
    draft.data = data
    draft.save()

    return {'ok': True, 'draft_id': draft.pk}


@ajax_request
def view_post(request, post_id):
    """
    Возвращает объект SocialPultPost и прогресс публикации по каждой сети
    """
    post = SocialPultPost.objects.get(pk=post_id)

    progress = {}
    for social_post in post.social_posts.all():
        progress[social_post.network] = {
            'social_post_id': social_post.id,
            'status': social_post.status,
            'task_id': social_post.task_id,
            'link': social_post.link,
            'error': social_post.error,
        }
        if social_post.status == 'scheduled' and social_post.scheduled_task:
            progress[social_post.network]['when'] = social_post.scheduled_task.when

    result = {
        'post_id': post.id,
        'text': post.text,
        'text_twitter': post.text_twitter,
        'selected_images': post.selected_images,
        'url': post.url,
        'progress': progress,
    }
    return result
