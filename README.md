# LineBot with Chat GPT4 Assistant that has send_email function

一個 Line Bot 機器人, 用戶傳訊息給該機器人進行對話, 並且具有寄信功能。

Ex. 請幫我寄信給service@cxcxc.io，主旨是大家好，內容是這是測試訊息。

## 安裝

在這個部分，你需要提供安裝你的項目所需要的步驟。這可能包括如何克隆你的儲存庫、安裝依賴項等。

```bash
# git clone 下來後

# 更新 docker-compose-dev.yml 的 NGROK_AUTH

# 透過 VSCode 的 Remote Container, 設定檔為 docker-compose-dev.yml

# 進入容器內開發後, localhost:8888 可以取得開發時要設定的 Line Bot webhook

# 更新 .env 設定值

# 在容器內執行
python app.py

# 至 Line Bot Developer 設定 webhook 並確認啟用該功能

# 測試傳訊息給 Line Bot
```

### .env設定值
1. LINE_CHANNEL_ACCESS_TOKEN = ''

Line Bot messaging API 所需設置

2. LINE_CHANNEL_SECRET = 

Line Bot messaging API 所需設置

3. OPEN_AI_KEY = 

使用 openAI Assistant API 所需的 key

4. EMAIL_ACCOUNT = ""

gmail, ex. sheiyuray@gmail.com

5. EMAIL_PWD = ""

EMAIL_PWD 如何取得, 請參考至 https://stackoverflow.com/a/72734404

## 當初開發時的邏輯紀錄
建立 1 個 assistant，該 assistant 會附帶 function，該 function 有特定的 schema。

當用戶向Line機器人說話時，說出如以下
請幫我寄信給 xxx，告訴他 aaa

建立暫存的 thread，並以該line_user_id為鍵，將thread_id存入暫存檔 thread_<line_user_id>.json

assistant 會幫我生成特定的 schema

利用該 schema 取出 要寄送的目標 email，寄送內容，主旨

放入我寫的 gmail API 寄送 email 到 service@cxcxc.io

將「已成功發送 email」回傳(submit_tool_outputs) 給AI

## 檔案結構說明
### app.py
用以運行 flask 作為 Line Bot 接收訊息後傳到我方的系統，以下是這個系統有的 API：

1. GET /ping

用來測試系統是否正常運行, 正常皆啟動的狀態下, 訪問 https://<ngrok網址>/ping, 會看到 pong 的內容

2. GET /callback

用以接收 Line Bot 用戶傳來的訊息。

### openai_helper.py
放有所有 openAI Assistant API 所做的客製化方法。

### send_gmail.py
寄信方法。

## 參考連結
1. https://platform.openai.com/assistants
2. https://cookbook.openai.com/examples/assistants_api_overview_python
3. https://cobusgreyling.medium.com/what-are-openai-assistant-function-tools-exactly-06ef8e39b7bd
4. https://platform.openai.com/docs/assistants/overview