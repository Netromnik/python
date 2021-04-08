from django.contrib.auth.models import AbstractUser, models
from django.utils.translation import gettext_lazy as _

from base.managers.group import GroupManager


class CustomGroup(models.Model):
    name = models.CharField(
        _('name'),
        max_length=128,
        unique=True,
    )
    description = models.CharField(
        _('description'),
        max_length=30,
        blank=True
    )
    obj = GroupManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Группа')
        verbose_name_plural = _('Группы')

from base.managers.user import UserModelCustomManeger

class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        CustomGroup,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="user_set",
        related_query_name="user",
    )
    support_q = UserModelCustomManeger()

    def get_wiki_collect(self):
        collect = self.support_q.get_collect(self)
        return collect

    def __str__(self):
        return self.first_name.capitalize() +" "+ self.last_name.capitalize()