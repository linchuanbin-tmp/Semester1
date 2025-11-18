# routing.py
from django.urls import re_path
from . import consumers

urlpatterns = [
    re_path(r'ws/tasks/(?P<task_id>\d+)/$', consumers.TaskConsumer.as_asgi()),
]