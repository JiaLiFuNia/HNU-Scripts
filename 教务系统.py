import base64
import csv
import datetime
import json
import os
import re
import sys
import time
from datetime import datetime

import requests
import unicodedata
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pksc1_v1_5
from Crypto.PublicKey import RSA
from bs4 import BeautifulSoup
from js2py import eval_js
from lxml import html

print("------------------------欢迎使用------------------------")
current_version = '6.1.8'
gitee_url = 'https://gitee.com/xhand_xbh/hnu/raw/master'
try:
    res_version = requests.get(gitee_url + "/htu_version.json")
    latest_version = res_version.json()['version_detail']
except Exception as e:
    print("无网络链接!请连接网络后，重试！")
    input("按回车键退出...")
    sys.exit()

if current_version != latest_version:
    print(f"当前版本：{current_version}")
    print(f"最新版本：{latest_version}")
    print(f"更新地址：https://www.123pan.com/s/uyHuVv-5LyVH.html")
else:
    print(f"版本状态：当前为最新版本 v{current_version}")
print("使用文档：https://flowus.cn/share/0854d558-65c2-414e-bc88-832c7c62c070")
# 伪装浏览器
headers = {
    'Referer': 'https://jwc.htu.edu.cn/new/desktop',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 '
                  'Safari/537.36 Edg/114.0.1823.43 '
}
new_login_cookies = {
    'language': 'zh-CN',
}
new_login_headers = {
    'Referer': 'https://jwc.htu.edu.cn/app/?code',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 9; ASUS_X00TD; Flow) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/359.0.0.288 Mobile Safari/537.36',
}
# 请求在线人数的url
"""getOnlineMembers_response = json.loads(
    requests.post('https://jwc.htu.edu.cn/new/login/getOnlineMembers', headers=headers).text)
print(f"在线人数：{getOnlineMembers_response['data']}")"""

# 获取当前学期和需要保留的键
xq_keys = requests.get(gitee_url + '/xq_keys.json').json()
# 课程表 成绩用
xnxqdm = xq_keys['xnxqdm']
# 选课用
xnxqdm_xk = xq_keys['xnxqdm_xk']
xnxqdm_pj = xq_keys['xnxqdm_pj']
# 获取白名单
white = requests.get(gitee_url + '/whitenames.json').json()
white_names = white['whitenames']
valid_usernames = white['valid_usernames']
# 获取密码加密公钥
public_key = requests.get(gitee_url + '/publickey.txt').text
if not os.path.exists(r'./login_message'):
    os.makedirs('login_message')

if not os.path.exists("./login_message/login.json"):
    login_message = {
        "id": "",
        "pwd": "",
        "RSA_pwd": "",
        "cookies": "",
        "token": ""
    }
    with open("./login_message/login.json", "w") as file:
        file.write(json.dumps(login_message))
    file.close()
with open(r"./login_message/login.json", "r") as file:
    a = file.read()
if a != '':
    LOGIN = json.loads(a)
file.close()


# 保存账号密码
def file_save(path, text):
    with open(path, "w") as f:
        f.write(text)


# 保存文件
def renew_LOGIN(key, value):
    LOGIN[key] = value
    with open(r"./login_message/login.json", "w") as f:
        f.write(json.dumps(LOGIN))
    f.close()


# 如果登录成功获取用户的姓名
def get_name(cookies):
    logined_url = 'https://jwc.htu.edu.cn/new/welcome.page'
    try:
        logined_response = requests.get(url=logined_url, cookies=cookies).text
        root = html.fromstring(logined_response)
        name_elements = root.xpath('(//div[@class="top"])[1]/text()')
        if name_elements:
            name = name_elements[0].strip()
            if name in white_names:
                return name
            else:
                print("登录状态：登录失败！您可能没有使用权限！")
                renew_LOGIN('id', '')
                renew_LOGIN('pwd', '')
                return ""
        else:
            print("登录状态：登录失败！")
            return ""
    except:
        print("用户姓名获取请求失败，错误码：03")


