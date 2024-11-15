import json
import threading
import schedule
import time
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

# LINE Bot設定
configuration = Configuration(access_token='17bVejREkwYGguGq300UUUEntbsxM3D1QW80/pKRA3QF3sH7twBwIqIkXB5Qsj3ZanbG+YHOflf2iPLwfyxGiZXEwJXWTeXmarUPttBXjoG9odTJ/0sTo8SAelxU6kHPn6qyBq0P7ZvcWEX8ddWXXwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('17221b84038708c34cb1a47ae5032623')
SCHEDULE_FILE = "schedule.json"

# スケジュール用のグローバル変数
scheduling_lock = threading.Lock()
setting_mode_users = set()  # スケジュール設定モードのユーザーIDを格納

def load_schedule():
    """JSONファイルからスケジュールを読み込み"""
    try:
        with open(SCHEDULE_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"study_time": None}

def save_schedule(schedule_data):
    """スケジュールをJSONファイルに保存"""
    with open(SCHEDULE_FILE, "w") as file:
        json.dump(schedule_data, file, indent=4)

def initialize_schedule():
    """スケジュールをセットアップ"""
    schedule.clear()
    data = load_schedule()
    time_str = data.get("study_time")
    if time_str:
        schedule.every().day.at(time_str).do(send_study_start_message)

def send_study_start_message():
    """勉強開始時刻のメッセージを送信"""
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        message = "勉強開始時刻です。今日も勉強頑張ろう！"
        # 送信先のユーザーIDに置き換える
        user_id = "Uc89db96b19d90572c620df0c1e9eac19"
        line_bot_api.push_message(
            to=user_id,
            messages=[TextMessage(text=message)]
        )
        print(f"メッセージを送信しました: {message}")

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """ユーザーのメッセージを処理し、勉強開始時刻を更新"""
    user_id = event.source.user_id
    lineRes = event.message.text.strip()
    botRes = ""

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # スケジュール設定モードのチェック
        if lineRes == "勉強スケジュール設定":
            setting_mode_users.add(user_id)
            botRes = "勉強スケジュール時刻を設定します。HH:MMの形式で入力してください。"
        elif user_id in setting_mode_users:
            try:
                # 時刻が正しい形式か確認
                time.strptime(lineRes, "%H:%M")
                with scheduling_lock:
                    # 新しいスケジュールに上書き
                    data = {"study_time": lineRes}
                    save_schedule(data)
                    initialize_schedule()
                    botRes = f"勉強開始時刻を {lineRes} に設定しました！"
                    setting_mode_users.remove(user_id)  # 設定モード解除
            except ValueError:
                botRes = "時間は HH:MM の形式で入力してください。もう一度勉強スケジュール設定を選択してください。"

        # メッセージの返信
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=botRes)]
            )
        )

def schedule_runner():
    """スケジューラーの実行ループ"""
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # スケジュール初期化
    initialize_schedule()

    # スケジューラーを別スレッドで実行
    scheduler_thread = threading.Thread(target=schedule_runner, daemon=True)
    scheduler_thread.start()

    # Flaskアプリの起動
    app.run()
