from model_api import MultiPortOpenAIClient

# vllm model info for CoDiQ-Gen-8B
ENDPOINTS = [
    "your_base_url",
]
API_KEY = "your_api_key"
MODEL = "your_model_name"

multi_client = MultiPortOpenAIClient(endpoints=ENDPOINTS, api_key=API_KEY)

def json_api_call(messages, n=1):
    client, _ = multi_client.get_next_client()
    
    completions = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        n=n,
        temperature=0.7,
        timeout=300,
        response_format={"type": "json_object"},
        extra_body={
            "chat_template_kwargs": {"enable_thinking": False},
        },
    )
    return [choice.message.content for choice in completions.choices]

def api_call(messages, n=1):
    client, _ = multi_client.get_next_client()
    
    completions = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        n=n,
        temperature=0.7,
        timeout=300,
        extra_body={
            "chat_template_kwargs": {"enable_thinking": False},
        },
    )
    return [choice.message.content for choice in completions.choices]

def call_gpt(history, prompt):
    return api_call(history + [{"role": "user", "content": prompt}])

if __name__ == "__main__":
    # 测试多次调用，观察端点轮询
    for i in range(10):
        ret = json_api_call([{"role": "user", "content": '中国首都是哪里？返回json格式 {"answer": "xxx"}'}])
        print(f"第{i+1}次调用结果 (endpoint: {multi_client.clients[i % len(multi_client.clients)]['endpoint']}): {ret}")
    
    breakpoint()