# 获取课程的上课时间函数
def add_time(kcrwdm, cookies):
    res = requests.get('https://jwc.htu.edu.cn/new/student/xsxk/jxrl',
                       params={'xnxqdm': xnxqdm_xk, 'kcrwdm': kcrwdm, '_': int(time.time() * 1000)},
                       headers=headers, cookies=cookies).text  # 请求上课时间的url
    start_index = res.find("data: [")
    end_index = res.find("],", start_index) + 1

    if start_index != -1 and end_index != -1:
        data_json = res[start_index + len("data: "):end_index]
        data_list = json.loads(data_json)
        return data_list


# 获取可选的项目
def get_add(cookies):
    print("------------------------选课类型------------------------")
    response = requests.get('https://jwc.htu.edu.cn/new/student/xsxk/', cookies=cookies, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    urls2 = soup.select('div.layui-container div#bb2')
    titles2 = soup.select('div.layui-container div#bb2 div.content div.text span.title')
    description2 = soup.select('div.layui-container div#bb2 div.content div.text div.description')

    urls1 = soup.select('div.layui-container div#bb1')
    titles1 = soup.select('div.layui-container div#bb1 div.content div.text span.title')
    description1 = soup.select('div.layui-container div#bb1 div.content div.text div.description')
    urls = urls1 + urls2
    titles = titles1 + titles2
    description = description1 + description2
    able_select = 0
    if len(titles) != 0:
        for i in range(len(titles)):
            description_2 = re.sub(r"(>|<|h|r|b|\t|\r|\n)", '', urls[i].get('lay-tips'))
            print(f"课程类型：[{i + 1}]{titles[i].get_text()}")
            print(f"选课信息：{re.split('>|<', str(description[i]))[2]}--{re.split('>|<', str(description[i]))[4]}")
            print(f"选课学期：{description_2[5:16]}")
            print(f"选课状态：{description_2[16:]}")
            if re.split('>|<', str(description[i]))[2][0] == '不':
                able_select = able_select + 1
            print("--------")
        if able_select != 0:
            return "", ""
        else:
            count = int(input("请输入目标选课类型序号："))
            if len(urls) >= count >= 1:
                count = count
            else:
                count = 1
            print(f"你选择了{titles[count - 1].get_text()}")
            url = "https://jwc.htu.edu.cn" + urls[count - 1].get("data-href")
            start_time = re.split('>|<', str(description[count - 1]))[2]
            return url, start_time
    else:
        return "", ""


# 06 专业选修
# 02 体育专选
# 01 博约专选
# 07 文学专选


def save_details(save_keys_zh, kcmls):
    # 保存文件
    f = open('课程信息目录.csv', 'w')
    csv_write = csv.writer(f)
    csv_write.writerow(save_keys_zh)
    for kcml in kcmls:
        csv_write.writerow(kcml.values())
    f.close()
    os.startfile("课程信息目录.csv")
    print("已完成")
    print('你可以查看"课程信息目录.csv"辅助选课')


# 获取课程信息
def get_rows(url, cookies):
    # 获取课程信息
    data = {
        'page': '',
        'rows': '500',
        'sort': 'kcrwdm',
        'order': 'asc'
    }
    # 请求课程信息的url
    xx_url = url + '/kxkc'
    res = requests.post(url=xx_url, headers=headers, data=data, cookies=cookies).json()
    rows = res['rows']
    return rows


# 直接选课
def way_1(rows, url, cookies):
    print('------------------------直接选课------------------------')
    index = 1
    kcrwdms = []
    kcmcs = []
    for i in rows:
        last = str(int(i['pkrs']) - int(i['jxbrs']))
        print(
            f"[{index}] 课程名称：{i['kcmc']} 课程代码：{i['kcrwdm']} 教学班名称：{i['jxbmc']} 授课教师：{i['teaxm']} 课程板块：{i['kcflmc']} 学分：{i['xf']} 还有{last}个名额")
        index = index + 1
        kcrwdms.append(i['kcrwdm'])
        kcmcs.append(i['kcmc'])
    print(f"[0] 退出")
    kcrwdms_indexs = input("输入序号(多个序号以空格隔开)：").split(" ")
    kcrwdms_indexs = [int(kcrwdms_indexs) for kcrwdms_indexs in kcrwdms_indexs]
    for kcrwdms_index in kcrwdms_indexs:
        if len(rows) >= kcrwdms_index >= 1:
            # 调用选课函数开始选课
            # adding(cookies, 课程代码, url, 课程名称)
            adding(cookies, kcrwdms[kcrwdms_index - 1], url, kcmcs[kcrwdms_index - 1], 1)
        else:
            if kcrwdms_index == 0:
                fun(cookies)
            else:
                print("输入的序号无效，请重新输入！")


# 定时选课
def way_2(start_time, url, cookies):
    print("------------------------定时选课------------------------")
    print("请查看“课程信息目录.csv”辅助选课")
    kcrwdms = input("输入目标选课的课程代码：").split(" ")
    kcmcs = input("输入目标选课的课程名称：").split(" ")
    if '0' <= start_time.split("%c")[0] <= '9':
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    else:
        print("选课未开始")
        start_time = input("预定开始时间(如：13:30:00)：")
        start_time = datetime.strptime(start_time, '%H:%M:%S')
    print(f"选课时间：{start_time}")
    kcrwdms = [int(kcrwdms) for kcrwdms in kcrwdms]
    for i in range(len(kcrwdms)):
        # 获取预定的时间
        # time_object = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        hour = start_time.hour
        minute = start_time.minute
        # 获取当前时间
        current_time = datetime.now().replace(microsecond=0)
        print(f"当前时间：{current_time}")
        # 判断输入的时间是否合法，小时大于等于当前，分钟大于当前
        if hour < current_time.hour or minute <= current_time.minute:
            adding(cookies, kcrwdms[i], url, kcmcs[i], 1)
        else:
            desired_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            time_to_wait = (desired_time - current_time).total_seconds()
            print("正在等待达到选课时间...")
            time.sleep(time_to_wait)
            # 调用adding选课函数开始选课
            adding(cookies, kcrwdms[i], url, kcmcs[i], 1)


# 已选课程
def way_3(url, cookies):
    print("------------------------已选课程------------------------")
    added_response = requests.post(url + '/yxkc', data={'sort': ' kcrwdm', 'order': 'asc'}, cookies=cookies,
                                   headers=headers).json()
    rows = added_response['rows']
    if len(rows) != 0:
        for i in rows:
            print(i['kcrwdm'] + i['kcmc'])
    else:
        print("当前类型没有已选课程")


# 下载课程信息
def way_4(rows, cookies):
    print("------------------------课程信息------------------------")
    print("正在生成信息文件，请稍后...")
    if len(rows) != 0:
        # 课程代码列表
        kcdm = []
        # 遍历所有课程 获取课程代码
        for row in rows:
            kcdm.append(row['kcrwdm'])
        index = 1
        # 每一个课程的所有键
        sum_keys = []
        if len(add_time(kcdm[0], cookies)) != 0:
            for key in add_time(kcdm[0], cookies)[-1].keys():
                sum_keys.append(key)
            # 需要保留的键
            save_keys = xq_keys['save_keys']
            # 获取需要删除的键值
            delete_keys = list(set(sum_keys) - set(save_keys))
            # 格式化后的课程信息
            kcmls = []
            # 遍历每一个课程代码
            for i in range(len(kcdm)):
                # 获取每一个课程代码的具体信息
                timecs = add_time(kcdm[i], cookies)
                print(f"[{i}] {kcdm[i]}")
                if len(timecs) != 0:
                    zc = timecs[0]['zc'] + '-' + timecs[-1]['zc']
                    jcdm2 = timecs[0]['jcdm2']
                    xq = timecs[0]['xq']
                    rows[i]['zc'] = zc
                    rows[i]['jcdm2'] = jcdm2
                    rows[i]['xq'] = xq
                    # 删除键
                    """for j in delete_keys:
                        rows[i].pop(j, f'没有{j}')"""
                index = index + 1
            save_details(rows[0].keys(), rows)
        else:
            save_details(rows[0].keys(), rows)
    else:
        print("课程信息为空，生成失败")


# 搜索课程
def way_5(url, cookies):
    print("------------------------搜索课程------------------------")
    searchKeys = ['kcmc', 'kcflmc', 'jxbmc', 'teaxm']
    print("[1]课程名称  [2]课程分类  [3]教学班名称  [4]教师名称")
    searchKey = int(input("输入搜索分类序号："))
    searchValue = input("模糊搜索：")
    true = 1
    while true == 1:
        data = {'searchKey': searchKeys[searchKey - 1], 'searchValue': searchValue, 'page': '1', 'rows': '400',
                'sort': 'kcrwdm', 'order': 'asc', }
        search_response = requests.post(url + '/kxkc', data=data, cookies=cookies,
                                        headers=headers).json()
        rows = search_response['rows']
        if len(rows) != 0:
            for i in rows:
                print(f"{i['teaxm']} {i['kcmc']} {i['kcflmc']} {i['jxbmc']}")
                adding(cookies, i['kcrwdm'], url, i['kcmc'], 0)
        else:
            print("当前搜索目标没有课程")
            true = 0


# 暴力选课
def way_6(url, cookies):
    print("------------------------暴力选课------------------------")
    while True:
        rows = get_rows(url, cookies)
        for i in rows:
            if i['pkrs'] - int(i['jxbrs']) == 0:
                print(f"{i['kcmc']}")
                adding(cookies, i['kcrwdm'], url, i['kcmc'], 0)


# 筛选课程函数
def add(cookies):
    global kcmc
    print("------------------------选课辅助------------------------")
    print("当前时间：" + time.strftime('%Y-%m-%d %H:%M:%S'))
    url, start_time = get_add(cookies)
    if url == "" and start_time == "":
        print("当前不是选课时间！")
    else:
        kind_url = url.split("/")[-1]
        rows = get_rows(url, cookies)
        if len(rows) != 0:
            way = 0
            while way == 0:
                print("------------------------选课方式------------------------")
                print('[1]直接选课 [2]定时选课 [3]课程信息 [4]已选课程 [5]搜索课程\n[6]暴力选课 [7]退出选课')
                add_way = input("输入数字：")
                # 直接选课
                if add_way == '1':
                    way_1(rows, url, cookies)
                # 定时课程
                elif add_way == '2':
                    way_2(start_time, url, cookies)
                # 已选课程
                elif add_way == '4':
                    way_3(url, cookies)
                # 课程信息
                elif add_way == '3':
                    way_4(rows, cookies)
                # 搜索课程
                elif add_way == '5':
                    way_5(url, cookies)
                # 暴力选课
                elif add_way == '6':
                    way_6(url, cookies)
                # 退出选课
                else:
                    fun(cookies)
                    way = 1
        else:
            print("请先检查是否具有选择该类型课程的权限！")


# 抢课函数
def adding(cookies, kcrwdm, url, kcmc, ifwhile):
    lx = url.split("/")[-1]
    data = {
        'kcrwdm': kcrwdm,
        'kcmc': kcmc,
        'qz': '-1',
        'hlct': '0'
    }
    i = 0
    while True:
        try:
            res_add = requests.post(url=url + '/add', headers=headers, data=data, cookies=cookies).json()
            print(res_add)  # 输出结果
            if res_add['message'] == '没有开设该课程':
                break
            time.sleep(1)
        except Exception as r:
            print("重试...")
        if ifwhile == 0:
            break


# 程序可能运行出的结果如下：
# {"code":-1,"data":"","message":"《NULL》 与 您的《数学分析Ⅱ》上课时间有冲突"}
# {"code":-1,"data":"","message":"选课人数超出，请选其他课程"}
# {"code": 0,"data":"","message":"选课成功"}
# {"code": -1,"data":"","message":"没有开设该课程"}

# 获取课程表函数
def getCalendarWeekDatas(cookies):
    print("------------------------课表查询------------------------")
    data = {
        'xnxqdm': xnxqdm,
        'zc': '',
        'd1': '2023-08-14 00:00:00',
        'd2': '2023-08-21 00:00:00',
    }
    getCalendarWeekDatas = \
        requests.post('https://jwc.htu.edu.cn/new/student/xsgrkb/getCalendarWeekDatas', cookies=cookies,
                      headers=headers, data=data).json()['data']
    # 创建一个空字典，用于储存xq
    xqs = {}
    # 遍历列表中的字典
    for getCalendarWeekData in getCalendarWeekDatas:
        xq_value = getCalendarWeekData["xq"]
        if xq_value in xqs:
            xqs[xq_value].append(getCalendarWeekData)
        else:
            xqs[xq_value] = [getCalendarWeekData]
    # 对xqs中的数排序
    sorted_xqs = sorted(xqs.keys())
    # 顺序输出每天的课程
    for xq in sorted_xqs:
        print(f"星期{xq}:")
        for getCalendarWeekData in xqs[xq]:
            weekdays = getCalendarWeekData['zc'].split(",")
            weekdays = [int(weekday) for weekday in weekdays]
            print(
                f"课程名称：{getCalendarWeekData['kcmc']}  授课教师：{getCalendarWeekData['teaxms']} 上课地点：{getCalendarWeekData['jxcdmc']}  上课周数：{min(weekdays)}-{max(weekdays)}周")
        print("------------------------")


def convert_to_fullwidth(input_str):
    fullwidth_str = ''
    for char in input_str:
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            # If character is fullwidth, keep it as is
            fullwidth_str += char
        else:
            # Convert halfwidth character to fullwidth
            fullwidth_str += chr(ord(char) + 0xFEE0)
    return fullwidth_str


# 获取考试成绩函数
def score(cookies):
    print("------------------------课程成绩------------------------")
    print("大一第二学期就输入 202202，点击回车输出当前学期")
    term_xnxqdm = input("请输入：")
    if term_xnxqdm == "":
        term_xnxqdm = xnxqdm_pj
    else:
        term_xnxqdm = int(term_xnxqdm)
    data = {
        'source': 'kccjlist',
        'xnxqdm': term_xnxqdm
    }
    score_response = \
        requests.post('https://jwc.htu.edu.cn/new/student/xskccj/kccjDatas', cookies=cookies, headers=headers,
                      data=data).json()["rows"]
    if len(score_response) != 0:
        cjjd_sum = 0  # 绩点总和
        cjxf_sum = 0  # 学分总和
        jd_xf_sum = 0  # 绩点乘以学分
        pj_index = 0  # 序号
        for scores in score_response:
            pj_index = pj_index + 1
            scores['kcmc'] = str.replace(scores['kcmc'], "Ⅳ", '四')
            scores['kcmc'] = str.replace(scores['kcmc'], "Ⅱ", '二')
            scores['kcmc'] = str.replace(scores['kcmc'], "Ⅲ", '三')
            scores['kcmc'] = str.replace(scores['kcmc'], "Ⅰ", '一')
            scores['kcmc'] = str.replace(scores['kcmc'], "Ｉ", '一')
            scores['kcmc'] = str.replace(scores['kcmc'], " ", '')
            scores['kcmc'] = convert_to_fullwidth(scores['kcmc'])
            print(
                "[{:<2}] 课程名称: {:\u3000<11} 总成绩: {:.2f}  绩点: {:.2f}  学分：{:}".format(pj_index, scores['kcmc'],
                                                                                               float(scores['zcjfs']),
                                                                                               float(scores['cjjd']),
                                                                                               format(scores['xf'])))
            cjjd_sum = cjjd_sum + scores['cjjd']
            cjxf_sum = cjxf_sum + scores['xf']
            jd_xf_sum = scores['cjjd'] * scores['xf'] + jd_xf_sum
        print('平均绩点：{:.2f} (每门课程绩点×课程学分的和/总学分)'.format(jd_xf_sum / cjxf_sum))
    else:
        print("当前学期没有成绩")


# 密码加密函数
def encrpt(pwd, publickey):
    publickey = '-----BEGIN PUBLIC KEY-----\n' + publickey + '\n-----END PUBLIC KEY-----'
    rsakey = RSA.importKey(publickey)
    cipher = Cipher_pksc1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(pwd.encode()))
    renew_LOGIN("RSA_pwd", cipher_text.decode())
    return cipher_text.decode()


