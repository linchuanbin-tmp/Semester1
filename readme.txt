这是一个简单的项目介绍。本项目采用瀑布式流程开发，旨在完成一个“多 LLM Agent 协作系统”。

简单来说，Agent = 大语言模型 + 系统提示 + 工具（可选）+ 记忆
多 Agent = 把多个上述实体放进同一“群聊”或“拓扑图”，让它们通过消息传递共同解决一个复杂任务。

具体而言，当解决复杂问题时，可以选择使用多个 LLM Agent。以下是有待实现的多智能体协作策略：
1.Round-Robin：依次发言，“下家”接收并继续处理（第二阶段实现）
2.ReAct-Group：每个 Agent 先思考（Thought）再行动（Action），把结果发给下家（第二阶段实现）
3.Debate：两个 Agent 持相反观点，多轮辩论后由裁判 Agent 总结（第二阶段实现）

还要补充一个选项，当用户想要解决简单问题时，也可以选择使用单个LLM Agent。比如进行简单的查询等。（第一阶段部分实现）

//--------------------------------------------------------------------------------
瀑布式开发第一阶段的是做一份“可运行”的 Demo，这一部分我9月22号已经完成了，具体内容包括但不限于：
1.纯 Django（3.10+ Django 4.2）
2.零前端框架依赖，只用 Django 模板 + Bootstrap5 CDN
3.多 Agent 协作的完整流程（哪怕现在只使用了一个模型来伪装成多agent）
4.留好接口，后续把模板层换成 Vue 即可，后台业务逻辑（models/views/celery）基本上只需要进行增量开发。

瀑布式开发第一阶段的目录结构（仅列出部分关键文件）：
DjangoProject/
├── dagenthub/
│   ├── celery.py
│   ├── settings.py
│   └── urls.py
├── engine/
│   ├── models.py
│   ├── views.py
│   ├── tasks.py          # Celery 异步任务
│   ├── urls.py
│   └── templates/engine/
│       ├── base.html
│       ├── index.html
│       └── run_detail.html
└── manage.py

具体使用时，需要安装如下的模块（这部分建议没有学过的跟着ai的步骤来）：
安装
1、django==4.2.10
2、celery==5.3.4
3、openai==1.3.0
4、redis（window的话我会发文件夹到群里，linux或者mac自行安装5.0.14）
5、LM Studio（软件，装最新版就行，然后在里面下载）

安装完毕后，需要同时开启4个终端（第一次要开5个，这部分建议没有学过的跟着ai的步骤来）：
终端-1　Redis
    redis-server（Linux 可后台 systemctl；macOS brew services；window直接点我发的那个文件的exe版即可）。

终端-2　Celery Worker
    进入项目根目录
    source venv/bin/activate
    celery -A dagenthub worker -l info -Q celery
    必须常驻，负责执行 run_workflow 异步任务；关掉后任务会卡住。

终端-3　LLM studio
    搜索TinyLlama-1.1B-Chat-v1.0-GGUF，每次使用前打开就行

终端-4　首次部署需要初始化 Django（项目根目录搞一次就行）
    source venv/bin/activate
    python manage.py makemigrations   # 根据 models.py 生成 0001_initial.py
    python manage.py migrate          # 真正把表建到库里

终端-5　Django 开发服务器（后续第二阶段改成vue以后就不用开了，开vue那个就行）
    同样激活虚拟环境
    python manage.py runserver
    提供 Web 页面和接口；调试代码时经常需要 Ctrl-C 重起。

//--------------------------------------------------------------------------------
瀑布式开发第二阶段的是做完整，可上交的“多 LLM Agent 协作系统”，DDL是11.17，需要做的有：
1、写项目需求文档，项目设计文档（方便前后端分离开发，需要确定前后端分离接口测试工具等）。【我10.28-10.29来做，这部分划好分工】
2、把模板层换成 Vue：Django 只提供 REST API（django-rest-framework）。【待分工，有意向或者经验群里说】
3、增加更多策略（Debate、MetaGPT等）。【待分工，有意向或者经验群里说】
4、接入更多并且更好用的 LLM（OpenAI/Claude等）与工具（PythonREPL、搜索等）。【待分工，有意向或者经验群里说】
5、增加并丰富评估指标。【待分工，有意向或者经验群里说】
6、项目部署。【待分工，有意向或者经验群里说】


