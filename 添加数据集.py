import chromadb
from utils.read import read_jsonl
from utils.requst_model import get_embedding
from collections import defaultdict
import json
query_data = defaultdict(list)
json_data_list = read_jsonl('database/json_data/0413crush.jsonl')
for json_data in json_data_list:
    query = json_data['query']
    query_data[query].append(json_data)
chroma_client = chromadb.PersistentClient(path ='/workspace/高情商机器人/database')

collection = chroma_client.get_or_create_collection(name="chat_bot")
for  idx, (query, json_data) in enumerate(query_data.items()):
    embedding = get_embedding(query)
    collection.add(documents=[query],
                   metadatas=[{"json_data": json.dumps(json_data,ensure_ascii=False)}],
                   ids=[str(idx)],
                   embeddings = [embedding])

'''
peek（）- 返回集合中前 10 个项目的列表。
计数（）- 返回集合中的项数。
修改（）- 重命名集合
collection.peek() 
collection.count() 
collection.modify(name="new_name")
collection.delete(ids=["0"])
'''
query = "crush"
results = collection.query(
    query_texts=[query],
    n_results=2,
    query_embeddings = [get_embedding(query)]
)
print(results)
