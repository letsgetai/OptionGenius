import chromadb
from utils.requst_model import get_embedding, chat_with_model
from collections import defaultdict
import json
from utils.prompt_tempate import prompt_tempate
class OptionGenius():
    def __init__(self,):
        chroma_client = chromadb.PersistentClient(path ='/workspace/高情商机器人/database')
        self.collection = chroma_client.get_or_create_collection(name="chat_bot")
        self.refs = None
    
    def result_to_prompt(self, result, query, situation):
        para = ''
        for id, doc in enumerate(result):
            query_cur = doc.get('query', '')
            answer_type = doc.get('回复类型', '')
            answer = doc.get('回复内容', '')
            situation_cur = doc.get('应用场景', '')
            emotion = doc.get('情绪类型', '')
            para += f"问题：{query_cur} 场景：{situation_cur}\n情绪：{emotion}，{answer_type}：{answer}\n\n"
        return prompt_tempate(para, query, situation)
    def run(self, query, situation):
        result = self.retrive(query)
        self.refs = self.rank(result)
        prompt = self.result_to_prompt(self.refs, query, situation)
        answer = chat_with_model(prompt)
        return answer, self.refs
    def retrive(self, query, top_k=5):
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            query_embeddings = [get_embedding(query)]
        )
        result = []
        for i in range(len(results['documents'][0])):
            json_list = json.loads(results['metadatas'][0][i]['json_data'])
            result.extend(json_list)
        return result
    def rank(self, result):
        # 情绪类型： 积极、中立、幽默、讽刺等等多种，我要从幽默的里面选3个，积极选3个，其他都选一个
        # 排序打乱
        result = sorted(result, key=lambda x: x['情绪类型'], reverse=True)
        positive = []
        humour = []
        other = []
        used_other = set()
        for i in range(len(result)):
            if result[i]['情绪类型'] == '幽默':
                if len(humour) == 3:
                    continue
                humour.append(result[i])
            elif result[i]['情绪类型'] == '积极':
                if len(positive) == 3:
                    continue
                positive.append(result[i])
            else:
                if result[i]['情绪类型'] not in used_other:
                    used_other.add(result[i]['情绪类型'])
                    other.append(result[i])
                else:
                    continue
        finally_result = []
        finally_result.extend(humour)
        finally_result.extend(positive)
        finally_result.extend(other)
        return finally_result[:10]
    
if __name__ == '__main__':
    option_genius = OptionGenius()
    answer, refs = option_genius.run("crush跟我发擦边美女视频","抖音聊天")
    print(answer)
    print(refs)