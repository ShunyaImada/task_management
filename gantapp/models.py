from django.db import models


# Create your models here.
# Projectsと、その小モデルTasks
class Projects(models.Model):
    Name = models.CharField(max_length=100, verbose_name='project')
    def __str__(self):
        return f"{self.Name[:25]}"


CHOICE = (('high','high'),('midle','midle'),('low','low'))

class Tasks(models.Model):
    STATUS_LIST = ((0, '待機'), (1, '取組中'), (2, '完了'))

    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='project_task')
    taskName = models.CharField(max_length=100, verbose_name='タスク')
    status = models.IntegerField(choices=STATUS_LIST, verbose_name='状況')
    createdDate = models.DateTimeField(blank=True,null=True, verbose_name='開始日')
    deadline = models.DateTimeField(blank=True,null=True, verbose_name='締め切り')
    finishedDate = models.DateTimeField(blank=True,null=True, verbose_name='達成した日')
    priority = models.CharField(
        max_length=50,
        choices=CHOICE
        )
    #color = models.CharField(max_length=100, verbose_name='color');
    
    def __str__(self):
        return f"{self.taskName[:25]}"                                                                      