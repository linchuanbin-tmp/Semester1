# api_views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from .models import Workflow, Task, Message, Agent
from .serializers import *
from .tasks import enqueue_workflow
from .utils import stop_running_task
import uuid, os


# ---------------- 工作流 ----------------
class WorkflowListCreate(generics.ListCreateAPIView):
    queryset = Workflow.objects.all().prefetch_related('task_set')
    serializer_class = WorkflowSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wf = serializer.save()

        task = Task.objects.create(
            workflow=wf,
            description=request.data.get("description", "")
        )

        strategy = request.data.get("strategy", "single_agent")
        if strategy == "single_agent":
            Agent.objects.create(
                workflow=wf,
                name="SingleAgent",
                role="assistant",
                prompt_template="请根据以下任务描述直接给出完整回答：{description}"
            )
        elif strategy == "round_robin":
            Agent.objects.create(
                workflow=wf,
                name="Agent1",
                role="writer1",
                prompt_template=(
                    "你是第一段写作者，请根据任务描述写出第一部分内容。\n"
                    "任务描述：{description}\n"
                    "请直接开始写第一段，不要有任何额外解释。"
                )
            )
            Agent.objects.create(
                workflow=wf,
                name="Agent2",
                role="writer2",
                prompt_template=(
                    "你是第二段写作者，请继续完成任务描述，写第二段内容。\n"
                    "任务描述：{description}\n"
                    "前面已写内容：\n{context}\n"
                    "请接着上文写第二段，保持逻辑连贯、风格一致，不要重复前文。"
                )
            )
        elif strategy == "react_group":
            Agent.objects.create(
                workflow=wf,
                name="Thinker1",
                role="reactor1",
                prompt_template=(
                    "你是第一个智能体，请阅读任务描述并进行一步推理（Thought），"
                    "然后给出一个可执行的行动计划（Action）。\n"
                    "任务描述：{description}\n"
                    "请以以下格式输出：\nThought: ...\nAction: ..."
                )
            )
            Agent.objects.create(
                workflow=wf,
                name="Thinker2",
                role="reactor2",
                prompt_template=(
                    "你是第二个智能体。"
                    "你的目标是基于前一个智能体的Observation进行新的推理。\n\n"
                    "任务描述：{description}\n"
                    "前一位智能体的Observation：\n{context}\n\n"
                    "请输出你的Thought和Action。\n"
                    "不要重复Observation的内容。"
                )
            )
        elif strategy == "debate":
            Agent.objects.create(
                workflow=wf,
                name="ProAgent",
                role="debater_pro",
                prompt_template=(
                    "你支持该命题，请阐述正方观点并提供论据。\n"
                    "任务描述：{description}\n"
                    "请清晰表达正方立场。"
                )
            )
            Agent.objects.create(
                workflow=wf,
                name="ConAgent",
                role="debater_con",
                prompt_template=(
                    "你反对该命题，请阅读正方的发言并给出反驳。\n"
                    "任务描述：{description}\n"
                    "正方发言：\n{context}\n"
                    "指出逻辑漏洞、提供反例或反驳理由。"
                )
            )
            Agent.objects.create(
                workflow=wf,
                name="Judge",
                role="referee",
                prompt_template=(
                    "你是裁判，请根据正反双方的论述，总结辩论内容并给出最终裁决。\n"
                    "任务描述：{description}\n"
                    "辩论记录：\n{context}\n"
                    "输出最终结论与理由"
                )
            )

        Agent.objects.create(
            workflow=wf,
            name="User",
            role="user",
            prompt_template=""
        )

        enqueue_workflow(task)

        data = self.get_serializer(wf).data
        data['task_id'] = task.id
        return Response(data, status=status.HTTP_201_CREATED)


class WorkflowDelete(generics.DestroyAPIView):
    queryset = Workflow.objects.all()


# ---------------- 任务 ----------------
class TaskCreate(generics.CreateAPIView):
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        task = serializer.save(status='pending')
        enqueue_workflow(task)


class ContinueTask(generics.CreateAPIView):
    serializer_class = TaskSerializer

    def post(self, request, task_id):
        question = request.data.get("question")
        context = request.data.get("context", "")

        task = Task.objects.get(id=task_id)

        user_agent = Agent.objects.get(workflow=task.workflow, role="user")

        # 保存用户追问
        Message.objects.create(
            task=task,
            agent=user_agent,
            content=question
        )

        # 使用新问题覆盖 old description
        task.description = question
        task.status = "pending"
        task.save(update_fields=["description", "status"])

        enqueue_workflow(task)

        return Response({"task_id": task.id, "status": "continued"})


class TaskRetrieve(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskMessages(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(task_id=self.kwargs['pk']).select_related('agent').order_by('timestamp')


class TaskStop(generics.GenericAPIView):
    def post(self, request, pk):
        if stop_running_task(pk):
            return Response({'code': 0, 'msg': 'stop signal sent'})
        return Response({'code': 1, 'msg': 'task not found'}, status=404)


# ---------------- 文件 ----------------
@api_view(['POST'])
def upload_csv(request):
    file = request.FILES['file']
    name = f"{uuid.uuid4().hex}.csv"
    path = os.path.join('media', name)
    with open(path, 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    return Response({'code': 0, 'data': {'url': f'/media/{name}'}})


# ---------------- 鉴权（JWT 简化版） ----------------
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User


@api_view(['POST'])
def register(request):
    username = (request.data.get('username') or '').strip()
    password = (request.data.get('password') or '').strip()
    email = (request.data.get('email') or '').strip()

    if not username or not password:
        return Response({'code': 1, 'msg': 'username and password are required'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'code': 1, 'msg': 'username already exists'}, status=400)

    user = User.objects.create_user(username=username, password=password, email=email or '')
    refresh = RefreshToken.for_user(user)

    return Response({
        'code': 0,
        'data': {
            'token': str(refresh.access_token),
            'user': {'id': user.id, 'username': user.username}
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login(request):
    from django.contrib.auth import authenticate
    user = authenticate(username=request.data['username'],
                        password=request.data['password'])
    if not user:
        return Response({'code': 1, 'msg': 'invalid'}, status=400)
    refresh = RefreshToken.for_user(user)
    return Response({
        'code': 0,
        'data': {
            'token': str(refresh.access_token),
            'user': {'id': user.id, 'username': user.username}
        }
    })


class WorkflowRetrieve(RetrieveAPIView):
    queryset = Workflow.objects.all()  # 直接走默认查找
    serializer_class = WorkflowSerializer
