# 第三方 OpenAI API 快速启动指南

## 🎯 适用场景

如果你使用的是：
- ✅ OpenAI API 中转服务
- ✅ 第三方 API 代理
- ✅ 自建 OpenAI 兼容服务
- ✅ 其他 OpenAI 格式的 API 服务

这个指南将帮助你快速配置和使用。

## 📋 前置要求

1. 已安装 conda 环境 `browser-use-0.8.1`
2. 拥有第三方 API 的访问地址和 API Key

## 🚀 快速开始

### 步骤 1: 配置环境变量

编辑项目根目录的 `.env` 文件（不是 `browser-use-0.8.1` 子目录）：

```bash
# 第三方 API 地址（必须包含 /v1 后缀）
OPENAI_ENDPOINT=http://10.141.103.6:3000/v1

# 第三方 API Key
OPENAI_API_KEY=sk-vCPaIE40N0eiNiefEc154492516f4954A7E05741Ec5a32D9
```

**重要提示**：
- `OPENAI_ENDPOINT` 必须以 `/v1` 结尾
- 确保 API 地址可以访问（检查网络和防火墙）

### 步骤 2: 验证配置

运行测试脚本验证配置是否正确：

```bash
cd browser-use-0.8.1
python test_third_party_api.py
```

如果看到以下输出，说明配置成功：

```
============================================================
✅ 配置验证通过！
============================================================
```

### 步骤 3: 运行示例

直接运行模板文件：

```bash
python my_custom_template.py
```

或者运行第三方 API 专用示例：

```python
# 在 my_custom_template.py 中修改
if __name__ == '__main__':
    asyncio.run(example_third_party_openai())
```

## 📝 配置说明

### 完整配置示例

```python
from my_custom_template import Config, run_agent
import asyncio

async def main():
    config = Config()
    
    # LLM Provider 设置为 openai
    config.LLM_PROVIDER = 'openai'
    
    # 第三方 API 会自动从环境变量读取
    # 如果需要在代码中覆盖，可以这样设置：
    # config.OPENAI_ENDPOINT = 'http://your-api-endpoint/v1'
    # config.OPENAI_API_KEY = 'sk-your-key'
    
    # 模型名称（使用第三方支持的模型）
    config.OPENAI_MODEL = 'gpt-4.1-mini'
    
    # 任务描述
    config.TASK = 'Go to google.com and search for AI news'
    
    # 其他配置
    config.USE_VISION = True  # 启用视觉功能
    config.HEADLESS = False   # 显示浏览器窗口
    config.MAX_STEPS = 10     # 最大步骤数
    
    await run_agent(config)

asyncio.run(main())
```

### 支持的模型

根据你的第三方 API 服务支持的模型，可以使用：

```python
# OpenAI 官方模型
config.OPENAI_MODEL = 'gpt-4.1-mini'
config.OPENAI_MODEL = 'gpt-4.1'
config.OPENAI_MODEL = 'gpt-5-mini'
config.OPENAI_MODEL = 'o1-mini'
config.OPENAI_MODEL = 'o1-preview'

# 或者第三方服务支持的其他模型
config.OPENAI_MODEL = 'your-custom-model-name'
```

## 🔧 常见问题

### Q1: 连接超时或无法访问 API

**检查项**：
1. 确认 API 地址正确，包含 `/v1` 后缀
2. 检查网络连接，确保可以访问 API 地址
3. 检查防火墙设置
4. 尝试在浏览器访问 `http://your-api-endpoint/v1/models` 测试

**解决方法**：
```bash
# 测试 API 连接
curl http://10.141.103.6:3000/v1/models \
  -H "Authorization: Bearer sk-your-key"
```

### Q2: API Key 错误

**检查项**：
1. 确认 `.env` 文件在正确的位置（项目根目录）
2. 确认 API Key 格式正确
3. 确认 API Key 有效且未过期

**解决方法**：
```bash
# 查看环境变量是否加载
python -c "from dotenv import load_dotenv; import os; load_dotenv(dotenv_path='../.env'); print(os.getenv('OPENAI_API_KEY'))"
```

### Q3: 模型不存在错误

**原因**：第三方 API 不支持你指定的模型

**解决方法**：
1. 查看第三方 API 文档，确认支持的模型列表
2. 修改 `config.OPENAI_MODEL` 为支持的模型名称

### Q4: 如何查看详细日志

在 `.env` 文件中添加：

```env
BROWSER_USE_LOGGING_LEVEL=debug
BROWSER_USE_DEBUG_LOG_FILE=debug.log
```

### Q5: 第三方 API 和官方 API 有什么区别？

**相同点**：
- API 调用格式完全一致
- 支持相同的参数和功能
- 代码无需修改

**不同点**：
- API 地址不同（需要设置 `OPENAI_ENDPOINT`）
- 可能支持的模型列表不同
- 价格和限制可能不同

## 💡 最佳实践

### 1. 环境变量管理

推荐使用 `.env` 文件管理配置：

```env
# .env 文件
OPENAI_ENDPOINT=http://your-api-endpoint/v1
OPENAI_API_KEY=sk-your-key
```

不要在代码中硬编码 API Key。

### 2. 错误处理

添加适当的错误处理：

```python
async def main():
    config = Config()
    config.LLM_PROVIDER = 'openai'
    config.TASK = 'Your task here'
    
    try:
        result = await run_agent(config)
        print("✅ 任务完成:", result)
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        # 记录日志或发送通知
```

### 3. 测试流程

在正式使用前：
1. 先运行 `test_third_party_api.py` 验证配置
2. 使用简单任务测试（如搜索）
3. 逐步增加任务复杂度

### 4. 性能优化

```python
# 对于简单任务，可以禁用 Vision 加快速度
config.USE_VISION = False

# 启用快速模式
config.FLASH_MODE = True

# 减少最大步骤数
config.MAX_STEPS = 5
```

## 📚 相关文档

- [完整配置文档](README_TEMPLATE_CN.md)
- [模板文件](my_custom_template.py)
- [官方文档](https://docs.browser-use.com)

## 🆘 获取帮助

如果遇到问题：

1. 查看 [常见问题](#常见问题)
2. 运行 `test_third_party_api.py` 诊断配置
3. 查看详细日志（设置 `BROWSER_USE_LOGGING_LEVEL=debug`）
4. 检查第三方 API 服务状态

## ✅ 验证清单

在运行前，确保：

- [ ] `.env` 文件配置正确
- [ ] `OPENAI_ENDPOINT` 包含 `/v1` 后缀
- [ ] `OPENAI_API_KEY` 有效
- [ ] 网络可以访问 API 地址
- [ ] 已运行 `test_third_party_api.py` 验证
- [ ] conda 环境已激活

---

**祝你使用愉快！** 🚀

如有问题，欢迎查看完整文档或提交 Issue。
