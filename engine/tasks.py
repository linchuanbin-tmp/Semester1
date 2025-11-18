# engine/tasks.py
import openai
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.exceptions import InvalidChannelLayerError
from django.utils import timezone

# ---------- 客户端 ----------
# 1. LMStudio 本地
spark_client = openai.OpenAI(
    base_url="https://your api",
    api_key="your key"
)

# 2. 讯飞星辰
# spark_client = openai.OpenAI(
#   base_url = "https://your api",
#   api_key = "your key"
# )

spark_client1 = openai.OpenAI(
    base_url="https://your api",
    api_key="your key"
)

spark_client2 = openai.OpenAI(
    base_url="https://your api",
    api_key="your key"
)

MODEL_LMSTUDIO = "your model name"
MODEL_SPARK1 = "your model name"
MODEL_SPARK2 = "your model name"


def call_llm(prompt: str, llm_type: int = 0) -> str:
    if llm_type == 0:
        client = spark_client
        model = MODEL_LMSTUDIO
    elif llm_type == 1:
        client = spark_client1
        model = MODEL_SPARK1
    else:
        client = spark_client2
        model = MODEL_SPARK2
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[LLM 错误: {e}]"


def enqueue_workflow(task):
    """派发 Celery 任务并记录任务 ID。"""
    result = run_workflow.delay(task.id)
    task.celery_task_id = result.id
    task.save(update_fields=['celery_task_id'])
    return result


def _push_ws_event(group: str, event_type: str, data: dict):
    """向 WebSocket 群组广播消息（若 Channels 未配置则直接忽略）。"""
    try:
        channel_layer = get_channel_layer()
    except (InvalidChannelLayerError, ModuleNotFoundError, ImportError):
        return
    if not channel_layer:
        return
    try:
        async_to_sync(channel_layer.group_send)(group, {
            'type': event_type,
            'data': data,
        })
    except Exception:
        pass


@shared_task(bind=True)
def run_workflow(self, task_id):
    from .models import Task, Message, Agent

    try:
        task = Task.objects.select_related('workflow').get(pk=task_id)
    except Task.DoesNotExist:
        return

    group_name = f"task_{task_id}"
    task.status = "running"
    task.celery_task_id = self.request.id or task.celery_task_id
    task.save(update_fields=['status', 'celery_task_id'])
    _push_ws_event(group_name, 'task_update',
                   {'task_id': task_id, 'status': task.status})

    agents = list(Agent.objects.filter(workflow=task.workflow).exclude(role="user").order_by('id'))
    context = ""  # 累积上下文
    strategy = getattr(task.workflow, "strategy", "single_agent")

    try:
        if strategy in ("single_agent", "round_robin"):
            for idx, agent in enumerate(agents):
                if Task.objects.filter(pk=task_id, status="stopped").exists():
                    return

                prompt = agent.prompt_template.format(
                    description=task.description,
                    context=context
                )
                answer = call_llm(prompt, llm_type=(idx % 2))  # 奇数索引用讯飞
                message = Message.objects.create(task=task, agent=agent, content=answer)

                context += ("\n" + answer)

                _push_ws_event(group_name, 'send_message', {
                    'id': message.id,
                    'agent_name': agent.name,
                    'agent_role': agent.role,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat()
                })
        elif strategy == "react_group":
            context = ""
            for idx, agent in enumerate(agents):
                if Task.objects.filter(pk=task_id, status="stopped").exists():
                    return

                prompt = agent.prompt_template.format(
                    description=task.description,
                    context=context
                )
                # Thought + Action
                answer = call_llm(prompt, llm_type=idx % 3)
                message = Message.objects.create(task=task, agent=agent, content=answer)
                _push_ws_event(group_name, 'send_message', {
                    'id': message.id,
                    'agent_name': agent.name,
                    'agent_role': agent.role,
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat()
                })
                # Observation
                observation_prompt = (
                    f"根据以下思考与行动，给出简要的观察结果（Observation）：\n{answer}"
                )
                observation = call_llm(observation_prompt, llm_type=1)

                block = f"\n{agent.name}:\n{answer}\nObservation: {observation}"

                context += block

        elif strategy == "debate":
            # ProAgent / ConAgent / Judge
            agents_by_role = {a.role: a for a in agents}
            debate_log = ""

            # --- Round 1: ProAgent ---
            pro_agent = agents_by_role.get("debater_pro")
            if pro_agent:
                prompt = pro_agent.prompt_template.format(description=task.description)
                pro_answer = call_llm(prompt, llm_type=0)
                Message.objects.create(task=task, agent=pro_agent, content=pro_answer)
                debate_log += f"\n[Pro]\n{pro_answer}"
                _push_ws_event(group_name, 'send_message', {
                    'agent_name': pro_agent.name,
                    'agent_role': pro_agent.role,
                    'content': pro_answer,
                    'timestamp': timezone.now().isoformat()
                })

            # --- Round 2: ConAgent ---
            con_agent = agents_by_role.get("debater_con")
            if con_agent:
                prompt = con_agent.prompt_template.format(
                    description=task.description,
                    context=pro_answer
                )
                con_answer = call_llm(prompt, llm_type=2)
                Message.objects.create(task=task, agent=con_agent, content=con_answer)
                debate_log += f"\n[Con]\n{con_answer}"
                _push_ws_event(group_name, 'send_message', {
                    'agent_name': con_agent.name,
                    'agent_role': con_agent.role,
                    'content': con_answer,
                    'timestamp': timezone.now().isoformat()
                })

            # --- Round 3: Judge ---
            judge = agents_by_role.get("referee")
            if judge:
                prompt = judge.prompt_template.format(
                    description=task.description,
                    context=debate_log
                )
                judge_answer = call_llm(prompt, llm_type=1)
                Message.objects.create(task=task, agent=judge, content=judge_answer)
                _push_ws_event(group_name, 'send_message', {
                    'agent_name': judge.name,
                    'agent_role': judge.role,
                    'content': judge_answer,
                    'timestamp': timezone.now().isoformat()
                })

        else:
            # 未知策略
            Message.objects.create(
                task=task, content=f"[未知策略: {strategy}]"
            )
    except Exception:
        task.status = "failed"
        task.finished = timezone.now()
        task.save(update_fields=['status', 'finished'])
        _push_ws_event(group_name, 'task_update',
                       {'task_id': task_id, 'status': task.status})
        raise
    else:
        task.refresh_from_db(fields=['status'])
        if task.status != "stopped":
            task.status = "completed"
        task.finished = timezone.now()
        task.save(update_fields=['status', 'finished'])
        _push_ws_event(group_name, 'task_update',
                       {'task_id': task_id, 'status': task.status})
