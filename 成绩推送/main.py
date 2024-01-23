import base64
from pushplus import send_message
import requests
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pksc1_v1_5
from Crypto.PublicKey import RSA

# 伪装浏览器
new_login_cookies = {
    'language': 'zh-CN',
}
new_login_headers = {
    'Referer': 'https://jwc.htu.edu.cn/app/?code',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 '
                  'Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090819) '
                  'XWEB/8519 Flue '
}
gitee_url = 'https://gitee.com/xhand_xbh/hnu/raw/master'
# 获取密码加密公钥
public_key = requests.get(gitee_url + '/publickey.txt').text


# 密码加密函数
def encrpt(passward, publickey):
    publickey = '-----BEGIN PUBLIC KEY-----\n' + publickey + '\n-----END PUBLIC KEY-----'
    rsakey = RSA.importKey(publickey)
    cipher = Cipher_pksc1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(passward.encode()))
    return cipher_text.decode()


# 获取消息列表
def new_if_logined(token):
    if token == "0000":
        login_response = new_jw(stu_id, pwd)
        token = login_response['user']['token']
        print(f"token：{token}")
    else:
        login_response = ""
    login_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/107.0.0.0 '
                      'Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090819) '
                      'XWEB/8519 Flue ',
        'token': token,
    }
    json_data = {}
    mes_res = requests.post('https://jwc.htu.edu.cn/dev-api/appapi/getNotice', cookies=new_login_cookies,
                            headers=login_headers,
                            json=json_data)
    if mes_res.json()['code'] == 401:
        token = "0000"
        new_if_logined(token)
    else:
        return login_response, mes_res.json(), token


# 获取全部成绩,生成kcdm, cjdm, jd
def get_scores_list(token):
    login_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/107.0.0.0 '
                      'Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090819) '
                      'XWEB/8519 Flue ',
        'token': token,
    }
    json_data = {
        'xnxqdm': '202301',
    }
    scores = requests.post('https://jwc.htu.edu.cn/dev-api/appapi/Studentcj/data', cookies=new_login_cookies,
                           headers=login_headers, json=json_data)
    print(f"成绩列表：{scores.json()['kccjList']}")
    cjdm = {}
    jd = {}
    for kcmc in scores.json()['kccjList']:
        cjdm[kcmc['kcdm']] = kcmc['cjdm']
        jd[kcmc['kcdm']] = kcmc['cjjd']
    return scores.json()['kccjList'], cjdm, jd


# 获取新增科目的信息
def get_score(token, kcdm, mc, cjdms, jd):
    print(f"new kcdm：{kcdm}")
    cjdm = cjdms[kcdm]
    login_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/107.0.0.0 '
                      'Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090819) '
                      'XWEB/8519 Flue ',
        'token': token,
    }
    json_data = {
        'cjdm': cjdm,
    }
    print(f"new cjdm：{cjdm}")
    response = requests.post('https://jwc.htu.edu.cn/dev-api/appapi/Studentcj/detail', cookies=new_login_cookies,
                             headers=login_headers, json=json_data)
    print(f"具体信息：{response.json()}")
    contents = f"课程名称：{mc}  \n" \
               f"总成绩：{response.json()['xscj']['zcj']}  \n" \
               f"平时成绩：{response.json()['xscj']['cj1']}  \n" \
               f"期末成绩：{response.json()['xscj']['cj4']}  \n" \
               f"绩点：{jd[kcdm]}  \n" \
               f"___\n"
    return contents


# 智慧教务获取个人信息
def person_message(login_message):
    if login_message['code'] != 200:
        new_jw(stu_id, pwd)
    elif login_message['code'] == 200:
        content = f"##### 个人信息：\n" \
                  f"姓名：{login_message['user']['userxm']}  \n" \
                  f"学号：{login_message['user']['userAccount']}  \n" \
                  f"学院：{login_message['user']['userdwmc']}  \n" \
                  f"___"
        return content


# 智慧教务登录
def new_jw(xh, passward):
    login_data = {
        'username': xh,
        'password': encrpt(passward, public_key),
        'code': '',
        'appid': None,
    }
    new_jw_url = 'https://jwc.htu.edu.cn/dev-api/appapi/applogin'
    login_response = requests.post(url=new_jw_url, cookies=new_login_cookies, headers=new_login_headers,
                                   json=login_data)
    if login_response.json()['code'] == 200:
        return login_response.json()


if __name__ == "__main__":
    tokend = 'e2b8907189b0e722ed467525664730f8'
    stu_id = '2201214001'
    pwd = 'xubohan2004819.'
    # 获取消息数目
    login_res, message_res, tokend = new_if_logined(tokend)
    if login_res == "":
        login_res = new_jw(stu_id, pwd)
    # 个人信息内容
    content_1 = person_message(login_res)
    content_2s = ["##### 成绩信息：  \n"]
    content_3s = ["##### 全部成绩：  \n"]
    # 获取全部成绩信息 cjdm jd
    scores_list, cjdm_s, jd_s = get_scores_list(tokend)
    for i in scores_list:
        content_3 = f"课程名称：{i['kcmc']}  \n" \
                    f"成绩：{i['zcjfs']}  \n" \
                    f"绩点：{i['cjjd']}  \n" \
                    f"  \n"
        content_3s.append(content_3)
    content_3s.append("___  \n")
    # 获取消息名称
    kcmcs = []
    if len(message_res['data']) != 0:
        for i in message_res['data']:
            msg = i['msg'].split('"')
            print(f"更新列表：{msg}")
            kcmcs.append(msg[-2])
            # get_score(token, kcdm, mc, cjdm, jd)
            content_2s.append(get_score(tokend, msg[7], msg[-2], cjdm_s, jd_s))
    else:
        print("无消息")
    # 拼接标题
    title = f"{' '.join(kcmcs)} 成绩已更新"
    # 拼接内容
    content = f"{''.join(content_2s)}{content_1}"
    print(content)
    if len(message_res['data']) != 0:
        # 发送push
        res = send_message(title, content)
        print(f"推送状态：{res}")
