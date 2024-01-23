import requests
import json
import os


def send_message(title, content):
    token = "0ee3d58a9bfe4dc2a7127720ba0f9edc"
    url = "http://www.pushplus.plus/send"
    data = {"token": token, "title": title, "content": content, "template": 'markdown'}
    body = json.dumps(data).encode(encoding="utf-8")
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=body, headers=headers)
    return response.text
