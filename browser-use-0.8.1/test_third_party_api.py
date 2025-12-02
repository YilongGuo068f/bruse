"""
测试第三方 OpenAI API 配置

这个脚本直接使用 HTTP 请求验证 API 是否可用
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(dotenv_path='../.env')

print("=" * 60)
print("第三方 OpenAI API 配置测试")
print("=" * 60)

# 检查环境变量
openai_endpoint = os.getenv('OPENAI_ENDPOINT')
openai_api_key = os.getenv('OPENAI_API_KEY')

print("\n📋 环境变量检查:")
print(f"✓ OPENAI_ENDPOINT: {openai_endpoint if openai_endpoint else '❌ 未设置'}")
print(f"✓ OPENAI_API_KEY: {'已设置 (' + openai_api_key[:20] + '...)' if openai_api_key else '❌ 未设置'}")

if not openai_endpoint or not openai_api_key:
    print("\n❌ 错误: 环境变量未正确设置")
    print("\n请确保 .env 文件包含:")
    print("OPENAI_ENDPOINT=http://your-api-endpoint/v1")
    print("OPENAI_API_KEY=sk-your-api-key")
    sys.exit(1)

# 🔥 直接用 HTTP 请求测试 API（模拟 curl）
print("\n📡 发送 HTTP 请求到 API...")
print(f"   目标地址: {openai_endpoint}/chat/completions")

# 构建请求 URL
api_url = openai_endpoint.rstrip('/') + '/chat/completions'

# 构建请求头
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_api_key}"
}

# 构建请求体（和 curl 命令一致）
payload = {
    "model": "o3",  # 改模型
    "messages": [
        {
            "role": "user",
            "content": "你是什么模型，什么型号，你可以识别图片么"
        }
    ]
}

print(f"   使用模型: {payload['model']}")
print(f"   测试消息: {payload['messages'][0]['content']}")
print("\n   (等待响应...)")

try:
    # 发送请求（设置超时时间）
    response = requests.post(
        api_url,
        headers=headers,
        json=payload,
        timeout=30  # 30秒超时
    )
    
    # 检查 HTTP 状态码
    print(f"\n✅ 收到响应!")
    print(f"   HTTP 状态码: {response.status_code}")
    
    if response.status_code == 200:
        # 解析 JSON 响应
        try:
            result = response.json()
            
            # 提取 AI 回复内容
            if 'choices' in result and len(result['choices']) > 0:
                ai_message = result['choices'][0]['message']['content']
                print(f"\n📨 API 响应内容:")
                print(f"   {ai_message}")
                
                # 显示更多信息
                if 'usage' in result:
                    usage = result['usage']
                    print(f"\n📊 Token 使用情况:")
                    print(f"   - 输入 tokens: {usage.get('prompt_tokens', 'N/A')}")
                    print(f"   - 输出 tokens: {usage.get('completion_tokens', 'N/A')}")
                    print(f"   - 总计 tokens: {usage.get('total_tokens', 'N/A')}")
                
                print("\n" + "=" * 60)
                print("✅ 完整配置验证通过！")
                print("=" * 60)
                print("\n🎉 你的 API 配置完全正常，可以开始使用了！")
                
            else:
                print(f"\n⚠️  警告: 响应格式异常")
                print(f"   完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
        except json.JSONDecodeError:
            print(f"\n❌ 无法解析 JSON 响应")
            print(f"   原始响应: {response.text[:500]}")
            sys.exit(1)
    
    else:
        # 非 200 状态码
        print(f"\n❌ API 返回错误状态码: {response.status_code}")
        print(f"   错误信息: {response.text[:500]}")
        print("\n可能的原因:")
        if response.status_code == 401:
            print("  - API key 无效或已过期")
        elif response.status_code == 404:
            print("  - API endpoint 地址不正确")
            print("  - 模型名称可能不正确")
        elif response.status_code == 429:
            print("  - 请求过于频繁，触发限流")
        elif response.status_code >= 500:
            print("  - API 服务器内部错误")
        else:
            print("  - 请检查 API 配置和网络连接")
        sys.exit(1)

except requests.exceptions.Timeout:
    print(f"\n❌ 请求超时!")
    print(f"   API 服务器响应时间过长（超过 30 秒）")
    print("\n可能的原因:")
    print("  - 网络连接不稳定")
    print("  - API 服务器负载过高")
    sys.exit(1)

except requests.exceptions.ConnectionError as e:
    print(f"\n❌ 连接失败!")
    print(f"   无法连接到: {api_url}")
    print(f"   错误信息: {str(e)}")
    print("\n可能的原因:")
    print("  - API endpoint 地址不正确")
    print("  - 网络连接问题")
    print("  - 防火墙阻止连接")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ 发生未知错误!")
    print(f"   错误类型: {type(e).__name__}")
    print(f"   错误信息: {str(e)}")
    sys.exit(1)

print("\n你现在可以运行:")
print("  python my_custom_template.py")
print("\n或者在代码中使用:")
print("  asyncio.run(example_third_party_openai())")
print("\n" + "=" * 60)