# 判断新版教务是否处于登录状态
def new_if_logined():
    if LOGIN['token'] != '':
        token = LOGIN['token']
        login_headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; ASUS_X00TD; Flow) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/359.0.0.288 Mobile Safari/537.36',
            'token': token,
        }
        json_data = {}
        response = requests.post('https://jwc.htu.edu.cn/dev-api/appapi/getNotice', cookies=new_login_cookies,
                                 headers=login_headers,
                                 json=json_data)
        if response.json()['code'] == 401:
            token = new_jw()['user']['token']
    else:
        token = new_jw()['user']['token']
    return token


# 智慧教务获取学分
def haved_score():
    token = new_if_logined()
    print("------------------------已修学分------------------------")
    login_data = {}
    login_headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 9; ASUS_X00TD; Flow) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/359.0.0.288 Mobile Safari/537.36',
        'token': token,
    }
    session_2 = requests.Session()
    score_message = session_2.post('https://jwc.htu.edu.cn/dev-api/appapi/Studentcj/kcdlxfDatas',
                                   cookies=new_login_cookies,
                                   headers=login_headers,
                                   json=login_data)
    if score_message.json()['code'] == 401:
        new_jw()
    elif score_message.json()['code'] == 200:
        index = 1
        sum_xf = 0
        for i in score_message.json()['list']:
            print(f"[{index}] {i['kcdlmc']} {i['xf']}分")
            index = index + 1
            sum_xf = sum_xf + i['xf']
        print(f"已修学分：{sum_xf}")
    else:
        print("查询失败！")


