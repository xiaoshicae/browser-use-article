# Browser-Use 最佳实践

browser-use 是一个让 AI Agent 控制浏览器的 Python 库，支持多种 LLM 模型。

## 快速开始

```python
import os
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'  # 避免代理影响 CDP 连接

from browser_use import Agent, BrowserSession, BrowserProfile, ChatOpenAI
import asyncio

async def main():
    browser = BrowserSession(
        browser_profile=BrowserProfile(
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            user_data_dir="~/.browser-use-chrome-profile",  # 保留登录状态
            headless=False,
        )
    )

    agent = Agent(
        task="你的任务描述",
        llm=ChatOpenAI(model="gpt-4o"),
        browser=browser,
    )

    result = await agent.run()
    print(result.final_result())

if __name__ == '__main__':
    asyncio.run(main())
```

## BrowserProfile 常用配置

```python
from browser_use import BrowserProfile
from browser_use.browser import ProxySettings

profile = BrowserProfile(
    # 浏览器路径
    executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # Mac
    # executable_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",  # Windows

    # 用户数据目录（保留 cookies、登录状态）
    user_data_dir="~/.browser-use-chrome-profile",

    # 无头模式
    headless=False,  # True=无界面运行，False=显示浏览器窗口

    # 性能优化
    minimum_wait_page_load_time=0.5,  # 页面加载最小等待时间
    wait_between_actions=0.3,  # 操作间等待时间

    # 安全设置
    disable_security=False,  # 是否禁用安全特性

    # 代理设置
    proxy=ProxySettings(
        server="http://proxy-server:8080",
        username="user",
        password="pass"
    ),

    # 视口大小
    viewport={"width": 1920, "height": 1080},

    # 录制视频（调试用）
    record_video_dir="./recordings",

    # 保持浏览器运行
    keep_alive=True,
)
```

## BrowserSession / BrowserProfile 参数详解

### 核心设置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `headless` | bool | `False` | 无头模式，不显示浏览器窗口 |
| `executable_path` | str | None | Chrome 可执行文件路径 |
| `cdp_url` | str | None | 连接到已运行的浏览器（Chrome DevTools Protocol） |

### 用户数据与会话持久化

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `user_data_dir` | str | None | 浏览器配置目录（保存 cookies、扩展、书签、缓存等），设为 `None` 启用隐身模式 |
| `profile_directory` | str | None | Chrome 配置子目录（如 `"Default"`, `"Profile 1"`） |
| `storage_state` | str/dict | None | 加载/保存 cookies 和 localStorage 的 JSON 文件路径或字典 |

**`user_data_dir` vs `storage_state` 区别**：

| 特性 | `user_data_dir` | `storage_state` |
|------|-----------------|-----------------|
| 存储内容 | 完整浏览器状态（cookies、扩展、书签、缓存、密码等） | 仅 cookies + localStorage |
| 存储格式 | 目录结构 | JSON 文件 |
| 适用场景 | 本地长期使用，需要稳定登录状态 | 跨机器共享，轻量级迁移 |
| 体积 | 较大 | 小 |

### 窗口与显示

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `window_size` | dict | None | 窗口尺寸 `{'width': 1024, 'height': 768}` |
| `window_position` | dict | None | 窗口位置 `{'x': 0, 'y': 0}` |
| `viewport` | dict | None | 视口尺寸（内容渲染区域），独立于窗口大小 |
| `no_viewport` | bool | False | 禁用视口模拟 |
| `device_scale_factor` | float | 1.0 | 设备像素比（高分屏设为 2.0） |

### 网络与代理

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `proxy` | ProxySettings | None | 代理设置，支持 `server`, `bypass`, `username`, `password` |

```python
from browser_use.browser import ProxySettings

proxy = ProxySettings(
    server="http://proxy-server:8080",
    bypass="localhost,127.0.0.1",  # 不走代理的地址
    username="user",
    password="pass"
)
```

