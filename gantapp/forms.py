from django import forms
from django.contrib.admin.widgets import AdminDateWidget    #インポート
from .models import Tasks,Projects


 
class AddTaskForm(forms.ModelForm):
    """タスク追加フォーム"""
    class Meta:
        model = Tasks
        fields = ('project','taskName','status','createdDate','deadline','priority',)
    

        widgets = {
            'createdDate': AdminDateWidget(),    #インポートしたウィジェットを使う指示
            'deadline': AdminDateWidget(),
        }
        
class AddProjectForm(forms.ModelForm):
    """タスク追加フォーム"""
    class Meta:
        model = Projects
        fields = ('Name','color',)
    

        widgets = {

        }

