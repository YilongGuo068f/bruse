# Browser-Use 自定义模板使用指南

## 📋 目录
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用示例](#使用示例)
- [常见问题](#常见问题)

## 🚀 快速开始

### 1. 配置环境变量

创建 `.env` 文件（或使用现有的）：

```bash
# 复制示例文件
cp .env.example .env
```

在 `.env` 文件中添加你的 API Key：

```env
# OpenAI (官方)
OPENAI_API_KEY=sk-your-openai-key-here

# OpenAI (第三方 API / 中转服务)
OPENAI_ENDPOINT=http://your-api-endpoint/v1
OPENAI_API_KEY=sk-your-third-party-key-here

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Google Gemini
GOOGLE_API_KEY=your-google-api-key-here

# Browser Use Cloud
BROWSER_USE_API_KEY=your-browser-use-key-here
```

### 2. 运行模板

```bash
# 激活 conda 环境
conda activate browser-use-0.8.1

# 运行模板
python my_custom_template.py
```

## 🛠️ 配置选项

### 文件保存配置

```python
class Config:
    # Agent 主动保存文件的路径（使用 FileSystem）
    FILE_SYSTEM_PATH: Optional[str] = './agent_output'
    # 文件会保存在: {FILE_SYSTEM_PATH}/browseruse_agent_data/
    
    # 浏览器下载文件的路径
    DOWNLOADS_PATH: Optional[str] = './downloads'
```

**支持的文件类型**：
- ✅ Markdown (`.md`)
- ✅ 文本文件 (`.txt`)
- ✅ JSON (`.json`)
- ✅ CSV (`.csv`)
- ✅ PDF (`.pdf`)
- ❌ Word (`.docx`) - 使用 PDF 或 Markdown 代替
- ❌ Excel (`.xlsx`) - 使用 CSV 代替

## ⚙️ 配置说明

### LLM Provider 配置

在 `Config` 类中修改 `LLM_PROVIDER` 来选择你要使用的模型：

```python
class Config:
    # 可选值: 'openai', 'anthropic', 'google', 'groq', 'ollama', 'azure', 'browser_use'
    LLM_PROVIDER: str = 'openai'
```

### 支持的模型

#### OpenAI
```python
OPENAI_MODEL: str = 'gpt-4.1-mini'
# 可选: gpt-4.1-mini, gpt-4.1, gpt-5-mini, o1-mini, o1-preview
```

#### Anthropic Claude
```python
ANTHROPIC_MODEL: str = 'claude-sonnet-4-0'
# 可选: claude-sonnet-4-0, claude-opus-4-0
```

#### Google Gemini
```python
GOOGLE_MODEL: str = 'gemini-flash-latest'
# 可选: gemini-flash-latest, gemini-pro-latest
```

#### Groq
```python
GROQ_MODEL: str = 'llama-3.3-70b-versatile'
# 可选: llama-3.3-70b-versatile, mixtral-8x7b-32768
```

#### Ollama (本地)
```python
OLLAMA_MODEL: str = 'llama2'
# 使用你本地安装的任何模型
```

### 任务配置

```python
# 设置你要执行的任务
TASK: str = 'Go to google.com and search for "browser automation tools"'
```

### System Prompt 配置

有两种方式自定义 System Prompt：

#### 1. 扩展系统提示（推荐）
在默认提示后添加额外规则：

```python
EXTEND_SYSTEM_MESSAGE: str = '''
IMPORTANT RULES:
1. Always explain what you are doing before each action
2. Be extra careful with form submissions
3. Take screenshots after important actions
'''
```

#### 2. 完全覆盖系统提示
完全替换默认提示（谨慎使用）：

```python
OVERRIDE_SYSTEM_MESSAGE: str = '''
You are a helpful assistant that automates web browsing tasks.
Follow these rules:
- Be precise and efficient
- Always verify before submitting forms
- Report any errors immediately
'''
```

### Vision 配置

控制是否发送截图给 LLM：

```python
# 启用 Vision（发送截图）
USE_VISION: bool = True

# 禁用 Vision（不发送截图，更安全但功能受限）
USE_VISION: bool = False
```

### 浏览器配置

#### 基本配置

```python
# 无头模式（不显示浏览器窗口）
HEADLESS: bool = False

# 浏览器可执行文件路径
EXECUTABLE_PATH: str = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'

# 用户数据目录（保存 cookies 等）
USER_DATA_DIR: str = './browser_data'
```

#### 使用现有浏览器实例（CDP）

```python
# 启用 CDP 连接
USE_EXISTING_BROWSER: bool = True
CDP_URL: str = 'http://localhost:9222'
```

**启动 Chrome 的 CDP 调试端口：**

Windows:
```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

Mac:
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222
```

Linux:
```bash
google-chrome --remote-debugging-port=9222
```

#### 使用 Browser-Use Cloud

```python
USE_CLOUD_BROWSER: bool = True
```

### 安全配置

#### 域名白名单

```python
# 只允许访问特定域名
ALLOWED_DOMAINS: List[str] = ['*google.com', 'github.com', 'stackoverflow.com']
```

#### 敏感数据过滤

```python
# 防止敏感信息发送给 LLM
SENSITIVE_DATA: Dict[str, str] = {
    'password': 'my_secret_pass',
    'email': 'user@example.com',
    'api_key': 'secret_key_123'
}
```

在任务中使用占位符：
```python
TASK: str = 'Login with email and password'
```

#### 代理配置

```python
PROXY_SERVER: str = 'http://proxy.example.com:8080'
```

### Agent 配置

```python
# 最大执行步骤数
MAX_STEPS: int = 10

# 快速模式（减少思考时间）
FLASH_MODE: bool = False

# 温度参数（0.0-2.0，越低越确定性）
TEMPERATURE: float = 0.0
```

## 📚 使用示例

### 示例 1: 基本搜索任务

```python
async def main():
    config = Config()
    config.LLM_PROVIDER = 'openai'
    config.OPENAI_MODEL = 'gpt-4.1-mini'
    config.TASK = 'Search Google for the latest AI news and summarize the top 3 results'
    config.USE_VISION = True
    config.HEADLESS = False
    
    await run_agent(config)

asyncio.run(main())
```

### 示例 2: 使用 Claude 进行数据提取

```python
async def main():
    config = Config()
    config.LLM_PROVIDER = 'anthropic'
    config.ANTHROPIC_MODEL = 'claude-sonnet-4-0'
    config.TASK = 'Go to GitHub trending page and extract the top 5 repositories with their stars'
    config.MAX_STEPS = 15
    
    await run_agent(config)

asyncio.run(main())
```

### 示例 3: 连接现有浏览器

```python
async def main():
    config = Config()
    config.LLM_PROVIDER = 'openai'
    config.USE_EXISTING_BROWSER = True
    config.CDP_URL = 'http://localhost:9222'
    config.TASK = 'Check my Gmail inbox and tell me how many unread emails I have'
    
    await run_agent(config)

asyncio.run(main())
```

### 示例 4: 安全模式（企业级）

```python
async def main():
    config = Config()
    config.LLM_PROVIDER = 'azure'
    config.AZURE_MODEL = 'gpt-4.1-mini'
    
    # 禁用 Vision（不发送截图）
    config.USE_VISION = False
    
    # 设置敏感数据过滤
    config.SENSITIVE_DATA = {
        'company_name': 'MyCompany',
        'project_name': 'SecretProject'
    }
    
    # 限制访问域名
    config.ALLOWED_DOMAINS = ['*.internal.company.com', 'github.com']
    
    # 禁用遥测
    config.ANONYMIZED_TELEMETRY = False
    
    config.TASK = 'Search for information about company_name project_name'
    
    await run_agent(config)

asyncio.run(main())
```

### 示例 5: 自定义 System Prompt

```python
async def main():
    config = Config()
    config.LLM_PROVIDER = 'openai'
    
    config.EXTEND_SYSTEM_MESSAGE = '''
    CRITICAL RULES:
    1. Before clicking any button, always read and confirm the button text
    2. Never submit forms without explicit confirmation
    3. Take a screenshot after each major action
    4. If you encounter a CAPTCHA, stop and report it
    5. Always verify URLs before navigating
    '''
    
    config.TASK = 'Go to example.com and fill out the contact form'
    
    await run_agent(config)

asyncio.run(main())
```

### 示例 6: 使用本地 Ollama

```python
async def main():
    config = Config()
    config.LLM_PROVIDER = 'ollama'
    config.OLLAMA_MODEL = 'llama2'  # 或你安装的其他模型
    config.TASK = 'Search DuckDuckGo for Python tutorials'
    config.HEADLESS = True
    
    await run_agent(config)

asyncio.run(main())
```

### 示例 7: 多步骤复杂任务

```python
async def main():
    config = Config()
    config.LLM_PROVIDER = 'anthropic'
    config.ANTHROPIC_MODEL = 'claude-sonnet-4-0'
    
    config.TASK = '''
    1. Go to GitHub
    2. Search for "browser automation" repositories
    3. Sort by stars
    4. Extract the top 5 repositories with:
       - Repository name
       - Stars count
       - Description
       - Last update date
    5. Save the results in a formatted list
    '''
    
    config.MAX_STEPS = 20
    config.USE_VISION = True
    
    await run_agent(config)

asyncio.run(main())
```

### 示例 8: 使用第三方 OpenAI API（中转服务）

```python
async def main():
    config = Config()
    config.LLM_PROVIDER = 'openai'
    
    # 第三方 API 配置会自动从 .env 文件读取
    # OPENAI_ENDPOINT=http://10.141.103.6:3000/v1
    # OPENAI_API_KEY=sk-your-key
    
    config.OPENAI_MODEL = 'gpt-4.1-mini'
    config.TASK = 'Search Google for latest AI developments'
    config.USE_VISION = True
    config.HEADLESS = False
    
    await run_agent(config)

asyncio.run(main())
```

**说明**：
- 适用于使用第三方 OpenAI API 中转服务、代理或自建服务
- 只需在 `.env` 中设置 `OPENAI_ENDPOINT` 即可
- API 调用规范与 OpenAI 官方完全一致
- 支持所有 OpenAI 兼容的模型

## 🔧 常见问题

### Q1: 如何查看浏览器操作过程？

```python
config.HEADLESS = False  # 设置为 False 可以看到浏览器窗口
```

### Q2: 任务执行太慢怎么办？

```python
config.FLASH_MODE = True  # 启用快速模式
config.USE_VISION = False  # 禁用 Vision 可以加快速度
```

### Q3: 如何保存浏览器状态（cookies 等）？

```python
config.USER_DATA_DIR = './browser_data'  # 指定用户数据目录
```

### Q4: 如何使用代理？

```python
config.PROXY_SERVER = 'http://proxy.example.com:8080'
```

### Q5: API Key 错误怎么办？

确保：
1. `.env` 文件在项目根目录
2. API Key 格式正确
3. 已经运行 `load_dotenv()`

### Q6: 如何调试错误？

```python
# 在 .env 文件中设置
BROWSER_USE_LOGGING_LEVEL=debug
BROWSER_USE_DEBUG_LOG_FILE=debug.log
```

### Q7: 如何限制 Agent 的访问权限？

```python
config.ALLOWED_DOMAINS = ['*.safe-domain.com']  # 白名单
config.SENSITIVE_DATA = {'key': 'value'}  # 敏感数据过滤
config.USE_VISION = False  # 禁用截图
```

### Q8: 支持哪些浏览器？

目前主要支持：
- Chromium
- Google Chrome
- Microsoft Edge

### Q9: 如何使用自己已登录的浏览器？

使用 CDP 方式连接：
```python
config.USE_EXISTING_BROWSER = True
config.CDP_URL = 'http://localhost:9222'
```

或者指定用户数据目录：
```python
config.USER_DATA_DIR = '~/Library/Application Support/Google/Chrome'
config.PROFILE_DIRECTORY = 'Default'
```

### Q10: 如何获取 API Key？

- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Google**: https://makersuite.google.com/app/apikey
- **Browser Use Cloud**: https://cloud.browser-use.com/dashboard/api

## 📖 更多资源

- [官方文档](https://docs.browser-use.com)
- [GitHub 仓库](https://github.com/browser-use/browser-use)
- [示例代码](https://github.com/browser-use/browser-use/tree/main/examples)
- [Discord 社区](https://link.browser-use.com/discord)

## 💡 提示

1. **从简单任务开始**：先测试简单的搜索任务，确保配置正确
2. **逐步增加复杂度**：任务复杂度逐步提升
3. **使用 Vision**：对于复杂页面，Vision 功能很有帮助
4. **调整 MAX_STEPS**：复杂任务需要更多步骤
5. **查看日志**：遇到问题时查看详细日志
6. **安全第一**：处理敏感信息时使用安全配置

## 🎯 最佳实践

1. **任务描述要清晰**：明确告诉 Agent 要做什么
2. **设置合理的步骤限制**：避免无限循环
3. **使用环境变量**：不要在代码中硬编码 API Key
4. **测试环境先试**：在生产环境前先测试
5. **监控执行过程**：使用非 headless 模式观察
6. **处理异常**：添加 try-except 错误处理
7. **保存重要数据**：及时保存 Agent 的输出结果

---

**祝你使用愉快！如有问题，欢迎查看文档或加入社区讨论。** 🚀
