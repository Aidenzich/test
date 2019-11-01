from flask import Flask, request, abort
import configparser #讀.ini套件
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
#爬蟲套件
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

import os
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), r"config.ini"))

line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
handler = WebhookHandler(config['line_bot']['Channel_Secret'])

my_id = 'U635be6992c3da08f2edc4e876b94254b' #我的User id
#line_bot_api.push_message(my_id, TextSendMessage(text='push api推播成功')) #直接發送

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	user_id = event.source.user_id #抓取使用者的ID
	profile = line_bot_api.get_profile(user_id) #抓使用者的個人資料
	print("說話的人是:"+profile.display_name+"\n他的user id是:"+profile.user_id+"\n他的大頭貼網址是:"+profile.picture_url+"\n他的狀態消息是:"+profile.status_message)
	message = TextSendMessage(text=event.message.text)
	line_bot_api.reply_message(event.reply_token, message) #傳啥回啥
	#line_bot_api.push_message(my_id, TextSendMessage(text=str(profile.display_name)+ '傳訊息，他說\n' +str(event.message.text)+ '\n他的user id是:\n' +str(user_id))) #回傳給我誰傳了訊息 說了什麼以及他的user id
	#if (str(user_id) == my_id and event.message.text == '群發測試'): #群發用的
		#line_bot_api.push_message(my_id, TextSendMessage(text='push api推播成功'))
		#line_bot_api.multicast([user_id, 'Ue61567a1bb1b9f0dd41541f4a7977aa3'], TextSendMessage(text='push api群發測試，麻煩收到回覆一下')) #傳送給複數人

@handler.add(FollowEvent) #加入好友的事件處理
def handle_follow(event): 
	user_id = event.source.user_id #抓取使用者的ID
	profile = line_bot_api.get_profile(user_id) #抓使用者的個人資料
	line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str(profile.display_name)+' Thanks your follow!\nYour user id is:\n'+str(user_id)))
	
#Flask測試
@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
