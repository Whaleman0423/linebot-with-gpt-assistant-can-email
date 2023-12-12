import json
import os
import time
from IPython.display import display
from openai import OpenAI
from send_gmail import send_email


api_key = os.getenv('OPEN_AI_KEY')
client = OpenAI(api_key=api_key)
# 在 https://platform.openai.com/assistants 上建立的 assistant 的 id
assistant_id = "asst_1CRiUsrQC3QO10Aipe9mUrjV"


def deal_with_user_text_request_and_return_text_response(line_user_id, user_message_content):

    thread_id = get_thread_id(line_user_id)

    message = create_new_message(
        thread_id,
        # content="我需要解決一個等式 `3x + 11 = 14`"
        content=user_message_content
    )

    run = create_a_run(thread_id)
    run = wait_on_run(run, thread_id)

    if run.status == "requires_action":
        show_json(run)
        name = get_function_name(run)
        arguments = get_function_return_arguments(run)
        print(f"呼叫函數名稱: {name}")
        print(f"呼叫函數的回傳參數: {arguments}")
        send_email(subject=arguments["subject"],
                   message=arguments["body"],
                   to_email=arguments["to_address"]
                   )

        # 將結果反饋回我們的 Assistant, 此為必要, 若無的話, thread 的狀態會卡住
        run = submit_tool_output(thread_id, run, "郵件已成功發送！")

        return ["郵件已成功發送！"]
    else:
        # Retrieve all the messages added after our last user message
        messages = get_messages_after(thread_id, message)
        show_json(messages)
        message_string_values = extract_message_values(messages)

        return message_string_values

def submit_tool_output(thread_id, run, output_message):
    """提交工具輸出到指定的線程和運行中, 想像成: Assistant 給我們答案, 我們給他反饋, 讓 Assistant 更優化。"""
    tool_call = run.required_action.submit_tool_outputs.tool_calls[0]

    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run.id,
        tool_outputs=[
            {
                "tool_call_id": tool_call.id,
                "output": json.dumps([output_message]),
            }
        ],
    )

    # 显示 JSON 结果（假设 show_json 是一个显示 JSON 的辅助函数）
    show_json(run)
    return run


def extract_message_values(messages):
    values = []
    for message in messages['data']:
        # 遍歷每個消息的 'content' 部分
        for content in message['content']:
            if 'text' in content and 'value' in content['text']:
                values.append(content['text']['value'])
    return values


def get_messages_after(thread_id, message):
    """獲取給定 thread_id 中在特定 message 之後的所有訊息。"""
    try:
        messages = client.beta.threads.messages.list(
            thread_id=thread_id, order="asc", after=message.id
        )
        return messages
    except Exception as e:
        print(f"獲取訊息時出錯: {e}")
        return {"data": []}


def get_function_return_arguments(run):
    """獲取函數的回傳參數"""
    tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
    arguments = json.loads(tool_call.function.arguments)
    return arguments


def get_function_name(run):
    """獲取函數的名稱"""
    tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
    name = tool_call.function.name
    return name


def show_json(obj):
    display(json.loads(obj.model_dump_json()))


def create_new_thread():
    """用戶需要開啟新的對話, 須建立 thread"""
    thread = client.beta.threads.create()
    show_json(thread)

    return thread


def save_personel_thread_id_file(line_user_id, thread_id):
    # 創建一個字典，其中包含 thread_id
    data = {"thread_id": thread_id}

    # 設定檔案名稱為 line_user_id.json
    file_name = f"{line_user_id}.json"

    # 寫入數據到JSON檔案中
    with open(file_name, 'w') as file:
        json.dump(data, file)

    print(f"檔案 {file_name} 已成功創建並寫入數據。")


def check_thread_id_file_save_in_local_cache(line_user_id):
    """檢查是否存在特定用戶的JSON檔案"""
    file_name = f"{line_user_id}.json"
    return os.path.exists(file_name)


def get_thread_id(line_user_id):
    """獲取或創建一個新的對話線程ID"""
    if check_thread_id_file_save_in_local_cache(line_user_id):
        # 如果檔案存在，從檔案中讀取 thread_id
        with open(f"{line_user_id}.json", 'r') as file:
            data = json.load(file)
            return data["thread_id"]
    else:
        # 如果檔案不存在，創建新的對話線程並保存
        thread = create_new_thread()
        save_personel_thread_id_file(line_user_id, thread.id)
        return thread.id


def create_new_message(thread_id, content):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )
    show_json(message)
    return message


def create_a_run(thread_id):
    """讓 assistant 處理這個 thread, 需創建 run"""
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    show_json(run)
    return run


def wait_on_run(run, thread_id):
    """run 為異步函數, 存有 assistant 處理該 thread 的狀態, 用 while 迴圈做監控"""
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        time.sleep(0.5)
    show_json(run)
    return run
