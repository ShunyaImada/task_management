from xml.etree.ElementInclude import include
from django.urls import path , include
from .views import task ,test,TodoList,Tododetail,TodoCreate,TodoDelete,TodoUpdate,PJList,PJdetail,PJCreate,PJDelete,PJUpdate,TestListView2,TestListView3

urlpatterns = [
    path('gant/',task,name='gant'),
    path('test/',test,name='test'),
    path('list/', TodoList.as_view(),name='list'),
    path('detail/<int:pk>', Tododetail.as_view(),name='detail'),
    path('create/',TodoCreate.as_view(),name='create'),
    path('delete/<int:pk>',TodoDelete.as_view(),name='delete'),
    path('update/<int:pk>',TodoUpdate.as_view(),name='update'),
    path('pjlist/', PJList.as_view(),name='pjlist'),
    path('pjdetail/<int:pk>',PJdetail.as_view(),name='pjdetail'),
    path('pjcreate/',PJCreate.as_view(),name='pjcreate'),
    path('pjdelete/<int:pk>',PJDelete.as_view(),name='pjdelete'),
    path('pjupdate/<int:pk>',PJUpdate.as_view(),name='pjupdate'),
    path('test5/',TestListView3.as_view(),name = 'test5'),
]



