from linebot import LineBotApi
from linebot.models import TextSendMessage

# リモートリポジトリに"ご自身のチャネルのアクセストークン"をpushするのは、避けてください。
# 理由は、そのアクセストークンがあれば、あなたになりすまして、プッシュ通知を送れてしまうからです。

configuration = Configuration(access_token='17bVejREkwYGguGq300UUUEntbsxM3D1QW80/pKRA3QF3sH7twBwIqIkXB5Qsj3ZanbG+YHOflf2iPLwfyxGiZXEwJXWTeXmarUPttBXjoG9odTJ/0sTo8SAelxU6kHPn6qyBq0P7ZvcWEX8ddWXXwdB04t89/1O/w1cDnyilFU=')
line_bot_api = LineBotApi(configuration)


def main():
    user_id = "Uc89db96b19d90572c620df0c1e9eac19"

    messages = TextSendMessage(text=f"こんにちは😁\n\n"
                                    f"最近はいかがお過ごしでしょうか?")
    line_bot_api.push_message(user_id, messages=messages)


if __name__ == "__main__":
    main()