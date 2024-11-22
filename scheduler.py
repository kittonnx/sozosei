import schedule
import time
import json
from linebot import LineBotApi
from linebot.models import TextSendMessage


token='17bVejREkwYGguGq300UUUEntbsxM3D1QW80/pKRA3QF3sH7twBwIqIkXB5Qsj3ZanbG+YHOflf2iPLwfyxGiZXEwJXWTeXmarUPttBXjoG9odTJ/0sTo8SAelxU6kHPn6qyBq0P7ZvcWEX8ddWXXwdB04t89/1O/w1cDnyilFU='

def run_task():
    """勉強開始時刻のメッセージを送信"""
    line_bot_api = LineBotApi(token)
    message = "勉強開始時刻です。今日も勉強頑張ろう！"
    user_id = "Uc89db96b19d90572c620df0c1e9eac19"
    line_bot_api.push_message(user_id, messages=[TextSendMessage(text=message)])
    
def load_schedule_from_file(filename="schedule.json"):
    """JSONファイルからスケジュール時間を読み取る"""
    try:
        with open(filename, "r") as file:
            data = json.load(file)
        return data.get("study_time", None)
    except FileNotFoundError:
        return None

def set_schedule(new_time):
    """スケジュールを設定"""
    scheduler.clear()
    if new_time:
        scheduler.every().day.at(new_time).do(run_task)
        print(f"スケジュールが {new_time} に設定されました！")
    else:
        print("スケジュール時間が設定されていません。")

# 初期スケジュールを読み込み
filename = "schedule.json"
current_time = load_schedule_from_file(filename)
set_schedule(current_time)

while True:
    # ファイルの変更をチェックしてスケジュールを更新
    new_time = load_schedule_from_file(filename)
    if new_time != current_time:
        current_time = new_time
        set_schedule(current_time)

    # タスクを実行
    scheduler.run_pending()
    time.sleep(5)
