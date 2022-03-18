#from msilib.schema import ListView
#from re import L
import contextvars
import re
from urllib import request
from django.shortcuts import render
from django.urls import reverse_lazy
from .models import Projects ,Tasks
import plotly.figure_factory as ff
import plotly.graph_objects as go
import pandas as pd
from django.views.generic import ListView ,DetailView ,CreateView,DeleteView,UpdateView
from .models import Tasks
from bokeh.plotting import figure, output_file
from bokeh.embed import components
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models.tools import HoverTool
from bokeh.io import curdoc
from bokeh.themes import Theme


# Create your views here.
def task(request):
    tasks = Tasks.objects.all()
    df = []
    for task in tasks:
        df.append(
            dict(Task=task.taskName,
                 # create_ganttのStartとFinishで使うため、フォーマットを整形
                 Start="{0:%Y-%m-%d %H:%M:%S}".format(task.createdDate),
                 Finish="{0:%Y-%m-%d %H:%M:%S}".format(task.deadline),))
    fig = ff.create_gantt(df, title='これまでの軌跡', bar_width=0.5, showgrid_x=True, showgrid_y=False,)
    print(df)
    plot_fig = fig.to_html(fig, include_plotlyjs=False)

    return render(request, 'index.html', {'graph' : plot_fig})

def test(request):
    tasks = Tasks.objects.all()
    print(request)
    lists = []
    for task in tasks:
        lists.append(
            dict(Task=task.taskName,
                 # create_ganttのStartとFinishで使うため、フォーマットを整形
                 Start="{0:%Y-%m-%d}".format(task.createdDate),
                 End="{0:%Y-%m-%d}".format(task.deadline),
                 Color = 'green')
        )
    
    df = pd.DataFrame(columns=['Task','Start','End','Color'])
    for i,dat in enumerate(lists[::-1]):
        df.loc[i]=dat

    
    df['Start_dt']=pd.to_datetime(df.Start)
    df['End_dt']=pd.to_datetime(df.End)
    plot = figure(title='Project Schedule',x_axis_type='datetime',width=1200,height=700,y_range=df.Task.tolist(),x_range=Range1d(df.Start_dt.min(),df.End_dt.max()), tools='save')

    plot.xaxis.axis_label = 'whatever'
    plot.xaxis.major_label_text_font_size = "18pt"
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
    return render(request, 'base3.html', {'script': script, 'div': div})

    #return render(request, 'base2.html', {'script': script, 'div': div})


'''タスク詳細'''
class TodoList(ListView):
    template_name = 'list.html'
    model = Tasks

class Tododetail(DetailView):
    template_name = 'detail.html'
    model = Tasks

class TodoCreate(CreateView):
    template_name = 'create.html'
    model = Tasks
    fields = ('project','taskName','status','createdDate','deadline','finishedDate','priority')
    success_url = reverse_lazy('test5')
    
class TodoDelete(DeleteView):
    template_name = 'delete.html'
    model = Tasks
    success_url = reverse_lazy('test5')


class TodoUpdate(UpdateView):
    template_name = 'update.html'
    model = Tasks
    fields = ('project','taskName','status','createdDate','deadline','finishedDate','priority')
    success_url = reverse_lazy('test5')
    
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
    fields = ('Name',)
    success_url = reverse_lazy('test5')
    

class PJDelete(DeleteView):
    template_name = 'pjdelete.html'
    model = Projects
    success_url = reverse_lazy('pjlist')
    
class PJUpdate(UpdateView):
    template_name = 'pjupdate.html'
    model = Projects
    fields = ('Name',)
    success_url = reverse_lazy('pjlist')
    
    
class TestListView2(ListView):
    model = Tasks
    template_name = 'check2.html'
    
    def get_queryset(self):
        # デフォルトは全件取得
        results = self.model.objects.all()

        # GETのURLクエリパラメータを取得する(check2.htmlでクエリパラメータの設定)
        # 該当のクエリパラメータが存在しない場合は、[]が返ってくる
        q_kinds = self.request.GET.getlist('project')
        q_name = self.request.GET.get('taskName')

        if len(q_kinds) != 0:
            kinds = [x for x in q_kinds]
        #  print(kinds)
            results = results.filter(project__in=kinds)
            
        # 名前での絞り込み
        if q_name is not None:
            results = results.filter(taskName__contains=q_name)
    
        return results

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['project_list'] = Projects.objects.all
        
        print(context)
        
        #グラフの描画
        tasks = self.get_queryset()
       # tasks = tasks.filter(project__in=context)
        lists = []
        for task in tasks:
            lists.append(
                dict(Task=task.taskName,
                    # create_ganttのStartとFinishで使うため、フォーマットを整形
                    Start="{0:%Y-%m-%d}".format(task.createdDate),
                    End="{0:%Y-%m-%d}".format(task.deadline),
                    Color = 'green')
            )
        
        df = pd.DataFrame(columns=['Task','Start','End','Color'])
        for i,dat in enumerate(lists[::-1]):
            df.loc[i]=dat

        
        df['Start_dt']=pd.to_datetime(df.Start)
        df['End_dt']=pd.to_datetime(df.End)
        
        
        plot = figure(title='Project Schedule',x_axis_type='datetime',width=900,height=650,y_range=df.Task.tolist(),x_range=Range1d(df.Start_dt.min(),df.End_dt.max()), tools='save')

        plot.xaxis.major_label_text_font_size = "18pt"
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
        context['script']=script
        context['div']=div
        
        return context
    
    
class TestListView3(ListView):
    model = Tasks
    template_name = 'check2.html'
    
    
    
    def plotgantt(self):
        #グラフの描画
        tasks = self.get_queryset()
        lists = []
        color_dic = {1:'slategray'
                     ,2:'crimson'
                     ,3:'blue'
                     ,4:'mediumaquamarine'
                     ,5:'darkslategray'
                     ,6:'naby'
                     ,7:'forestgreen',
                     }
        for task in tasks:
            lists.append(
                dict(Task=task.taskName,
                    # create_ganttのStartとFinishで使うため、フォーマットを整形
                    Start="{0:%Y-%m-%d}".format(task.createdDate),
                    End="{0:%Y-%m-%d}".format(task.deadline),
                    Color = color_dic[task.project.id],
                    project_id = task.project.id
                    )
            )
        
        df = pd.DataFrame(columns=['Task','Start','End','Color'])
        for i,dat in enumerate(lists[::-1]):
            df.loc[i]=dat

        print(lists)
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
        
        if len(q_kinds) != 0:
            kinds = [x for x in q_kinds]
            results = results.filter(project__in=kinds)
        
        # 名前での絞り込み
        if q_name is not None:
            results = results.filter(taskName__contains=q_name)
        return results
    

       