# 教学评价
def teacher_pj():
    token = new_if_logined()
    print("------------------------教学评价------------------------")
    json_data = {
        'xnxqdm': xnxqdm_pj,
    }
    login_headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 9; ASUS_X00TD; Flow) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/359.0.0.288 Mobile Safari/537.36',
        'token': token,
    }
    all_courses = requests.post('https://jwc.htu.edu.cn/dev-api/appapi/Studentpjwj/teacher', cookies=new_login_cookies,
                                headers=login_headers, json=json_data).json()
    # 未安排评价时间 200
    # 请登录 401
    #
    if all_courses['code'] == 401:
        new_jw()
    if all_courses['code'] == 200:
        print(f"评价时间：{all_courses['msg']}")
        y = input("输入[y/Y/回车]确认开始自动评价当前学期：")
        json_data_1 = requests.get(gitee_url + '/pj_details_1.json')  # 理论课
        json_data_2 = requests.get(gitee_url + '/pj_details_2.json')  # 实验课
        if y == 'y' or "Y" or "":
            print("已开始（每门课程评价后延迟5秒）")
            dgksdms = []
            teadm = []
            kcrwdms = []
            index = 0
            for i in all_courses['allPjxxList']:
                i['kcmc'] = str.replace(i['kcmc'], " ", '')
                if i['pjdm'] != '':
                    index = index + 1
                    i['kcmc'] = str.replace(i['kcmc'], "Ⅳ", '四')
                    i['kcmc'] = str.replace(i['kcmc'], "Ⅱ", '二')
                    i['kcmc'] = str.replace(i['kcmc'], "Ⅲ", '三')
                    i['kcmc'] = str.replace(i['kcmc'], "Ⅰ", '一')
                    i['kcmc'] = str.replace(i['kcmc'], "Ｉ", '一')
                    i['kcmc'] = str.replace(i['kcmc'], " ", '')
                    i['kcmc'] = convert_to_fullwidth(i['kcmc'])
                    print("[{:<2}] {:\u3000<3} {:\u3000<12} 已评价".format(index, i['teaxm'], i['kcmc']))
                if i['pjdm'] == '':
                    dgksdms.append(i['dgksdm'])
                    teadm.append(i['teadm'])
                    kcrwdms.append(i['kcrwdm'])
            if len(dgksdms) != 0:
                for i in range(len(dgksdms)):
                    json_data = {
                        'dgksdm': dgksdms[i],
                        'teadm': teadm[i],
                    }
                    teachers_detail = requests.post('https://jwc.htu.edu.cn/dev-api/appapi/Studentpjwj/pjTea',
                                                    cookies=new_login_cookies,
                                                    headers=login_headers, json=json_data)
                    json_data_detail = teachers_detail.json()['skInfo']
                    if json_data_detail['jxhjmc'] == '理论':
                        json_data = json_data_1
                    else:
                        json_data = json_data_2
                    pj = requests.post('https://jwc.htu.edu.cn/dev-api/appapi/Studentpjwj/saveTeaPj',
                                       cookies=new_login_cookies,
                                       headers=login_headers, json=json_data)
                    print(pj.json())
                    if pj.json()['msg'] == 'app_retrun_success_saveTeaPj':
                        print(
                            f"{json_data_detail['teaxm']} {json_data_detail['jxhjmc']} {json_data_detail['kcmc']} 评价成功")
                    time.sleep(5)
                print("评价状态：评价已完成")
            else:
                print("评价状态：所有课程均已评价")
    else:
        print(f"评价状态：{all_courses['msg']}")


