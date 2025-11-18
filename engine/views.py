from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .models import Workflow, Task
from .tasks import enqueue_workflow
def index(request):
    if request.method == "POST":
        wf = Workflow.objects.create(
            name=request.POST["name"],
            strategy=request.POST.get("strategy", "round_robin"))
        task = Task.objects.create(workflow=wf, description=request.POST["desc"])
        # 预置 3 个 Agent
        wf.agents.create(name="PlannerBot", role="planner",
                         prompt_template="请把任务拆成 3 步：{description}")
        wf.agents.create(name="CoderBot", role="coder",
                         prompt_template="请写出 Python 代码实现：{description}")
        wf.agents.create(name="ReviewBot", role="reviewer",
                         prompt_template="请检查上述代码并给出意见，任务：{description}")
        enqueue_workflow(task)
        return redirect("engine:run_detail", task_id=task.id)   # 关键改动
    workflows = Workflow.objects.all()
    return render(request, "engine/index.html", {"workflows": workflows})

def run_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    msgs = task.message_set.select_related("agent").order_by("timestamp")
    return render(request, "engine/run_detail.html", {"task": task, "msgs": msgs})

def clear_all(request):
    if request.method == "POST":
        Workflow.objects.all().delete()   # 级联删除 Task、Message
        messages.success(request, "已清空全部工作流！")
    return redirect(reverse("engine:index"))
