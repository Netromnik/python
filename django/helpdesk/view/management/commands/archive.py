from django.core.management.base import BaseCommand
from fsm.models import Task
from datetime import datetime
import json

class Command(BaseCommand):
    help = 'Архивирования данных в json файл,с удалением заявок'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        date = datetime.now()
        if date.month < 2:
            q =Task.object.filter(data_create__year_lte=date.year-1)
        else:
            q =Task.object.filter(data_create__month__lte=date.month - 2)
        q.filter(state='Закрыта')
        with open(options['filename'][0], '+a') as outfile:
            json.dump(q, outfile)
        q.delete()
        print("Успешно записанно записанно {} строк".format(q.count()))
