from django import forms
from django.contrib.admin.widgets import AdminDateWidget    #インポート
from .models import Tasks,Projects
import bootstrap_datepicker_plus as bootstrap_datepicker


 
class AddTaskForm(forms.ModelForm):
    """タスク追加フォーム"""
    class Meta:
        model = Tasks
        fields = ('project','taskName','status','createdDate','deadline','priority',)
        widgets = {
            'createdDate': AdminDateWidget(),    #インポートしたウィジェットを使う指示
            'deadline': AdminDateWidget(),
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(AddTaskForm, self).__init__(*args, **kwargs)
        print(user)
        self.fields['project'].queryset = Projects.objects.filter(owner=user)
        #self.fields['taskName'].queryset = Tasks.objects.filter(owner=user)
    
        
class AddProjectForm(forms.ModelForm):
    """タスク追加フォーム"""
    class Meta:
        model = Projects
        fields = ('Name','color',)
    

        widgets = {

        }

