from django_extensions.management.jobs import WeeklyJob

from base.models import Task, CustomUser


class TaskClose(WeeklyJob):
    help = "task close weekly"

    def execute(self):
        # executing empty sample job
        root=CustomUser.objects.filter(is_superuser=True)[0]
        ch = Task.manager_task_state.chenge_status
        [ch(f,root,"C") for f in Task.obj.filter(status="S")]