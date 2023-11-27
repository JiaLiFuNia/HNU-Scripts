import requests
import re
import time
from PIL import Image

# 获取二维码uuid
url = 'https://open.weixin.qq.com/connect/qrconnect?' \
      'appid=wx47499e3e379d78a7&' \
      'redirect_uri=http://authserver2.htu.edu.cn/authserver/callback&' \
      'response_type=code&' \
      'scope=snsapi_login&' \
      'state=2b57fbd2128f70048f1dc9d2ca22837e '

uuid_response = requests.get(url=url)
'<img class="web_qrcode_img" src="/connect/qrcode/041DivUO29hoFa1X"/>'
pattern = r'<img\s+class="web_qrcode_img"\s+src="/connect/qrcode/([^"]+)"\s*/>'
match = re.search(pattern, uuid_response.text)
uuid = match.group(1)
print("二维码的uuid：", uuid)

# 获取二维码图片
code_response = requests.get('https://open.weixin.qq.com/connect/qrcode/' + uuid).content

with open(f"{uuid}.jpg", "wb") as file:
    file.write(code_response)
img = Image.open(f'{uuid}.jpg')
img.show()

headers = {
    'Referer': 'https://open.weixin.qq.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 '
                  'Safari/537.36 Edg/114.0.1823.58',
}
params = {
    'uuid': uuid,
    '_': str(int(time.time() * 1000))
}
status_code = '400'
while status_code != '405':
    # 获取状态信息
    response = requests.get('https://lp.open.weixin.qq.com/connect/l/qrconnect', params=params, headers=headers)
    """window.wx_errcode=408;window.wx_code='';"""
    match = re.search(r'window\.wx_errcode=(\d+);', response.text)
    status_code = match.group(1)
    if status_code == '405':
        match = re.search(r'window\.wx_code=\'(.*?)\';', response.text)
        wx_code = match.group(1)
        print('wx_code:', wx_code)

        match = re.search(r'&state=([^\s;&]+)', uuid_response.text)
        state = match.group(1)
        print('state:', state)

        login_url = 'http://authserver2.htu.edu.cn/authserver/callback'
        login_data = {
            'code': wx_code,
            'state': state
        }
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58',
        }
        session = requests.Session()
        session.keep_alive = False
        login_response = session.post(url=login_url, data=login_data, headers=headers, allow_redirects=True)
        jsessionid = login_response.cookies.get("JSESSIONID")
        route = login_response.cookies.get("route")
        set_cookies = login_response.headers['Set-Cookie']
        print(login_response.headers)
        print(jsessionid, route)
        print(login_response.status_code)
        print(set_cookies)
        session.close()

        cookies = {
            'route': '7dae9be4d7bdb1d18ee0236b10df067e',
            'JSESSIONID': '4E3CB034F907F552706A38D0376B9E36',
            'CASTGC': 'TGT-50701-cgnWAir-dwh20vZy0VZRHubnr8BrBJnGnd71rc7Oe8muD67-ZvuRb-gXR824VK6UoU0localhost'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58',
        }

        params = {
            'service': 'https://jwc.htu.edu.cn/new/ssoLogin',
        }
        login_response_2 = requests.get(url=login_response.url, params=params, cookies=cookies, headers=headers, verify=False)
        if login_response_2.history:
            last_response = login_response_2.history[-1]
            location_url = last_response.headers['Location']
            print(location_url)
        else:
            print('没有重定向')
    else:
        print("状态码：", status_code)