截止2025年11月10日，我目前已完成的功能有（其实已经勉强可以项目验收）：
1、写项目需求文档，项目设计文档
2、把模板层换成 Vue
3、增加一部分策略，并接入llm

瀑布式开发第二阶段的目录结构（仅列出部分关键文件）：
.                                   # 项目根
├── DjangoProject                         # Django 后端（可任意命名）
│   ├── dagenthub                   # 项目配置目录
│   │   ├── init.py
│   │   ├── asgi.py                 # WebSocket 入口
│   │   ├── celery.py               # Celery 实例
│   │   ├── settings.py             # 全局配置（含 CHANNEL_LAYERS / CELERY）
│   │   ├── urls.py                 # 总路由
│   │   └── wsgi.py
│   ├── engine                      # 业务 App
│   │   ├── api_views.py            # round-robin 逻辑
│   │   ├── consumers.py            # WebSocket 消费者
│   │   ├── models.py
│   │   ├── routing.py              # WebSocket 路由
│   │   ├── serializers.py
│   │   ├── tasks.py                # LLM 交替调用
│   │   ├── urls.py                 # 页面路由
│   │   ├── urls_api.py             # RESTful 路由
│   │   ├── utils.py
│   │   └── views.py                # 传统模板视图
│   ├── manage.py
│   ├── db.sqlite3                  # 开发库
│   └── readme.txt            # 你现在在这里！
└── frontend                        # Vite + Vue3 + TS
    ├── index.html
    ├── vite.config.ts              # 代理 /api 与 /ws
    ├── package.json
    ├── src
    │   ├── main.ts
    │   ├── App.vue
    │   ├── router.ts
    │   ├── store
    │   │   └── auth.ts
    │   ├── types
    │   │   ├── auth.ts
    │   │   └── workflow.ts
    │   ├── services
    │   │   ├── http.ts             # axios 拦截 
    │   │   ├── auth.ts
    │   │   └── workflows.ts        # 业务 AP
    │   ├── utils
    │   │   └── polling.ts          # 轮询封装
    │   └── views
    │       ├── LoginView.vue
    │       ├── RegisterView.vue
    │       ├── WorkflowListView.vue  
    │       ├── WorkflowCreateView.vue  
    │       └── WorkflowDetailView.vue  
    └── dist/                         # build 输出（git 忽略）


后续还要完成的工作：
4、后端完成剩下两个策略的增量开发
5、前端删掉“后端正在开发的标识”
6、前端看看要不要完成details功能，加一下管理员，还有完成注册功能，还要改mysql（非必须）
7、后端看看要不要加一下评估指标（非必须）
8、项目部署（非必须，不过我应该有时间做，13-17赶一赶）

使用上的话， 页面是http://localhost:3000，需要同时开启5个终端（第一次要开6个，这部分建议没有学过的跟着ai的步骤来）：
终端-1　Redis
    redis-server（Linux 可后台 systemctl；macOS brew services；window直接点我发的那个文件的exe版即可）。

终端-2　Celery Worker
    进入项目根目录
    source venv/bin/activate
    celery -A dagenthub worker -l info -Q celery
   windows ：celery -A dagenthub worker -l info -Q celery --pool=solo
    必须常驻，负责执行 run_workflow 异步任务；关掉后任务会卡住。

终端-3　LLM studio
    搜索meta-llama-3.1-8b-instruct，每次使用前打开就行（和第一阶段用的不一样，有独显的机子换成这个，没有就还是用第一阶段的就行）

终端-4　首次部署需要初始化 Django（项目根目录搞一次就行，后续不用开这个终端）
    source venv/bin/activate
    python manage.py makemigrations   # 根据 models.py 生成 0001_initial.py
    python manage.py migrate          # 真正把表建到库里

终端-5　Django 开发服务器（后续第二阶段改成vue以后就不用开了，开vue那个就行）
    同样激活虚拟环境
    python manage.py runserver
    提供 Web 页面和接口；调试代码时经常需要 Ctrl-C 重起。

终端-6  vue前端页面
    先进入前端目录：cd frontend
    如果还没装依赖，执行 npm install
    运行开发服务器：npm run dev。终端会打印本地访问地址（默认 http://localhost:3000）

//-----------------------截止11.17前，已完成上述提到的所有功能。
