# -*- coding: utf-8 -*-

from irk.contests.views.base.list import ListContestBaseView
from irk.contests.views.base.participant_create import CreateParticipantBaseView
from irk.contests.views.base.participant_create import CreateParticipantBaseView
from irk.contests.views.base.participant_read import ReadParticipantBaseView
from irk.contests.views.base.read import ReadContestBaseView

read = ReadContestBaseView.as_view(template_name='contests/read.html', by_csite=False)
index = ListContestBaseView.as_view(template_name='contests/list.html', by_csite=False)
participant = ReadParticipantBaseView.as_view(template_name='contests/participant/read.html', by_csite=False)
participant_create = CreateParticipantBaseView.as_view(template_dir='contests/participant/add', by_csite=False)
