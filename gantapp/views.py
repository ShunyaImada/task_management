#from msilib.schema import ListView
#from re import L
import contextvars
import re
from urllib import request
from django.shortcuts import render
from django.urls import reverse_lazy
from .models import Projects ,Tasks
import pandas as pd
from django.views.generic import ListView ,DetailView ,CreateView,DeleteView,UpdateView
from .models import Tasks
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models.tools import HoverTool
from .forms import AddTaskForm


# Create your views here.

'''タスク'''
class Tododetail(DetailView):
    template_name = 'detail.html'
    model = Tasks

class TodoCreate(CreateView):
    template_name = 'create.html'
    model = Tasks
    form_class = AddTaskForm
    success_url = reverse_lazy('home')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AddTaskForm()
        print(context['form'])
        return context
    
    
    

    
class TodoDelete(DeleteView):
    template_name = 'delete.html'
    model = Tasks
    success_url = reverse_lazy('home')


class TodoUpdate(UpdateView):
    template_name = 'update.html'
    model = Tasks
    fields = ('project','taskName','status','createdDate','deadline','priority')
    success_url = reverse_lazy('home')
    
    '''
    form_class = UpdateTaskForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UpdateTaskForm#ここで定義した変数名
        return context
    '''
    
    
'''PJ'''
class PJList(ListView):
    template_name = 'pjlist.html'
    model = Projects
    
class PJdetail(DetailView):
    template_name = 'pjdetail.html'
    model = Projects
    
class PJCreate(CreateView):
    template_name = 'pjcreate.html'
    model = Projects
    fields = ('Name','color')
    success_url = reverse_lazy('home')
    

class PJDelete(DeleteView):
    template_name = 'pjdelete.html'
    model = Projects
    success_url = reverse_lazy('pjlist')
    
class PJUpdate(UpdateView):
    template_name = 'pjupdate.html'
    model = Projects
    fields = ('Name','color')
    success_url = reverse_lazy('pjlist')


'''Main'''
class TestListView3(ListView):
    model = Tasks
    template_name = 'home.html'
    
    def plotgantt(self):
        #グラフの描画
        tasks = self.get_queryset()
        print(len(tasks))
        if len(tasks) == 0:
            script = 'Null'
            div = 'Null'
            return script, div
        else:
            
            lists = []

            for task in tasks:
                lists.append(
                    dict(Task=task.taskName,
                        # create_ganttのStartとFinishで使うため、フォーマットを整形
                        Start="{0:%Y-%m-%d}".format(task.createdDate),
                        End="{0:%Y-%m-%d}".format(task.deadline),
                        Color = task.project.color,
                        project_id = task.project.id
                        )
                )
                
            print(lists)
            
            df = pd.DataFrame(columns=['Task','Start','End','Color'])
            print(df)
            
            for i,dat in enumerate(lists[::-1]):
                df.loc[i]=dat

            df['Start_dt']=pd.to_datetime(df.Start)
            df['End_dt']=pd.to_datetime(df.End)
            
            plot = figure(title='Project Schedule',x_axis_type='datetime',width=900,height=550,y_range=df.Task.tolist(),x_range=Range1d(df.Start_dt.min(),df.End_dt.max()), tools='save')
            
            plot.xaxis.major_label_text_font_size = "15pt"
            plot.yaxis.major_label_text_font_size = "15pt"
            
            hover=HoverTool(tooltips="Task: @Task<br>\
            Start: @Start<br>\
            End: @End")
            plot.add_tools(hover)
            
            df['ID']=df.index+0.3   # 数値調整 元は 0.8
            df['ID1']=df.index+0.7  # 数値調整 元は 1.2
            CDS=ColumnDataSource(df)
            plot.quad(left='Start_dt', right='End_dt', bottom='ID', top='ID1',source=CDS,color="Color")  
            
            script, div = components(plot)
            return script, div

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['project_list'] = Projects.objects.all
        
        script, div = self.plotgantt()
        
        context['script']=script
        context['div']=div
        
        return context
    
    
    def get_queryset(self):
        results = self.model.objects.all()
        q_kinds = self.request.GET.getlist('project')
        q_name = self.request.GET.get('taskName')
        sort1 = self.request.GET.get('sort1')
        sort2 = self.request.GET.get('sort2')
        if len(q_kinds) != 0:
            kinds = [x for x in q_kinds]
            results = results.filter(project__in=kinds)
            results = results.order_by(sort1,sort2)
        
        # 名前での絞り込み
        if q_name is not None:
            results = results.filter(taskName__contains=q_name)
        return results
    

       