# 智慧教务获取个人信息
def person_message():
    login_message = new_jw()
    print("------------------------登录信息------------------------")
    if login_message['code'] != 200:
        print("获取个人信息失败，请重新登录...")
        main()
    elif login_message['code'] == 200:
        print(f"用户姓名：{login_message['user']['userxm']}")
        print(f"用户学号：{login_message['user']['userAccount']}")
        print(f"学院名称：{login_message['user']['userdwmc']}")
        print(f"身份证号：{login_message['user']['usersfzh']}")
        print(f"电话号码：{login_message['user']['userdh']}")
        print(f"登录时间：{login_message['user']['loginTime']}")
        print(f"登录地点：{login_message['user']['loginIp']}")


# 智慧教务登录
def new_jw():
    if LOGIN['id'] != '':
        xh = LOGIN['id']
    else:
        xh = "0000000000"
    if LOGIN['RSA_pwd']:
        key_password = LOGIN['RSA_pwd']
    else:
        key_password = "0000000000"
    login_data = {
        'username': xh,
        'password': key_password,
        'code': '',
        'appid': None,
    }
    session_2 = requests.Session()
    new_jw_url = 'https://jwc.htu.edu.cn/dev-api/appapi/applogin'

    login_message = session_2.post(url=new_jw_url, cookies=new_login_cookies, headers=new_login_headers,
                                   json=login_data)
    if login_message.json()['code'] == 200:
        renew_LOGIN("token", login_message.json()['user']['token'])
        return login_message.json()


