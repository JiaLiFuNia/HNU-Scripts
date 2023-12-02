import requests
import base64
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pksc1_v1_5
from Crypto.PublicKey import RSA

import requests

cookies = {
    'language': 'zh-CN'
}

headers = {

    'token': '3f3f6524c53f202b7cfb752a734ef354',
}

json_data = {}

response = requests.post('https://jwc.htu.edu.cn/dev-api/appapi/Studentcj/kcdlxfDatas', cookies=cookies, headers=headers, json=json_data)
print(response.json())
def encrpt(password, public_key):
    public_key = '-----BEGIN PUBLIC KEY-----\n' + public_key + '\n-----END PUBLIC KEY-----'
    rsakey = RSA.importKey(public_key)
    cipher = Cipher_pksc1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(password.encode()))
    return cipher_text.decode()


# key需要修改成自己的
key = 'MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAKoR8mX0rGKLqzcWmOzbfj64K8ZIgOdHnzkXSOVOZbFu/TJhZ7rFAN+eaGkl3C4buccQd' \
      '/EjEsj9ir7ijT7h96MCAwEAAQ=='

password = encrpt('xubohan2004819.', key)

login_cookies = {
    'language': 'zh-CN',
}
login_headers = {
    'Referer': 'https://jwc.htu.edu.cn/app/?code',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 9; ASUS_X00TD; Flow) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/359.0.0.288 Mobile Safari/537.36',
}
login_data = {
    'username': '2201214001',
    'password': password,
    'code': '',
    'appid': None,
}
login_message = requests.post('https://jwc.htu.edu.cn/dev-api/appapi/applogin', cookies=login_cookies,
                              headers=login_headers,
                              json=login_data)

# print(login_message.json())
# print(login_message.json()['user'])
print("登录时间：" + login_message.json()['user']['loginTime'])
print("登录地点：" + login_message.json()['user']['loginIp'])
print("身份证号：" + login_message.json()['user']['usersfzh'])
print("电话号码：" + login_message.json()['user']['userdh'])
print("学院名称：" + login_message.json()['user']['userdwmc'])
print("用户姓名：" + login_message.json()['user']['userxm'])

Token = login_message.json()['user']['token']
print(Token)

cookies = {
    'language': 'zh-CN',
}

headers = {
    'Referer': 'https://jwc.htu.edu.cn/app/',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX3085) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 '
                  'Mobile Safari/537.36',
    'token': Token,
}

json_data = {
    'zc': '',
    'jc': '',
}

response = requests.post('https://jwc.htu.edu.cn/dev-api/appapi/Studentkb/index', cookies=cookies, headers=headers,
                         json=json_data)
print(response.json())
print(response.json()['kbList'])
