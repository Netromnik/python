# coding=utf-8
from __future__ import unicode_literals

from mock import patch, Mock
import pytest

from user_agents import parse

from irk.adv import clickhouse as adv_clickhouse
from irk.adv.clickhouse import EventStream, ClickhouseUploader


@pytest.fixture
def encode():
    def _encode(data):
        return EventStream()._encode(data)
    return _encode


@pytest.fixture
def stream():
    return EventStream(redis=Mock())


@pytest.fixture
def uploader():
    return ClickhouseUploader(redis=Mock(), house=Mock())


def test_save_place_view(rf):
    request = rf.get('/some/request')

    with patch.object(adv_clickhouse, 'redis') as redis_mock:
        adv_clickhouse.save_place_view(1, request)

    # пуш в редис вызывался
    redis_mock.rpush.assert_called()


class TestEventStream:
    def test_place_view_data(self, rf, stream):
        request = rf.get('/some/request', HTTP_USER_AGENT='Mozilla/5.0')
        data = stream._place_view_data(100, request)

        # из данных реквеста формируется массив
        assert data['PlaceId'] == 100
        assert data['EventType'] == 1
        assert data['URL'].endswith('/some/request')
        assert data['UserAgent'] == 'Mozilla/5.0'

    def test_place_view_data_parsers(self, rf, stream):
        # данные по устройству парсятся и используются
        request = rf.get('/some/request', HTTP_USER_AGENT='Mozilla/5.0')
        request.user_agent = parse('Mozilla/5.0 (iPhone; CPU iPhone OS 13_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Mobile/15E148 Safari/604.1')
        data = stream._place_view_data(100, request)
        assert data['IsMobile'] == 1

    def test_limit_queue_size(self, stream):
        # если очередь имеет размер 200
        stream.redis.llen.return_value = 200

        # а допустимый размер - 100
        stream.QUEUE_MAX_SIZE = 100
        stream.QUEUE_LIMITER_FREQ = 0

        stream._limit_queue_size('some')

        # то очередь оставит только последние 100 элементов
        stream.redis.ltrim.assert_called_with('some', -100, -1)

    def test_redis_timeout(self, rf, stream):
        # тестируем ситуацию, когда редис не отвечает и происходит ошибка
        from redis import TimeoutError
        request = rf.get('/some/request')
        stream.redis.rpush.side_effect = TimeoutError("Timeout reading from socket")
        stream.push_place_view(1, request)
        # правильное поведение - не сохранился показ, вывелся warning в лог


class TestEncoder:
    def test_encode(self, encode):
        data = {'EventDate': 'xx', 'EventType': 'yy'}

        tsv, version = encode(data)
        assert len(tsv.split('\t')) == len(EventStream().keys())
        assert tsv.endswith('\n')
        assert 'xx' in tsv
        assert 'yy' in tsv

    def test_encode_dialect_applied(self, encode):
        # нехорошие данные нормально эскейпятся диалектом
        data = {'UserAgent': 'hello\nworld'}
        tsv, version = encode(data)
        assert 'hello\\\nworld' in tsv

    def test_encoder_unsupported_keys(self, encode):
        # если в массиве есть такие ключи, которые он не может закодировать,
        # то будет экзепшн
        with pytest.raises(ValueError):
            data = {'NonExistant': 'xx'}
            encode(data)


class TestUploader:
    """Тесты аплоадера через мок"""

    def test_should_work(self, uploader):
        # если у нас две строки данных
        uploader.redis.lrange.side_effect = [['row', 'row'], []]

        # то они загрузятся за раз
        uploader.upload(2)
        uploader.house.insert_bulk.assert_called_once()

    def test_should_upload_multiple_chunks(self, uploader):
        # если у нас три строки данных
        uploader.redis.lrange.side_effect = [['row', 'row'], ['row'], []]

        # а мы загружаем по две за раз
        uploader.upload(2)

        # то будет две отправки на бекенд
        assert uploader.house.insert_bulk.call_count == 2

    def test_should_ignore_small_reminder(self, uploader):
        # у нас 11 строк в редисе
        uploader.redis.lrange.side_effect = [['row']*10, ['row'], []]

        # загрузим десять, чтобы осталось меньше 20%
        uploader.upload(10)

        # загрузка вызывалась всего один раз, последняя строчка оставлена в базе
        # ждать, когда к ней добавится компания
        assert uploader.house.insert_bulk.call_count == 1

        # 10 первых значений удалено
        uploader.redis.ltrim.assert_called_with(uploader.key, 10, -1)


class TestUploaderRealRedis:
    """Тесты аплоадера на настоящем редисе"""

    @pytest.fixture
    def key(self):
        return 'test:event_queue'

    def test_should_just_work(self, key, redis):
        if not redis:
            pytest.skip('no real redis connection')

        uploader = ClickhouseUploader(redis, house=Mock())
        uploader.key = key

        # в редисе две строки, чанк тоже 2
        redis.rpush(key, '1', '2')
        uploader.upload(2)

        # выгрузит за раз, ничего не останется
        assert redis.llen(key) == 0
        assert uploader.house.insert_bulk.call_count == 1

    def test_should_do_multiple_calls(self, key, redis):
        if not redis:
            pytest.skip('no real redis connection')

        uploader = ClickhouseUploader(redis, house=Mock())
        uploader.key = key

        redis.rpush(key, '1', '2', '3')  # в редисе три строки
        uploader.upload(2)   # чанк - две

        # тоже выгрузит полностью, но за два раза
        assert redis.llen(key) == 0
        assert uploader.house.insert_bulk.call_count == 2

    def test_should_not_get_small_reminder(self, key, redis):
        if not redis:
            pytest.skip('no real redis connection')

        uploader = ClickhouseUploader(redis, house=Mock())
        uploader.key = key

        # в редисе шесть строк
        redis.rpush(key, '1', '2', '3', '4', '5', '6')
        uploader.upload(5)

        # одна останется
        assert redis.lrange(key, 0, -1) == ['6']
        assert uploader.house.insert_bulk.call_count == 1