### 浏览器行为

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `keep_alive` | bool | None | 任务完成后保持浏览器运行（调试时有用） |
| `allowed_domains` | list | None | 允许访问的域名白名单（支持通配符 `*.example.com`） |
| `prohibited_domains` | list | None | 禁止访问的域名黑名单 |
| `disable_security` | bool | True | 禁用安全特性（跨域限制等） |
| `enable_default_extensions` | bool | False | 启用默认自动化扩展 |
| `cross_origin_iframes` | bool | False | 支持跨域 iframe |
| `extra_chromium_args` | list | None | 额外的 Chrome 启动参数 |

```python
# 域名限制示例
BrowserProfile(
    allowed_domains=['*.google.com', 'https://github.com'],
    prohibited_domains=['*.ads.com', '*.tracking.net'],
)

# 额外启动参数示例
BrowserProfile(
    extra_chromium_args=[
        '--start-maximized',        # 最大化启动
        '--disable-notifications',  # 禁用通知
        '--mute-audio',             # 静音
    ],
)
```

### 性能调优

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `minimum_wait_page_load_time` | float | - | 页面加载最小等待时间（秒），减小可加速 |
| `wait_between_actions` | float | - | 操作之间的等待时间（秒），减小可加速 |

```python
# 快速执行配置
BrowserProfile(
    minimum_wait_page_load_time=0.1,  # 最小等待
    wait_between_actions=0.1,         # 快速操作
    headless=True,                    # 无 GUI 开销
)
```

### 录制与调试

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `record_video_dir` | Path/str | None | 录制视频保存目录，用于调试回放 |

### 云服务（Browser-Use Cloud）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `use_cloud` | bool | False | 使用 Browser-Use 云浏览器服务 |
| `cloud_profile_id` | str | None | 云端配置 ID |
| `cloud_proxy_country_code` | str | None | 代理国家代码（us, uk, fr, it, jp, au, de, fi, ca, in） |
| `cloud_timeout` | int | None | 会话超时时间（分钟），免费用户最长 15 分钟 |

```python
# 云服务配置示例
browser = Browser(
    use_cloud=True,
    cloud_profile_id='your-profile-id',
    cloud_proxy_country_code='us',
    cloud_timeout=30,
)
```

### Chrome 各平台路径参考

```python
# macOS
executable_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
user_data_dir = '~/Library/Application Support/Google/Chrome'

# Windows
executable_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
user_data_dir = '%LOCALAPPDATA%\\Google\\Chrome\\User Data'

# Linux
executable_path = '/usr/bin/google-chrome'
user_data_dir = '~/.config/google-chrome'
```

## Agent 高级配置

```python
from browser_use import Agent

agent = Agent(
    task="你的任务描述",
    llm=llm,
    browser=browser,

    # 视觉模式（使用截图分析页面）
    use_vision=True,

    # 执行限制
    max_steps=20,           # 最大执行步数
    step_timeout=120,       # 每步超时（秒）
    max_failures=3,         # 最大连续失败次数

    # 快速模式（禁用 LLM 思考输出）
    flash_mode=True,

    # 保存对话历史
    save_conversation_path='./conversation.json',

    # 扩展系统提示词
    extend_system_message="""
    额外指令：
    - 总是先检查页面是否加载完成
    - 遇到验证码时暂停等待用户处理
    """,
)
```

## 支持的 LLM 模型

```python
# OpenAI
from browser_use import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o")
llm = ChatOpenAI(model="gpt-5.2")

# Anthropic Claude
from browser_use import ChatAnthropic
llm = ChatAnthropic(model="claude-sonnet-4-20250514")

# Google Gemini
from browser_use import ChatGoogle
llm = ChatGoogle(model="gemini-2.0-flash")
llm = ChatGoogle(model="gemini-flash-lite-latest")  # 速度优化

# Groq (超快推理)
from browser_use import ChatGroq
llm = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct")

# Ollama (本地模型)
from browser_use import ChatOllama
llm = ChatOllama(model="llama3")

# Azure OpenAI
from browser_use import ChatAzureOpenAI
llm = ChatAzureOpenAI(model="gpt-4o", azure_endpoint="...")

# 阿里云 Qwen
from browser_use import ChatOpenAI
llm = ChatOpenAI(
    model='qwen-vl-max',
    api_key=os.getenv('ALIBABA_CLOUD'),
    base_url='https://dashscope-intl.aliyuncs.com/compatible-mode/v1'
)
```

