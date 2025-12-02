"""
==============================================
Browser-Use 自定义配置模板
==============================================

这个模板提供了完整的配置选项，让你可以灵活调整所有参数。

使用方法：
1. 在下面的配置区域修改你需要的参数
2. 运行: python my_custom_template.py
3. 或者在代码中导入并使用: from my_custom_template import run_agent

支持的功能：
✓ 多种 LLM Provider (OpenAI, Anthropic, Google, Groq, Ollama等)
✓ 自定义 System Prompt
✓ Vision 开关控制
✓ CDP URL 连接现有浏览器
✓ 浏览器配置（headless、代理等）
✓ 敏感数据过滤
✓ 自定义工具和函数
"""

import asyncio
import os
import sys
import json
import logging
import signal
import atexit
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# ============================================
# 日志配置
# ============================================

class AgentLogger:
    """Agent 运行日志记录器 - 捕获所有终端输出"""
    
    def __init__(self, log_dir: str = './logs', enable_json: bool = True, enable_console: bool = True):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成日志文件名（带时间戳）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.log_dir / f'agent_run_{timestamp}.log'
        self.json_log_file = self.log_dir / f'agent_run_{timestamp}.json'
        
        # 日志数据存储
        self.logs = []  # 存储所有日志条目
        self.enable_json = enable_json
        self.enable_console = enable_console
        self.start_time = datetime.now()
        
        # 配置 Python logging 并捕获所有输出
        self._setup_logging()
        
        print(f"📝 日志记录已启用")
        print(f"   - 文本日志: {self.log_file}")
        if enable_json:
            print(f"   - JSON日志: {self.json_log_file}")
    
    def _setup_logging(self):
        """配置 Python logging 并添加自定义 Handler 捕获所有日志"""
        
        # 创建自定义 Handler 来捕获日志到 JSON
        class JsonCaptureHandler(logging.Handler):
            def __init__(self, logger_instance):
                super().__init__()
                self.logger_instance = logger_instance
            
            def emit(self, record):
                try:
                    log_entry = {
                        'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                        'level': record.levelname,
                        'logger': record.name,
                        'message': record.getMessage(),
                        'module': record.module,
                        'function': record.funcName,
                        'line': record.lineno
                    }
                    
                    # 添加异常信息（如果有）
                    if record.exc_info:
                        log_entry['exception'] = self.format(record)
                    
                    self.logger_instance.logs.append(log_entry)
                except Exception:
                    pass  # 避免日志记录本身出错
        
        # 设置根日志级别
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8', mode='w'),
                logging.StreamHandler() if self.enable_console else logging.NullHandler(),
                JsonCaptureHandler(self)  # 添加 JSON 捕获 Handler
            ],
            force=True  # 强制重新配置
        )
        
        # 设置 browser-use 相关的日志级别
        logging.getLogger('browser_use').setLevel(logging.INFO)  # 改为 INFO 避免过多 DEBUG 信息
        logging.getLogger('playwright').setLevel(logging.WARNING)
        logging.getLogger('root').setLevel(logging.INFO)
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """记录自定义事件到 JSON 日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': 'EVENT',
            'logger': 'AgentLogger',
            'event_type': event_type,
            'message': f"Event: {event_type}",
            'data': data
        }
        self.logs.append(log_entry)
        # 同时写入标准日志
        logging.info(f"📌 Event: {event_type}")
    
    def save_json_logs(self):
        """保存 JSON 格式的日志（包含元数据和统计信息）"""
        if not self.enable_json:
            return
        
        try:
            # 计算统计信息
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            
            level_counts = {}
            event_counts = {}
            logger_counts = {}
            
            for log in self.logs:
                level = log.get('level', 'UNKNOWN')
                level_counts[level] = level_counts.get(level, 0) + 1
                
                if 'event_type' in log:
                    event_type = log['event_type']
                    event_counts[event_type] = event_counts.get(event_type, 0) + 1
                
                logger = log.get('logger', 'UNKNOWN')
                logger_counts[logger] = logger_counts.get(logger, 0) + 1
            
            # 构建完整的日志数据
            log_data = {
                'metadata': {
                    'start_time': self.start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_seconds': round(duration, 2),
                    'total_entries': len(self.logs),
                    'log_file': str(self.log_file),
                    'json_log_file': str(self.json_log_file)
                },
                'statistics': {
                    'by_level': level_counts,
                    'by_event_type': event_counts,
                    'by_logger': logger_counts
                },
                'logs': self.logs
            }
            
            with open(self.json_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ JSON 日志已保存: {self.json_log_file}")
            print(f"   📊 共 {len(self.logs)} 条日志，运行时长 {duration:.1f} 秒")
        except Exception as e:
            print(f"\n❌ 保存 JSON 日志失败: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """获取日志摘要"""
        level_counts = {}
        event_counts = {}
        
        for log in self.logs:
            level = log.get('level', 'UNKNOWN')
            level_counts[level] = level_counts.get(level, 0) + 1
            
            if 'event_type' in log:
                event_type = log['event_type']
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        duration = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'total_entries': len(self.logs),
            'duration_seconds': round(duration, 2),
            'by_level': level_counts,
            'by_event': event_counts,
            'log_file': str(self.log_file),
            'json_log_file': str(self.json_log_file) if self.enable_json else None
        }

# 全局日志记录器
_global_logger: Optional[AgentLogger] = None
_logs_saved: bool = False  # 标记日志是否已保存，避免重复

def get_logger() -> Optional[AgentLogger]:
    """获取全局日志记录器"""
    return _global_logger

def cleanup_and_save_logs():
    """清理并保存日志（程序退出时调用）"""
    global _logs_saved
    
    # 如果已经保存过，直接返回
    if _logs_saved:
        return
    
    if _global_logger:
        try:
            _global_logger.save_json_logs()
            summary = _global_logger.get_summary()
            print("\n" + "=" * 60)
            print("📊 运行摘要:")
            print(f"   ⏱️  运行时长: {summary['duration_seconds']:.1f} 秒")
            print(f"   📝 日志条目: {summary['total_entries']} 条")
            print(f"   📊 日志级别: {summary['by_level']}")
            if summary['by_event']:
                print(f"   🎯 事件类型: {summary['by_event']}")
            print(f"   📄 文本日志: {summary['log_file']}")
            if summary['json_log_file']:
                print(f"   📋 JSON日志: {summary['json_log_file']}")
            print("=" * 60)
            _logs_saved = True  # 标记已保存
        except Exception as e:
            print(f"⚠️  保存日志时出错: {e}")

def setup_signal_handler():
    """设置 Ctrl+C 信号处理器和退出处理器"""
    # 注册退出时的清理函数（适用于所有平台）
    atexit.register(cleanup_and_save_logs)
    
    # 尝试设置信号处理器（可能在某些平台上不工作）
    def signal_handler(sig, frame):
        print("\n\n⚠️  收到中断信号 (Ctrl+C)，正在保存日志...")
        cleanup_and_save_logs()
        sys.exit(0)
    
    try:
        signal.signal(signal.SIGINT, signal_handler)
        if sys.platform == 'win32':
            # Windows 特殊处理
            signal.signal(signal.SIGBREAK, signal_handler)
    except Exception as e:
        print(f"⚠️  无法设置信号处理器: {e}")

from browser_use import Agent, Browser, BrowserProfile, BrowserSession, Tools
from browser_use.llm import (
    ChatOpenAI,
    ChatAnthropic, 
    ChatGoogle,
    ChatGroq,
    ChatOllama,
    ChatAzureOpenAI,
    ChatBrowserUse,
)


# ============================================
# 配置区域 - 在这里修改你的参数
# ============================================

class Config:
    """所有配置参数的集中管理"""
    
    # ========== LLM Provider 配置 ==========
    # 选择你要使用的 LLM Provider: 'openai', 'anthropic', 'google', 'groq', 'ollama', 'azure', 'browser_use'
    LLM_PROVIDER: str = 'openai'
    
    # 各个 Provider 的 API Key (从环境变量读取，或直接在这里设置)
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    OPENAI_ENDPOINT: Optional[str] = os.getenv('OPENAI_ENDPOINT')  # 第三方 OpenAI API 地址
    ANTHROPIC_API_KEY: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
    GOOGLE_API_KEY: Optional[str] = os.getenv('GOOGLE_API_KEY')
    GROQ_API_KEY: Optional[str] = os.getenv('GROQ_API_KEY')
    AZURE_OPENAI_KEY: Optional[str] = os.getenv('AZURE_OPENAI_KEY')
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv('AZURE_OPENAI_ENDPOINT')
    BROWSER_USE_API_KEY: Optional[str] = os.getenv('BROWSER_USE_API_KEY')
    
    # ========== Model 配置 ==========
    # 每个 Provider 对应的模型名称
    OPENAI_MODEL: str = 'o3'  # 可选: gpt-4.1-mini, gpt-4.1, gpt-5-mini, o1-mini, o1-preview, deepseek-chat, qwen3-235b-a22b
    ANTHROPIC_MODEL: str = 'claude-sonnet-4-0'  # 可选: claude-sonnet-4-0, claude-opus-4-0
    GOOGLE_MODEL: str = 'gemini-flash-latest'  # 可选: gemini-flash-latest, gemini-pro-latest
    GROQ_MODEL: str = 'llama-3.3-70b-versatile'  # 可选: llama-3.3-70b-versatile, mixtral-8x7b-32768
    OLLAMA_MODEL: str = 'llama2'  # 本地 Ollama 模型
    AZURE_MODEL: str = 'gpt-4.1-mini'
    
    # LLM 参数
    TEMPERATURE: float = 0.1  # 0.0-2.0, 越低越确定性
    MAX_TOKENS: Optional[int] = None  # 最大生成 token 数
    
    # ========== Task 配置 ==========
    TASK: str = '''
# OA系统待办采集任务

## 任务目标
登录OA系统，筛选并采集"待办事宜"标签页中**属于需求类型**的待办项，生成需求汇总报告。

核心要求：只采集需求类待办项，非需求类跳过！

### 需求判断标准（满足任一条件即为需求）：
1. **标题关键词**：包含"需求"、"功能"、"开发"、"系统"、"平台"、"项目"、"应用"等
2. **发起人特征**：由业务部门/用户/客户提交（非IT内部流程）
3. **内容特征**：详情页包含"需求描述"、"功能说明"、"业务场景"、"用户故事"等
4. **排除项**：不包含"周报"、"工时"、"考勤"、"报销"、"请假"、"培训"、"通知"等非需求关键词

### 关键要求：
- 必须点击每条待办项进入详情页，通过标题+详情内容双重判断是否为需求
- 每判断一条记录到Memory：`已检查: [标题] - 是否需求: [是/否]`
- 只有确认为需求的才采集详细信息并记录：`已采集需求: [标题]`
- 关键标签页：大部分的信息离不开"待办事宜"标签页内的事项列表
- 文本驱动点击：先提取待办标题和索引，按文本匹配选择索引再点击
- 等待与重试：点击后等待3-5秒验证页面切换；每步最多重试3次

---

## 执行流程

### 步骤1：登录系统
访问地址：http://10.141.42.231:8080/

1.1 切换登录方式
- 如果看到二维码，点击切换到"账号密码登录"

1.2 填写登录信息
- 登录名：`04653`
- 密码：`dwzq1213**`
- 点击"登录"按钮，等待3秒

验证：页面显示"欢迎回来"或"门户导航"

---

### 步骤2：进入待办列表
- 点击页面右侧中的"待办"入口（旁边有"您有X条消息"字样）
- 等待2秒，确保跳转到待办列表新标签页面（标签页名为待办事宜）
- 记录待办总数到Memory

---

### 步骤3：逐条筛选与采集（核心 - 必须执行）

重要说明：
- 必须点击每条待办项进入详情页，通过"标题+详情内容"双重判断是否为需求
- 只采集确认为需求的待办项，非需求直接跳过
- 所有操作离不开"待办事宜"标签页的事项列表的循环执行：点击（会跳转到新标签页） → 判断 → 采集/跳过 → 返回

---

循环筛选与采集流程（对每条待办项重复执行）：

A. 点击待办项标题
- 在待办列表中，先提取下一条未检查的待办项标题（前20字符）
- 检查该标题是否在Memory['已检查']中
  - 如果已存在 → 跳过，继续下一条
  - 如果不存在 → 点击该待办项
- 等待3秒，确保进入详情页

B. 验证页面切换
```
提取当前页面完整标题
记录到Memory['正在检查: [标题]']，继续判断
```

C. 判断是否为需求（关键步骤）

C1. 提取判断信息
- 标题：页面顶部流程标题（完整）
- 发起人：查找"发起人"或"申请人"字段
- 内容关键词：提取页面主要内容的关键词（前100字）
- 流程类型：查找"类型"或"分类"字段

C2. 执行需求判断
根据你自己对详情页面的标题和页面内容来判断，其是否为某人/部门提交的需求，如果是需求则输出需求=是，否则输出需求=否，并给出判断依据/跳过原因

C3. 记录判断结果到Memory
```
Memory['已检查: [标题] - 需求: [是/否] - [判断依据/跳过原因]']
Memory['进度: 已检查 X/11 条']  
```

D. 采集需求详情（仅当判断为需求时执行）

如果 `是否需求 = True`，采集以下信息：
- 标题：完整流程标题
- 发起人：提交需求的人员/部门
- 发起时间：查找"创建时间"或"提交时间"字段
- 需求描述：概括主要内容（100-200字），重点提取需求要点
- 附件：是否有附件（有/无）
- 状态：当前流程状态（待处理/进行中/已完成等）

采集后记录到Memory：
```
Memory['已采集需求: [标题] - 发起人: [XXX] - 时间: [YYYY-MM-DD]']
```

如果 `是否需求 = False`，跳过采集，直接执行步骤E。

E. 返回待办事宜标签页（关键步骤）
- 回到之前打开的待办事宜标签页
- 等待3秒，确保返回到待办列表页面
- 验证页面标签名为"待办事宜"或显示待办列表

F. 继续下一条
- 在待办列表中点击下一条待办项
- 重复步骤A-F

完成条件：已检查数量 = 待办总数（包括需求和非需求）

---

### 步骤4：生成需求报告（必须执行 - 即使采集失败也要生成）

关键：无论采集成功多少条，都必须生成报告文件！

操作步骤：
1. 从Memory中整理所有"已采集需求"的数据
2. 统计"已检查"总数和"已采集需求"数量
3. 按照下面的格式生成 Markdown 内容
4. 调用 `write_file(file_name='oa_requirements_report.md', content='生成的内容')`
5. 验证文件已成功保存（查看工具返回消息中的 💾 标志）

报告格式：
```markdown
# OA系统待办需求汇总报告

采集时间：使用实际当前时间，格式：YYYY-MM-DD HH:MM:SS
待办总数：XX条  
需求数量：XX条  
筛选率：XX%（需求数/总数）

---

## 需求列表

| 序号 | 需求标题 | 发起人 | 发起时间 | 需求描述 | 附件 | 状态 |
|:----:|:---------|:-------|:---------|:---------|:----:|:-----|
| 1 | XX系统开发需求 | 张三/业务部 | 2025-01-15 | 需要开发XX功能，实现XX业务场景... | 有 | 待处理 |
| 2 | XX平台优化需求 | 李四/产品部 | 2025-01-14 | 优化XX模块性能，提升用户体验... | 无 | 进行中 |
| 3 | XX功能新增需求 | 王五/客户A | 2025-01-13 | 新增XX功能，支持XX操作... | 有 | 待处理 |

---

## 📊 统计分析

### 基本统计
- **待办总数**：XX条
- **需求数量**：XX条
- **非需求数量**：XX条（周报、工时、通知等）
- **筛选率**：XX%

### 需求分类
- **有附件需求**：X条
- **无附件需求**：X条


### 状态分布
- **待处理**：X条
- **进行中**：X条
- **已完成**：X条

---

## 🔍 筛选日志

### 已采集需求（XX条）
1. ✅ [需求标题1] - 发起人: XXX - 判断依据: 标题包含需求关键词
2. ✅ [需求标题2] - 发起人: XXX - 判断依据: 内容包含需求特征
...

### 已跳过非需求（XX条）
1. ❌ [周报标题] - 跳过原因: 非需求类流程
2. ❌ [工时标题] - 跳过原因: 非需求类流程
...

---

## 📝 备注
- 本报告由 Browser-Use Agent 自动生成
- 采集范围：OA系统 > 待办事宜 > 全部类型
- 筛选标准：标题+内容双重判断
- 数据来源：http://10.141.42.231:8080/
```
  '''
    
    # ========== System Prompt 配置 ==========
    # 扩展系统提示（在默认提示后添加）
    EXTEND_SYSTEM_MESSAGE: Optional[str] = None
    # 示例: 'IMPORTANT: Always be polite and explain your actions step by step.'
    
    # 完全覆盖系统提示（替换默认提示）
    OVERRIDE_SYSTEM_MESSAGE: Optional[str] = '用简体中文回答我的问题和任务，最后保存的文件里面也用简体中文'
    # 示例: 'You are a helpful assistant that automates web browsing tasks.'
    
    # ========== Vision 配置 ==========
    # 是否启用视觉功能（发送截图给 LLM）
    USE_VISION: bool = False
    
    # ========== Browser 配置 ==========
    # 是否使用无头模式（不显示浏览器窗口）
    HEADLESS: bool = False
    
    # 初始访问的URL（Agent启动时自动访问）
    INITIAL_URL: str = 'http://10.141.42.231:8080/'
    
    # 是否使用现有浏览器实例（通过 CDP）
    USE_EXISTING_BROWSER: bool = True
    
    # CDP URL (如果使用现有浏览器)
    # 启动 Chrome 命令: chrome --remote-debugging-port=9222
    CDP_URL: str = 'http://127.0.0.1:9222'
    
    # 是否使用 Browser-Use Cloud 浏览器
    USE_CLOUD_BROWSER: bool = False
    
    # 浏览器可执行文件路径（可选）
    EXECUTABLE_PATH: Optional[str] = None
    # Windows 示例: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    # Mac 示例: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    
    # 用户数据目录（保存 cookies、缓存等）
    USER_DATA_DIR: Optional[str] = None
    # 示例: './browser_data' 或 '~/Library/Application Support/Google/Chrome'
    
    # 配置文件目录
    PROFILE_DIRECTORY: Optional[str] = None
    # 示例: 'Default' 或 'Profile 1'
    
    # 允许访问的域名（安全限制）
    ALLOWED_DOMAINS: Optional[List[str]] = None
    # 示例: ['*google.com', 'github.com', 'stackoverflow.com']
    
    # 代理配置
    PROXY_SERVER: Optional[str] = None
    # 示例: 'http://proxy.example.com:8080'
    
    # ========== Agent 配置 ==========
    # 最大执行步骤数
    MAX_STEPS: int = 70
    STEP_TIMEOUT: int = 130  # 每步超时时间（秒），默认120
    
    # 是否启用快速模式（减少思考时间）
    FLASH_MODE: bool = False
    
    # 敏感数据过滤（防止敏感信息发送给 LLM）
    SENSITIVE_DATA: Optional[Dict[str, str]] = None
    # 示例: {'password': 'my_secret_pass', 'email': 'user@example.com'}
    
    # ========== 其他配置 ==========
    # 是否启用匿名遥测
    ANONYMIZED_TELEMETRY: bool = False
    
    # 是否启用默认浏览器扩展
    ENABLE_DEFAULT_EXTENSIONS: bool = True
    
    # ========== 文件保存配置 ==========
    # Agent 主动保存文件的路径（使用 FileSystem 保存）
    FILE_SYSTEM_PATH: Optional[str] = './agent_output'
    # 示例: './agent_output' 或 'D:/MyProjects/browser_data/files'
    # 文件会保存在: {FILE_SYSTEM_PATH}/browseruse_agent_data/
    
    # 浏览器下载文件的路径（用户点击下载按钮时）
    DOWNLOADS_PATH: Optional[str] = './downloads'
    # 示例: './downloads' 或 'D:/Downloads'
    
    # ========== 日志配置 ==========
    # 是否启用详细日志记录
    ENABLE_LOGGING: bool = True
    
    # 日志保存目录
    LOG_DIR: str = './logs'
    
    # 是否生成 JSON 格式的日志（用于问题分析）
    ENABLE_JSON_LOG: bool = True
    
    # 是否在控制台显示详细日志
    ENABLE_CONSOLE_LOG: bool = True


# ============================================
# LLM 初始化函数
# ============================================

def get_llm(config: Config):
    """根据配置返回对应的 LLM 实例"""
    
    provider = config.LLM_PROVIDER.lower()
    
    if provider == 'openai':
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set")
        
        # 构建 ChatOpenAI 参数
        openai_kwargs = {
            'model': config.OPENAI_MODEL,
            'api_key': config.OPENAI_API_KEY,
            'temperature': config.TEMPERATURE,
        }
        
        # 如果设置了自定义 endpoint（第三方 API），添加 base_url
        if config.OPENAI_ENDPOINT:
            openai_kwargs['base_url'] = config.OPENAI_ENDPOINT
        
        # 如果设置了 max_tokens
        if config.MAX_TOKENS:
            openai_kwargs['max_tokens'] = config.MAX_TOKENS
        
        return ChatOpenAI(**openai_kwargs)
    
    elif provider == 'anthropic':
        if not config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        return ChatAnthropic(
            model=config.ANTHROPIC_MODEL,
            api_key=config.ANTHROPIC_API_KEY,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
        )
    
    elif provider == 'google':
        if not config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set")
        return ChatGoogle(
            model=config.GOOGLE_MODEL,
            api_key=config.GOOGLE_API_KEY,
            temperature=config.TEMPERATURE,
        )
    
    elif provider == 'groq':
        if not config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set")
        return ChatGroq(
            model=config.GROQ_MODEL,
            api_key=config.GROQ_API_KEY,
            temperature=config.TEMPERATURE,
        )
    
    elif provider == 'ollama':
        return ChatOllama(
            model=config.OLLAMA_MODEL,
            temperature=config.TEMPERATURE,
        )
    
    elif provider == 'azure':
        if not config.AZURE_OPENAI_KEY or not config.AZURE_OPENAI_ENDPOINT:
            raise ValueError("AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT must be set")
        return ChatAzureOpenAI(
            model=config.AZURE_MODEL,
            api_key=config.AZURE_OPENAI_KEY,
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            temperature=config.TEMPERATURE,
        )
    
    elif provider == 'browser_use':
        if not config.BROWSER_USE_API_KEY:
            raise ValueError("BROWSER_USE_API_KEY is not set")
        return ChatBrowserUse(
            api_key=config.BROWSER_USE_API_KEY,
        )
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


# ============================================
# Browser 初始化函数
# ============================================

def get_browser(config: Config):
    """根据配置返回对应的 Browser 实例"""
    
    # 如果使用 Cloud Browser
    if config.USE_CLOUD_BROWSER:
        return Browser(use_cloud=True)
    
    # 如果使用现有浏览器（CDP）
    if config.USE_EXISTING_BROWSER:
        browser_session = BrowserSession(
            browser_profile=BrowserProfile(
                cdp_url=config.CDP_URL,
                is_local=True
            )
        )
        return browser_session
    
    # 标准浏览器配置
    browser_kwargs = {
        'headless': config.HEADLESS,
    }
    
    if config.EXECUTABLE_PATH:
        browser_kwargs['executable_path'] = config.EXECUTABLE_PATH
    
    if config.USER_DATA_DIR:
        browser_kwargs['user_data_dir'] = config.USER_DATA_DIR
    
    if config.PROFILE_DIRECTORY:
        browser_kwargs['profile_directory'] = config.PROFILE_DIRECTORY
    
    return Browser(**browser_kwargs)


# ============================================
# BrowserProfile 初始化函数
# ============================================

def get_browser_profile(config: Config):
    """根据配置返回 BrowserProfile 实例"""
    
    profile_kwargs = {
        'enable_default_extensions': config.ENABLE_DEFAULT_EXTENSIONS,
    }
    
    if config.ALLOWED_DOMAINS:
        profile_kwargs['allowed_domains'] = config.ALLOWED_DOMAINS
    
    if config.PROXY_SERVER:
        profile_kwargs['proxy_server'] = config.PROXY_SERVER
    
    # 添加下载路径配置
    if config.DOWNLOADS_PATH:
        profile_kwargs['downloads_path'] = config.DOWNLOADS_PATH
    
    return BrowserProfile(**profile_kwargs) if profile_kwargs else None


# ============================================
# Agent 运行函数
# ============================================

async def run_agent(config: Config = Config()):
    """
    运行 Browser-Use Agent
    
    Args:
        config: 配置对象，包含所有参数
    
    Returns:
        Agent 执行结果
    """
    
    global _global_logger
    
    # 初始化日志记录器
    if config.ENABLE_LOGGING:
        _global_logger = AgentLogger(
            log_dir=config.LOG_DIR,
            enable_json=config.ENABLE_JSON_LOG,
            enable_console=config.ENABLE_CONSOLE_LOG
        )
        # 设置 Ctrl+C 信号处理
        setup_signal_handler()
        
        # 记录配置信息
        _global_logger.log_event('config', {
            'llm_provider': config.LLM_PROVIDER,
            'model': config.OPENAI_MODEL if config.LLM_PROVIDER == 'openai' else 'other',
            'use_vision': config.USE_VISION,
            'max_steps': config.MAX_STEPS,
            'step_timeout': config.STEP_TIMEOUT,
            'task_preview': config.TASK[:200] + '...' if len(config.TASK) > 200 else config.TASK
        })
    
    # 设置环境变量
    if not config.ANONYMIZED_TELEMETRY:
        os.environ['ANONYMIZED_TELEMETRY'] = 'false'
    
    # 初始化 LLM
    print(f"🤖 初始化 LLM Provider: {config.LLM_PROVIDER}")
    llm = get_llm(config)
    
    # 初始化 Browser
    print(f"🌐 初始化浏览器...")
    browser = get_browser(config)
    
    # 初始化 BrowserProfile
    browser_profile = get_browser_profile(config)
    
    # 构建 Agent 参数
    agent_kwargs = {
        'task': config.TASK,
        'llm': llm,
        'use_vision': config.USE_VISION,
    }
    
    # 添加可选参数
    if config.EXTEND_SYSTEM_MESSAGE:
        agent_kwargs['extend_system_message'] = config.EXTEND_SYSTEM_MESSAGE
    
    if config.OVERRIDE_SYSTEM_MESSAGE:
        agent_kwargs['override_system_message'] = config.OVERRIDE_SYSTEM_MESSAGE
    
    if browser:
        if isinstance(browser, BrowserSession):
            agent_kwargs['browser_session'] = browser
        else:
            agent_kwargs['browser'] = browser
    
    if browser_profile:
        agent_kwargs['browser_profile'] = browser_profile
    
    if config.SENSITIVE_DATA:
        agent_kwargs['sensitive_data'] = config.SENSITIVE_DATA
    
    if config.FLASH_MODE:
        agent_kwargs['flash_mode'] = config.FLASH_MODE
    
    # 添加文件系统路径配置
    if config.FILE_SYSTEM_PATH:
        agent_kwargs['file_system_path'] = config.FILE_SYSTEM_PATH
    
    # 在 agent_kwargs 中添加
    if config.STEP_TIMEOUT:
        agent_kwargs['step_timeout'] = config.STEP_TIMEOUT

    # 创建 Agent
    print(f"🚀 创建 Agent...")
    if config.FILE_SYSTEM_PATH:
        print(f"📁 Agent 保存文件路径: {config.FILE_SYSTEM_PATH}/browseruse_agent_data/")
    if config.DOWNLOADS_PATH:
        print(f"💾 浏览器下载路径: {config.DOWNLOADS_PATH}")
    print(f"📝 任务: {config.TASK[:100]}..." if len(config.TASK) > 100 else f"📝 任务: {config.TASK}")
    print(f"👁️  Vision: {'启用' if config.USE_VISION else '禁用'}")
    print(f"⚡ Flash Mode: {'启用' if config.FLASH_MODE else '禁用'}")
    if config.ENABLE_LOGGING:
        print(f"📝 日志记录: 已启用 (JSON: {config.ENABLE_JSON_LOG})")
    print("-" * 60)
    
    if _global_logger:
        _global_logger.log_event('agent_created', {
            'agent_kwargs': {k: str(v)[:100] for k, v in agent_kwargs.items()}
        })
    
    agent = Agent(**agent_kwargs)
    
    # 运行 Agent
    print("▶️  开始执行任务...\n")
    
    try:
        if _global_logger:
            _global_logger.log_event('task_started', {'timestamp': datetime.now().isoformat()})
        
        result = await agent.run(max_steps=config.MAX_STEPS)
        
        if _global_logger:
            _global_logger.log_event('task_completed', {
                'success': True,
                'result_preview': str(result)[:500] if result else None
            })
    
    except Exception as e:
        if _global_logger:
            _global_logger.log_event('task_failed', {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'traceback': str(e)
            })
        raise
    
    print("\n" + "=" * 60)
    print("✅ 任务执行完成！")
    print("=" * 60)
    
    # 显示文件保存位置
    if config.FILE_SYSTEM_PATH:
        print(f"\n📁 Agent 保存的文件在: {config.FILE_SYSTEM_PATH}/browseruse_agent_data/")
    if config.DOWNLOADS_PATH:
        print(f"💾 下载的文件在: {config.DOWNLOADS_PATH}")
    
    # 注意：日志会在程序退出时自动保存（通过 atexit）
    # 但这里也可以手动保存一次，确保正常退出时能看到日志信息
    if _global_logger:
        cleanup_and_save_logs()
    
    return result


# ============================================
# 主函数
# ============================================

async def main():
    """主函数 - 使用自定义配置运行 Agent"""
    
    # 创建配置实例
    config = Config()
    
    # 你可以在这里覆盖配置
    # config.LLM_PROVIDER = 'anthropic'
    # config.TASK = 'Your custom task here'
    # config.USE_VISION = False
    
    # 运行 Agent
    try:
        result = await run_agent(config)
        return result
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        raise


# ============================================
# 快速配置示例
# ============================================

async def example_openai():
    """示例: 使用 OpenAI GPT-4"""
    config = Config()
    config.LLM_PROVIDER = 'openai'
    config.OPENAI_MODEL = 'gpt-5'
    config.TASK = 'Search Google for the latest AI news'
    config.USE_VISION = True
    config.HEADLESS = False
    await run_agent(config)


async def example_anthropic():
    """示例: 使用 Anthropic Claude"""
    config = Config()
    config.LLM_PROVIDER = 'anthropic'
    config.ANTHROPIC_MODEL = 'claude-sonnet-4-0'
    config.TASK = 'Go to GitHub and find the browser-use repository'
    config.USE_VISION = True
    await run_agent(config)


async def example_with_cdp():
    """示例: 连接现有浏览器（CDP）"""
    config = Config()
    config.LLM_PROVIDER = 'openai'
    config.USE_EXISTING_BROWSER = True
    config.CDP_URL = 'http://localhost:9222'
    config.TASK = 'Navigate to my already opened tabs and summarize them'
    await run_agent(config)


async def example_custom_prompt():
    """示例: 自定义 System Prompt"""
    config = Config()
    config.LLM_PROVIDER = 'openai'
    config.EXTEND_SYSTEM_MESSAGE = '''
    IMPORTANT RULES:
    1. Always explain what you are doing before each action
    2. Be extra careful with form submissions
    3. Take screenshots after important actions
    '''
    config.TASK = 'Fill out a contact form on example.com'
    await run_agent(config)


async def example_secure_mode():
    """示例: 安全模式（禁用 Vision + 敏感数据过滤）"""
    config = Config()
    config.LLM_PROVIDER = 'azure'
    config.USE_VISION = False  # 不发送截图
    config.SENSITIVE_DATA = {
        'company_name': 'MyCompany',
        'api_key': 'secret_key_123'
    }
    config.ALLOWED_DOMAINS = ['*.google.com', 'github.com']
    config.TASK = 'Search for information about company_name'
    await run_agent(config)


async def example_third_party_openai():
    """示例: 使用第三方 OpenAI API（如中转服务、代理等）"""
    config = Config()
    config.LLM_PROVIDER = 'openai'
    
    # 第三方 API 会自动从环境变量读取
    # OPENAI_ENDPOINT=http://your-api-endpoint/v1
    # OPENAI_API_KEY=your-api-key
    
    # 或者直接在这里设置
    # config.OPENAI_ENDPOINT = 'http://10.141.103.6:3000/v1'
    # config.OPENAI_API_KEY = 'sk-your-key'
    
    config.OPENAI_MODEL = 'gpt-5'  # 使用第三方支持的模型名称
    config.TASK = 'Go to google.com and search for "AI news"'
    config.USE_VISION = True
    config.HEADLESS = False
    
    await run_agent(config)


async def example_save_files():
    """示例: 提取网页内容并保存文件"""
    config = Config()
    config.LLM_PROVIDER = 'openai'
    config.OPENAI_MODEL = 'gpt-5'
    
    # 配置文件保存路径
    config.FILE_SYSTEM_PATH = './my_extracted_data'  # Agent 主动保存的文件
    config.DOWNLOADS_PATH = './my_downloads'  # 浏览器下载的文件
    
    config.TASK = '''
    1. 访问 https://news.ycombinator.com
    2. 提取首页前5条新闻的标题和链接
    3. 将结果保存到 hackernews.md 文件中，使用 Markdown 格式
    4. 格式如下：
       # Hacker News Top 5
       1. [标题](链接)
       2. [标题](链接)
       ...
    '''
    
    config.USE_VISION = True
    config.HEADLESS = False
    
    await run_agent(config)


# ============================================
# 程序入口
# ============================================

if __name__ == '__main__':
    # 运行主函数
    asyncio.run(main())
    
    # 或者运行示例
    # asyncio.run(example_openai())
    # asyncio.run(example_anthropic())
    # asyncio.run(example_with_cdp())
    # asyncio.run(example_custom_prompt())
    # asyncio.run(example_secure_mode())
    # asyncio.run(example_third_party_openai())  # 第三方 OpenAI API
    # asyncio.run(example_save_files())  # 文件保存示例
