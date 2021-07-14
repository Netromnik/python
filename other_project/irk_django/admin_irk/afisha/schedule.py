# -*- coding: utf-8 -*-


class ScheduleError(Exception):
    pass


class Schedule(object):
    """ Расписание объекта по какому либо критерию

        для событий может быть по
            - дням

        для гида:
            - дням
            - залу
    """

    def __init__(self, obj):
        self.sessions = []
        self.clarifies = None
        self.obj = obj

    def get_key(self, session):
        """ Возвращает ключ для группировки """
        idx = self.obj.pk if self.obj.pk else session.id
        return "%s_%s" % (idx, session.date.strftime("%y_%m_%d"))

    def append(self, session):
        if session.time is not None:
            if not any([s for s in self.sessions if s.time == session.time]):
                self.sessions.append(session)
            # else:
            #     raise ScheduleError()
        else:
            self.clarifies = session

    @property
    def first(self):
        """ Первый сеанс расписания """
        if self.sessions:
            return self.sessions[0]
        elif self.clarifies:
            return self.clarifies

    def __iter__(self):
        for session in self.sessions:
            yield session

    def __len__(self):
        return len(self.sessions)
