from rest_framework import serializers
from .models import Workflow, Task, Message


class WorkflowSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()
    latest_task_id = serializers.SerializerMethodField()
    latest_task_status = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = [
            'id', 'name', 'strategy', 'created',
            'status', 'task_count', 'latest_task_id', 'latest_task_status'
        ]

    def _get_latest_task(self, obj):
        cached = getattr(obj, '_latest_task', None)
        if cached is None:
            cached = obj.task_set.order_by('-created').first()
            obj._latest_task = cached
        return cached

    def get_status(self, obj):
        latest = self._get_latest_task(obj)
        return latest.status if latest else None

    def get_task_count(self, obj):
        return obj.task_set.count()

    def get_latest_task_id(self, obj):
        latest = self._get_latest_task(obj)
        return latest.id if latest else None

    def get_latest_task_status(self, obj):
        latest = self._get_latest_task(obj)
        return latest.status if latest else None


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    agent_role = serializers.CharField(source='agent.role', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'agent_name', 'agent_role', 'content', 'timestamp']
