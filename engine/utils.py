# engine/utils.py
from rest_framework.response import Response
from celery import current_app
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.exceptions import InvalidChannelLayerError


def exception_handler(exc, context):
    return Response({'code': 1, 'msg': str(exc)}, status=400)


def stop_running_task(task_id):
    """停止任务：更新状态并尝试撤销 Celery 任务。"""
    from .models import Task

    task = Task.objects.filter(pk=task_id).first()
    if not task:
        return False

    if task.celery_task_id:
        current_app.control.revoke(task.celery_task_id, terminate=True)

    updated_fields = []
    if task.status in ("pending", "running"):
        task.status = "stopped"
        updated_fields.append('status')
    if not task.finished:
        task.finished = timezone.now()
        updated_fields.append('finished')

    if updated_fields:
        task.save(update_fields=updated_fields)
        try:
            channel_layer = get_channel_layer()
        except (InvalidChannelLayerError, ModuleNotFoundError, ImportError):
            channel_layer = None
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    f"task_{task.id}",
                    {'type': 'task_update', 'data': {'task_id': task.id, 'status': task.status}}
                )
            except Exception:
                pass

    return True
