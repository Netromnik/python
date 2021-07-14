# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import hashlib
import random

from irk.game.models import Prize, Purchase, Gamer, Treasure, Progress

class Game:

    gamer = None

    def __init__(self, user):
        if user.is_authenticated:
            self.gamer, _ = ExpandGamer.objects.get_or_create(user_id=user.pk)

    def prizes(self):
        if self.gamer:
            return ExpandPrize.set_gamer(self.gamer).objects.visible().order_by('price')
        else:
            return ExpandPrize.objects.visible().order_by('price')

    def purchases(self):
        return Purchase.objects.all().order_by('-created')

    def get_prize_obj(self, prize):
        prize_id = prize.pk if isinstance(prize, Prize) else prize
        return self.prizes().filter(pk=prize_id).first()

    def get_treasure_obj(self, treasure):
        treasure_id = treasure.pk if isinstance(treasure, Treasure) else treasure
        return Treasure.objects.filter(pk=treasure_id).first()

    def get_treasure_by_secret(self, secret):
        return Treasure.objects.filter(secret=secret, visible=True).first()

    def found_treasure(self, treasure):
        progress = Progress.objects.get_or_create(gamer_id=self.gamer.pk, treasure_id=treasure.pk)
        return progress

    def take_prize(self, prize):
        prize = self.get_prize_obj(prize)
        if prize.can_bay():
            code = random.randint(100000, 999999)
            purchase = Purchase.objects.get_or_create(gamer_id=self.gamer.pk, prize=prize, code=code)
            return purchase
        return False

    def is_treasure_found(self, treasure):
        return Progress.objects.for_gamer(self.gamer.pk).filter(treasure_id=treasure.pk).exists()

    def create_treasure_hash(self, treasure):
        return hashlib.sha1(''.join([str(self.gamer.user.pk), treasure.secret])).hexdigest()

    def check_treasure_hash(self, treasure, hash_):
        return hash_ == hashlib.sha1(''.join([str(self.gamer.user.pk), treasure.secret])).hexdigest()


class ExpandGamer(Gamer):

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'
        proxy = True

    def progress(self):
        return Progress.objects.for_gamer(self.pk)

    def taked_prize(self):
        purchase = Purchase.objects.for_gamer(self.pk).first()
        if purchase:
            return purchase.prize

    def prize_code(self):
        purchase = Purchase.objects.for_gamer(self.pk).first()
        if purchase:
            return purchase.code

    def balance(self):
        return Progress.objects.for_gamer(self.pk).count()

    def get_hint(self, treasure_id=None):
        found_treasure_ids = self.progress().values_list('treasure_id', flat=True)
        treasures = Treasure.objects.filter(visible=True).exclude(pk__in=found_treasure_ids).exclude(hint='')
        if treasure_id:
            treasures = treasures.exclude(pk=treasure_id)
        treasure = treasures.order_by('position', 'pk').first()
        if treasure:
            return treasure.hint
        return ''


class ExpandPrize(Prize):

    class Meta:
        verbose_name = 'Приз'
        verbose_name_plural = 'Призы'
        proxy = True

    @classmethod
    def set_gamer(cls, gamer):
        cls.gamer = gamer
        return cls

    def amount_left(self):
        return self.amount - Purchase.objects.filter(prize_id=self.pk).count()

    def is_in_stock(self):
        return bool(self.amount_left())

    def is_enough_tresuse(self):
        return self.price <= self.gamer.balance()

    def tresuse_left(self):
        left = self.price - self.gamer.balance()
        return left if left > 0 else 0

    def tresuse_to_next_prize(self):
        next_prize = Prize.objects.filter(price__gt=self.price).order_by('price').first()
        if next_prize:
            return next_prize.price - self.gamer.balance()
        return ''

    def can_bay(self):
        return self.amount_left() and self.is_in_stock() and self.is_enough_tresuse()