# 菜单函数
def fun(cookies):
    while True:
        print('------------------------选择功能------------------------')
        print("""[1]选课辅助 [2]课表查询 [3]课程成绩 [4]已修学分 [5]登录信息
[6]教学评价 [7]退出程序 [8]退出登录""")
        choice = input("输入数字：")
        if choice == '1':
            add(cookies)
        elif choice == '2':
            getCalendarWeekDatas(cookies)
        elif choice == '3':
            score(cookies)
        elif choice == '7':
            input("按回车键退出...")
            sys.exit()
        elif choice == '8':
            renew_LOGIN('id', '')
            renew_LOGIN('pwd', '')
            renew_LOGIN('cookies', '')
            renew_LOGIN('RSA_pwd', '')
            renew_LOGIN('token', '')
            print("已退出登录！")
            main()
        elif choice == '5':
            person_message()
            username(0)
        elif choice == '4':
            haved_score()
            username(0)
        elif choice == '6':
            teacher_pj()
            username(0)
        elif choice == '':
            input("按回车键退出...")
            sys.exit()
        else:
            input("按回车键退出...")
            sys.exit()


# 读取本地Cookies
def cookies_read():
    if LOGIN['cookies'] != '':
        jsessionid = LOGIN['cookies']
        cookies = {
            "JSESSIONID": jsessionid
        }
        name = get_name(cookies)
        if name != "":
            print(f"用户姓名：{name}")
            fun(cookies)
            return cookies
        else:
            main()
    # 本地cookies为空
    else:
        if LOGIN['pwd'] != '':
            username(1)
        else:
            main()


