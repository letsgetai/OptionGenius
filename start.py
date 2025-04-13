import gradio as gr
from OptionGenius import OptionGenius
import json
import chromadb
from utils.requst_model import get_embedding
from datetime import datetime
from collections import defaultdict
# 初始化组件
agent = OptionGenius()
chroma_client = chromadb.PersistentClient(path='/workspace/高情商机器人/database')
collection = chroma_client.get_or_create_collection(name="chat_bot")

# 状态缓存
response_cache = gr.State({})

def generate_response(query, situation):
    try:
        raw_response, refs = agent.run(query, situation)
        print(raw_response)
        raw_response = raw_response.replace("```json", '').replace("```", '')
        try:
            parsed = json.loads(raw_response)
            return parsed,parsed, refs  # 返回原始数据和处理后数据
        except Exception as e:
            print(f"解析失败: {str(e)}")
            print(f"原始数据: {raw_response}")
            return {"error": f"解析失败: {str(e)}"}, None, None
    except Exception as e:
        print(f"生成响应失败: {str(e)}")
        return {"error": str(e)}, None, None

def save_selected_responses(query, situation, selected_items, current_data):
    print(selected_items,current_data)
    try:
        records = []
        for selected_index in selected_items:
            reply = current_data["推荐回复"][int(selected_index)]
            print(reply,'----------------------------')
            records.append({
                "query": query,
                "应用场景": situation,
                "回复内容": reply["回复内容"],
                "情绪类型": reply["情绪类型"],
                "回复类型": reply["回复类型"]

            })
        
        # 添加到数据库
        add_data_to_collection(records)
        return f"✅ 成功保存 {len(records)} 条记录到数据库"
    except Exception as e:
        return f"❌ 保存失败: {str(e)}"

def add_data_to_collection(data_list):
    """优化后的新版存储函数"""
    query_data = defaultdict(list)
    for json_data in data_list:
        query = json_data['query']
        query_data[query].append(json_data)
    for  idx, (query, json_data) in enumerate(query_data.items()):
        embedding = get_embedding(query)
        collection.add(documents=[query],
                    metadatas=[{"json_data": json.dumps(json_data,ensure_ascii=False)}],
                    ids=datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    embeddings = [embedding])   
    print("数据导入成功",data_list)
def generate_choice_labels(data):
    """生成带索引值的多选标签"""
    emotion_icons = {
        "幽默": "😂",
        "调侃": "😏", 
        "积极": "🌞",
        "挑衅": "🔥"
    }
    choices = []  # 改用 choices 而不是 labels
    for idx, item in enumerate(data["推荐回复"]):
        # icon = emotion_icons.get(item["情感类型"], "💬")
        # label = f"{icon} {item['回复类型']} | {item['情感类型']}"
        choices.append(str(idx))  # ✅ 格式: (value, display_text)
    return choices

# 在with gr.Blocks()内添加状态初始化
with gr.Blocks(theme=gr.themes.Soft(), title="对话管理系统") as demo:
    gr.Markdown("## 🤖 高情商对话管理系统 V2.1")
    
    # 显式初始化所有状态相关组件
    response_cache = gr.State({})
    #save_panel = gr.Column(visible=True)
    #response_selector = gr.CheckboxGroup(visible=True)
    #refs = gr.JSON()
    with gr.Row():
        with gr.Column(scale=4):
            query_box = gr.Textbox(label="输入对话内容", placeholder="请输入需要回应的对话内容...",
                                 value="crush问我明天一起出去玩嘛？？",max_lines=3)
            situation_selector = gr.Textbox(label="适用场景", value="微信聊天")
            generate_btn = gr.Button("生成智能回复", variant="primary")
            
            refs = gr.JSON(label="参考例子")
        with gr.Column(scale=6):
            with gr.Accordion("生成结果详情", open=True):
                analysis_view = gr.JSON(label="数据分析")
                response_selector = gr.CheckboxGroup(
                    label="选择要保存的回复方案",
                    interactive=True,
                    visible=True
                )
            save_panel = gr.Column(visible=True)
            with save_panel:
                save_btn = gr.Button("保存选中方案", variant="secondary")
                save_status = gr.Markdown()

    # 修改后的交互链
    generate_btn.click(
        fn=generate_response,
        inputs=[query_box, situation_selector],
        outputs=[analysis_view, response_cache, refs]
    ).then(
        lambda data: gr.update(  # ✅ 使用 gr.update() 而不是 CheckboxGroup.update
            choices=generate_choice_labels(data) if data else [],
            value=[],
            visible=True if data else False
        ),
        inputs=[response_cache],
        outputs=[response_selector]
    )

    # 修改后的保存函数调用
    save_btn.click(
        fn=save_selected_responses,
        inputs=[query_box, situation_selector, response_selector, response_cache],
        outputs=[save_status]
    ).then(
        lambda: gr.update(value=[]),
        outputs=[response_selector]
    )
if __name__ == "__main__":
    demo.launch(server_port=7860, show_error=True, share=True)