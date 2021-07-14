# -*- coding: utf-8 -*-

"""Class-based view для создания нового участника"""

from irk.contests.views.base.participant_mixins import ParticipantBaseViewMixin


class CreateParticipantBaseView(ParticipantBaseViewMixin):
    """Class-based view для создания нового участника"""

    def get(self, request, *args, **kwargs):
        return super(CreateParticipantBaseView, self).get(request, self.get_model(request)())

    def post(self, request, *args, **kwargs):
        return super(CreateParticipantBaseView, self).post(request, self.get_model(request)())