## 自定义工具/动作

```python
from browser_use import Tools, Agent, BrowserSession

tools = Tools()

@tools.action(description='获取两步验证码')
async def get_2fa_code() -> str:
    # 你的实现
    code = input("请输入 2FA 验证码: ")
    return code

@tools.action(description='发送通知')
async def send_notification(message: str) -> str:
    print(f"通知: {message}")
    return "已发送"

agent = Agent(
    task="登录需要 2FA 的网站",
    llm=llm,
    browser=browser,
    tools=tools,  # 传入自定义工具
)
```

## 处理执行结果

```python
history = await agent.run()

# 常用方法
print(history.final_result())        # 最终结果
print(history.urls())                # 访问过的 URL 列表
print(history.is_successful())       # 是否成功完成
print(history.has_errors())          # 是否有错误
print(history.errors())              # 错误列表
print(history.number_of_steps())     # 执行步数
print(history.action_names())        # 执行的动作名称
print(history.extracted_content())   # 提取的内容
print(history.model_thoughts())      # Agent 的思考过程
```

## 速度优化配置

```python
# 1. 使用快速 LLM
from browser_use import ChatGroq
llm = ChatGroq(
    model='meta-llama/llama-4-maverick-17b-128e-instruct',
    temperature=0.0,
)

# 2. 优化浏览器配置
browser_profile = BrowserProfile(
    minimum_wait_page_load_time=0.1,
    wait_between_actions=0.1,
    headless=True,  # 无头模式更快
)

# 3. 启用快速模式
agent = Agent(
    task="...",
    llm=llm,
    browser_profile=browser_profile,
    flash_mode=True,  # 禁用思考输出
    extend_system_message="尽可能快速完成任务，使用多动作序列。",
)
```

## 常见问题解决

### 1. CDP 连接超时（代理问题）
```python
import os
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
```

### 2. 每次都要重新登录
```python
# 指定固定的用户数据目录
BrowserProfile(user_data_dir="~/.browser-use-chrome-profile")
```

### 3. 浏览器启动冲突
```bash
# 关闭所有 Chrome 进程后再运行
pkill -f "Google Chrome"
```

### 4. 使用已运行的 Chrome
```python
# 先启动 Chrome 开启调试端口
# /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

browser = BrowserSession(
    browser_profile=BrowserProfile(
        cdp_url="http://localhost:9222"
    )
)
```

### 5. 视觉模式不工作
```python
agent = Agent(
    task="...",
    llm=llm,
    use_vision=True,  # 确保开启
)
# 注意：需要支持视觉的模型（如 gpt-4o, claude-sonnet）
```

## 环境变量

```bash
# .env 文件
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GROQ_API_KEY=...

# 可选配置
BROWSER_USE_DISABLE_EXTENSIONS=0  # 是否禁用默认扩展
BROWSER_USE_SETUP_LOGGING=true    # 是否启用日志
```

## 项目结构建议

```
my-browser-agent/
├── .env                    # API 密钥
├── main.py                 # 主程序
├── tasks/                  # 任务定义
│   ├── login.py
│   └── scrape.py
├── tools/                  # 自定义工具
│   └── custom_actions.py
├── recordings/             # 视频录制（调试用）
└── conversations/          # 对话历史
```

## 参考链接

- 官方文档: https://docs.browser-use.com
- GitHub: https://github.com/browser-use/browser-use
- 云服务: https://cloud.browser-use.com