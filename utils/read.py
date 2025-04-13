import json
def read_jsonl(file_path):
    result = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    json_obj = json.loads(line)
                    result.append(json_obj)
                except json.JSONDecodeError:
                    print(f"错误: 第 {len(result) + 1} 行不是有效的 JSON 格式。")
    except FileNotFoundError:
        print("错误: 文件未找到。")
    except Exception as e:
        print(f"错误: 发生未知错误: {e}")
    return result

    