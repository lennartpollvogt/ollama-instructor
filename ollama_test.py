from ollama import Client

client = Client()

response = client.chat(
    model='qwen2.5:3b',
    messages=[
        {
            'role': 'user',
            'content': 'Why is the sky blue?'
        }
    ],
    stream=True
)

for chunk in response:
    if isinstance(chunk, dict) and 'message' in chunk and isinstance(chunk['message'], dict):
        message_content = chunk['message'].get('content', '')
        print(message_content)
    else:
        print("Unexpected structure:", chunk)
