from django.urls import path
from . import api_views as views

app_name = 'engine_api'
urlpatterns = [
    # 工作流
    path('workflows', views.WorkflowListCreate.as_view()),               # 列表 + 新建
    path('workflows/<int:pk>/detail', views.WorkflowRetrieve.as_view()), # 查询单个
    path('workflows/<int:pk>', views.WorkflowDelete.as_view()),          # 删除

    # 任务
    path('tasks', views.TaskCreate.as_view(), name='task-create'),
    path('tasks/<int:task_id>/continue', views.ContinueTask.as_view()),
    path('tasks/<int:pk>', views.TaskRetrieve.as_view(), name='task-detail'),
    path('tasks/<int:pk>/messages', views.TaskMessages.as_view(), name='task-msgs'),
    path('tasks/<int:pk>/stop', views.TaskStop.as_view(), name='task-stop'),

    # 文件
    path('files', views.upload_csv, name='upload-csv'),

    # 鉴权
    path('auth/login', views.login, name='login'),
    path('auth/register', views.register, name='reg'),
]