# 密码登录
def username(ifname):
    # 输入登录信息
    valid_usernames = requests.get(gitee_url + "/whitenames.json").json()['valid_usernames']
    if LOGIN['id'] != '' and LOGIN['pwd'] != '':
        password = LOGIN['pwd']
        username = LOGIN['id']
    else:
        print("------------------------密码登录------------------------")
        username = input("输入学号：")
        password = input("输入密码：")
        renew_LOGIN('id', username)
        renew_LOGIN('pwd', password)

    # 获取cookies
    jsessionid_response = requests.post('https://jwc.htu.edu.cn')
    jsessionid = jsessionid_response.cookies.get("JSESSIONID")

    cookies = {
        "JSESSIONID": jsessionid,
    }

    # 获取验证码图片
    verifycode_url = 'https://jwc.htu.edu.cn/yzm?' + str(int(time.time() * 1000 + 3))
    verifycode_response = requests.get(url=verifycode_url, cookies=cookies).content
    # 保存验证码图片
    with open(r'./login_message\verifycode_image.jpg', 'wb') as f:
        f.write(verifycode_response)

    # 识别验证码函数
    def base64_api(uname, pwd, img, typeid):
        with open(img, 'rb') as f_code:
            base64_data = base64.b64encode(f_code.read())
            b64 = base64_data.decode()
        data = {"username": uname, "password": pwd, "typeid": typeid, "image": b64}
        result = json.loads(requests.post("http://api.ttshitu.com/predict", json=data).text)
        if result['success']:
            return result["data"]["result"]
        else:
            return result["message"]

    # 调用函数识别
    img_path = r"./login_message\verifycode_image.jpg"
    verifycode = base64_api(uname='Jialifuniya', pwd='zxcvbnm123', img=img_path, typeid=3)
    if len(verifycode) == 4:
        os.remove(img_path)
    else:
        verifycode = 'abcd'

    # 密码加密使用了aes.js文件
    try:
        aes_response = requests.get(gitee_url + '/aes.js')
    except:
        print("aes.js请求失败，错误码：02")
    with open(r'./login_message\aes.js', 'wb') as js_file:
        js_file.write(aes_response.content)
    # 读取 JavaScript 代码
    js_file_path = r'./login_message\aes.js'
    # 检查文件是否存在
    if os.path.exists(js_file_path):
        with open(js_file_path, 'r') as js_file:
            js_code = js_file.read()
    else:
        print("密码加密失败，请使用Cookies登录")
        jsession()

    # 替换 JavaScript 代码中的变量
    js_code = js_code.replace('var account = "";', f'var account = "{username}";')
    js_code = js_code.replace('var password = "";', f'var password = "{password}";')
    js_code = js_code.replace('var verifycode = "";', f'var verifycode = "{verifycode}";')

    # 使用 js2py 执行 JavaScript 代码
    password_key = eval_js(js_code)
    # print("加密后的密码为："+password_key)
    os.remove(js_file_path)
    js_file.close()
    login_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58',
    }
    # 构造登录请求的参数
    login_data = {
        'account': username,
        'pwd': password_key,
        'verifycode': verifycode
    }
    # 发送登录请求
    login_url = 'https://jwc.htu.edu.cn/new/login'  # 替换为实际的登录页面URL
    try:
        login_response = requests.post(url=login_url, data=login_data, headers=login_headers, cookies=cookies)
    except:
        print("账号密码登录请求失败，错误码：01")
    name = get_name(cookies)
    if name != "":
        if ifname == 1:
            print(f"用户姓名：{name.strip()}")
            print(f"登录状态：{login_response.json()['message']}")
        # print("Cookies:"+jsessionid)
        encrpt(password, public_key)
        renew_LOGIN('cookies', jsessionid)
        fun(cookies)
        return cookies
    else:
        print(login_response.json()['message'] + "，请检查后重新输入！")
        renew_LOGIN('id', '')
        renew_LOGIN('pwd', '')
        main()


# Cookies登录
def jsession():
    print("-----------------------Cookies登录---------------------")
    jsessionid = input("请输入Cookies：")
    cookies = {
        "JSESSIONID": jsessionid,
    }
    name = get_name(cookies)
    if name != "":
        print("登录状态：登录成功！")
        renew_LOGIN('cookies', jsessionid)
        return cookies
    else:
        main()


# 登录函数
def main():
    print("------------------------登录系统------------------------")
    print("[1]密码登录   [2]Cookies登录   [3]清除信息   [4]退出程序")
    login_way = input("选择登录方式：")
    if login_way == '1':
        cookies = username(1)
        fun(cookies)
    elif login_way == '2':
        cookies = jsession()
        fun(cookies)
    elif login_way == '3':
        renew_LOGIN('id', '')
        renew_LOGIN('pwd', '')
        renew_LOGIN('cookies', '')
        renew_LOGIN('RSA_pwd', '')
        renew_LOGIN('token', '')
        print("已清除")
        main()
    elif login_way == '':
        input("按回车键退出...")
        sys.exit()
    else:
        input("按回车键退出...")
        sys.exit()


if __name__ == "__main__":
    cookies = cookies_read()
