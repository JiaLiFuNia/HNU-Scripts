import base64
import json
import time
from PIL import Image
import requests
import datetime
import os

headers = {
    "Host": "api-xcx-qunsou.weiyoubot.cn",
    "Connection": "keep-alive",
    "Content-Length": "324",
    "charset": "utf-8",
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22041211AC Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, "
                  "like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5279 MMWEBSDK/20230504 "
                  "MMWEBID/6844 MicroMessenger/8.0.37.2380(0x28002537) WeChat/arm64 Weixin NetType/5G Language/zh_CN "
                  "ABI/arm64 MiniProgramEnv/android",
    "content-type": "application/json",
    "Accept-Encoding": "gzip,compress,br,deflate",
    "Referer": "https://servicewechat.com/wxfaa08012777a431e/968/page-frame.html"
}
eids = []
titles = []
times = []
limits = []


def save_token(text):
    with open(r"./Token.txt", 'w') as file:
        file.write(text)


def get_ocr():
    url = 'https://api-xcx-qunsou.weiyoubot.cn/xcx/enroll_web/v1/pc_code'
    ret = requests.get(url).json()
    if ret['msg'] != 'ok':
        return ''
    img_imf = ret['data']['qrcode'].replace('data:image/jpg;base64,', '')
    code = ret['data']['code']
    page_content = base64.b64decode(img_imf)
    with open('./b.png', 'wb') as f:
        f.write(page_content)
    print("使用微信扫码二维码！！！！")
    img = Image.open('./b.png')
    img.show()
    url = 'https://api-xcx-qunsou.weiyoubot.cn/xcx/enroll_web/v1/pc_login?code=%s' % code
    os.remove('./b.png')
    while True:
        ret = requests.get(url).json()
        if ret['msg'] != 'please wait':
            save_token(ret['data']['access_token'])
            return ret['data']['access_token']
        time.sleep(1)


def Tokens():
    if os.path.exists(r"Token.txt"):
        file_time = os.path.getctime(r"Token.txt")
        current_timestamp = time.time()
        if current_timestamp - file_time <= 18000:
            with open(r'Token.txt', 'r') as file:
                return file.read()
        else:
            return get_ocr()
    else:
        return get_ocr()


token = Tokens()
params = {
    'access_token': token,
}
response = requests.get('https://api-xcx-qunsou.weiyoubot.cn/xcx/enroll/v1/user/history', params=params)
active_datas = response.json()['data']
index = 1
print('活动信息如下：')
for i in active_datas:
    if i['status'] != 2:
        print(f"序号：[{index}] 活动名称：{i['title']} 人数限制：{i['limit']} 开始时间: {datetime.datetime.fromtimestamp(i['start_time'])}")
        index += 1
        eids.append(i['eid'])
        titles.append(i['title'])
        times.append(i['start_time'])
        limits.append(i['limit'])
timestamp = int(time.time())
print("当前时间：" + str(datetime.datetime.fromtimestamp(timestamp)))
url = 'https://api-xcx-qunsou.weiyoubot.cn/xcx/enroll/v5/enroll'
num = int(input("请输入序号："))
# print(times[num - 1])
# print(timestamp)
name = input("输入姓名：")
data = {
    "access_token": token,
    "eid": eids[num - 1],
    "info": [
        {
            "field_name": "姓名",
            "field_value": name,
            "field_key": 1
        }
    ],
    "on_behalf": 0,
    "items": [],
    "referer": "",
    "fee_type": "",
    "from": "xcx",
}
timestamp = int(time.time())
if times[num - 1] > timestamp:
    print("正在等待达到预定时间...")
    time_sleep = times[num - 1] - timestamp
    print(f"还有{time_sleep}秒...")
else:
    print("报名已开始...")
    time_sleep = -1

time.sleep(time_sleep + 1)
response = requests.post(url=url, headers=headers, data=json.dumps(data))
print(response.json())
input("点击回车退出...")
