#from msilib.schema import ListView
#from re import L
import contextvars
import re
from urllib import request
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from .models import Projects ,Tasks
import pandas as pd
from django.views.generic import ListView ,DetailView ,CreateView,DeleteView,UpdateView
from .models import Tasks
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models.tools import HoverTool
from .forms import AddTaskForm,AddProjectForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator



# Create your views here.

'''タスク'''
@method_decorator(login_required, name='dispatch')
class Tododetail(DetailView):
    template_name = 'gantapp/detail.html'
    model = Tasks

@method_decorator(login_required, name='dispatch')
class TodoCreate(CreateView):
    template_name = 'gantapp/create.html'
    model = Tasks
    form_class = AddTaskForm
    success_url = reverse_lazy('gantapp:home')
    
    def get_form_kwargs(self):
        kwargs = super(TodoCreate, self).get_form_kwargs()
        print(kwargs)
        kwargs['user'] = self.request.user
        print(kwargs)
        return kwargs

    def form_valid(self, form):
        post = form.save(commit=False)
        post.owner = self.request.user
        post.save()
        return redirect('gantapp:home')
    
    
    
    
    
    

@method_decorator(login_required, name='dispatch')  
class TodoDelete(DeleteView):
    template_name = 'gantapp/delete.html'
    model = Tasks
    success_url = reverse_lazy('gantapp:home')

@method_decorator(login_required, name='dispatch')
class TodoUpdate(UpdateView):
    template_name = 'gantapp/update.html'
    model = Tasks
    fields = ('project','taskName','status','createdDate','deadline','priority')
    success_url = reverse_lazy('gantapp:home')
    

    
    
'''PJ'''
@method_decorator(login_required, name='dispatch')
class PJList(ListView):
    template_name = 'gantapp/pjlist.html'
    model = Projects
    def get_queryset(self):
        results = self.model.objects.all()
        results = results.model.objects.filter(owner=self.request.user)
        return results

@method_decorator(login_required, name='dispatch')
class PJdetail(DetailView):
    template_name = 'gantapp/pjdetail.html'
    model = Projects

@method_decorator(login_required, name='dispatch')
class PJCreate(CreateView):
    template_name = 'gantapp/pjcreate.html'
    model = Projects
    form_class = AddProjectForm
    success_url = reverse_lazy('gantapp:home')
    def form_valid(self, form):
        post = form.save(commit=False)
        post.owner = self.request.user
        post.save()
        return redirect('gantapp:home')
    
    
@method_decorator(login_required, name='dispatch')
class PJDelete(DeleteView):
    template_name = 'gantapp/pjdelete.html'
    model = Projects
    success_url = reverse_lazy('gantapp:pjlist')

@method_decorator(login_required, name='dispatch')
class PJUpdate(UpdateView):
    template_name = 'gantapp/pjupdate.html'
    model = Projects
    fields = ('Name','color')
    success_url = reverse_lazy('gantapp:pjlist')


'''Main'''
@method_decorator(login_required, name='dispatch')
class TestListView3(ListView):
    model = Tasks
    template_name = 'gantapp/home.html'
    
    def plotgantt(self):
        #グラフの描画
        tasks = self.get_queryset()
        print(tasks)
        print(len(tasks))
        if len(tasks) == 0:
            script = 'データがありません。タスクを追加してください。'
            div = 'データがありません。タスクを追加してください。'
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
            
            plot = figure(title='Project Schedule',x_axis_type='datetime',width=900,height=500,y_range=df.Task.tolist(),x_range=Range1d(df.Start_dt.min(),df.End_dt.max()), tools='save')
            
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
        context['project_list'] = Projects.objects.filter(owner=self.request.user)
        
        script, div = self.plotgantt()
        
        context['script']=script
        context['div']=div
        
        return context
    
    
    def get_queryset(self):
        results = self.model.objects.all()
        results = results.model.objects.filter(owner=self.request.user)
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
    

       
