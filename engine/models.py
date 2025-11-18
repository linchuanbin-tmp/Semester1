from django.db import models

class Workflow(models.Model):
    name = models.CharField(max_length=100)
    strategy = models.CharField(max_length=50, default="round_robin")
    created = models.DateTimeField(auto_now_add=True)

class Agent(models.Model):
    ROLE_CHOICES = (("planner","Planner"),("coder","Coder"),("reviewer","Reviewer"))
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="agents")
    name = models.CharField(max_length=50)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    prompt_template = models.TextField()

class Task(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=20, default="pending")
    created = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True, blank=True)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

class Message(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
