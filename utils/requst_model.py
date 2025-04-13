import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # 加载.env文件
# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI(
    api_key=os.environ.get("ARK_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

def get_embedding(text):
    resp = client.embeddings.create(
        model="doubao-embedding-text-240715",
        input=[text],
        encoding_format="float"
    )
    return resp.data[0].embedding

def chat_with_model(prompt):
    completion = client.chat.completions.create(
        # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
        model="deepseek-v3-250324",
        messages=[
            {"role": "system", "content": "你是一个高情商的人工智能助手"},
            {"role": "user", "content": prompt},
        ],
        )
    return completion.choices[0].message.content
