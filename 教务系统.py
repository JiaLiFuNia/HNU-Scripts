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
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pksc1_v1_5
from Crypto.PublicKey import RSA
from bs4 import BeautifulSoup
from js2py import eval_js
from lxml import html

print("------------------------欢迎使用------------------------")
current_version = 5.3
gitee_url = 'https://gitee.com/xhand_xbh/hnu/raw/master'
try:
    res_version = requests.get(gitee_url + "/htu_version.json")
    latest_version = res_version.json()['version']
except Exception as e:
    print("无网络链接!请连接网络后，重试！")
    input("按回车键退出...")
    sys.exit()

if current_version < latest_version:
    print(f"当前版本：{current_version}")
    print(f"最新版本：{latest_version}")
    print(f"更新地址：https://www.123pan.com/s/uyHuVv-5LyVH.html")
else:
    print("版本状态：当前为最新版本")
print("使用文档：https://flowus.cn/share/0854d558-65c2-414e-bc88-832c7c62c070")
print("开源地址：")
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
getOnlineMembers_response = json.loads(
    requests.post('https://jwc.htu.edu.cn/new/login/getOnlineMembers', headers=headers).text)
print(f"在线人数：{getOnlineMembers_response['data']}")

# 获取当前学期和需要保留的键
xq_keys = requests.get(gitee_url + '/xq_keys.json').json()
xnxqdm = xq_keys['xnxqdm']
# 获取白名单
white = requests.get(gitee_url + '/whitenames.json').json()
white_names = white['whitenames']
valid_usernames = white['valid_usernames']
# 获取密码加密公钥
public_key = requests.get('https://gitee.com/xhand_xbh/hnu/raw/master/publickey.txt').text
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


# 保存Cookies
def cookies_save(text):
    with open(r"./login_message/cookies.txt", 'w') as file:
        file.write(text)


# 保存账号密码
def file_save(path, text):
    with open(path, "w") as file:
        file.write(text)


# 保存文件
def renew_LOGIN(key, value):
    LOGIN[key] = value
    with open(r"./login_message/login.json", "w") as f:
        f.write(json.dumps(LOGIN))
    f.close()


# 如果登录成功获取用户的姓名
def get_name(cookies):
    logined_url = 'https://jwc.htu.edu.cn/new/welcome.page'
    logined_response = requests.get(url=logined_url, cookies=cookies).text
    root = html.fromstring(logined_response)
    name_elements = root.xpath('(//div[@class="top"])[1]/text()')
    return name_elements


# 获取课程的上课时间函数
def add_time(kcrwdm, cookies):
    res = requests.get('https://jwc.htu.edu.cn/new/student/xsxk/jxrl',
                       params={'xnxqdm': xnxqdm, 'kcrwdm': kcrwdm, '_': int(time.time() * 1000)},
                       headers=headers, cookies=cookies).text  # 请求上课时间的url
    start_index = res.find("data: [")
    end_index = res.find("]", start_index) + 1

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
    if len(titles) != 0:
        for i in range(len(titles)):
            print(f"课程类型:[{i + 1}]{titles[i].get_text()}")
            print(f"选课信息:{re.split('>|<', str(description[i]))[2]}--{re.split('>|<', str(description[i]))[4]}")
            print("----")
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
        # 获取课程信息
        data = {
            'page': '',
            'rows': '300',
            'sort': 'kcrwdm',
            'order': 'asc'
        }
        # 请求课程信息的url
        xx_url = url + '/kxkc'
        res = requests.post(url=xx_url, headers=headers, data=data, cookies=cookies).json()
        rows = res['rows']
        if len(rows) != 0:
            print("------------------------选课方式------------------------")
            print('[1]直接选课 [2]定时选课 [3]课程信息 [4]已选课程 [5]退出选课')
            add_way = int(input("输入数字："))
            # 直接选课
            if add_way == 1:
                print('-----------------------直接选课-----------------------')
                """print('''一、博约核心
            0.公共艺术   1.创新创业   2.健康人生
            3.科学思维   4.国际视野   5.社会人文
        二、博约百花
            6.人文科学   7.社会科学   8.自然科学
        三、博约经典
            9.博约经典''')
                kclxs = ['公共艺术', '创新创业', '健康人生', '科学思维', '国际视野', '社会人文', '人文科学', '社会科学',
                         '自然科学', '博约经典']
                print('''   如选择博约百花（人文科学），请输入6；
                  输入其他数字默认为博约经典；''')
                # 输入选课类型
                kclxnum = int(input("输入数字："))
                kcflmc = kclxs[kclxnum]
                print('你选择了' + kcflmc)
                print('请输入目标选课的上课时间（如：周5的第07,08节课，就输入5和07,08）')
                zc_input = int(input("星期几（如:4）："))
                jcdm2_input = input("第几节课（如:07,08）：")"""
                index = 1
                kcrwdms = []
                kcmcs = []
                for i in rows:
                    last = str(int(i['pkrs']) - int(i['jxbrs']))
                    print(
                        f"[{index}] 课程名称：{i['kcmc']} 课程代码：{i['kcrwdm']} 课程板块：{i['kcflmc']} 学分：{i['xf']} 还有{last}个名额")
                    index = index + 1
                    kcrwdms.append(i['kcrwdm'])
                    kcmcs.append(i['kcmc'])
                print(f"[{index}] 退出")
                kcrwdms_indexs = input("输入序号(多个序号以空格隔开)：").split(" ")
                kcrwdms_indexs = [int(kcrwdms_indexs) for kcrwdms_indexs in kcrwdms_indexs]
                print(kcrwdms_indexs)
                for kcrwdms_index in kcrwdms_indexs:
                    if len(rows) >= kcrwdms_index >= 1:
                        # 调用选课函数开始选课
                        # adding(cookies, 课程代码, url, 课程名称)
                        adding(cookies, kcrwdms[kcrwdms_index - 1], url, kcmcs[kcrwdms_index - 1])
                    else:
                        if kcrwdms_index == len(rows) + 1:
                            fun(cookies)
                        else:
                            print("输入的序号无效，请重新输入！")
                    # 循环输出符合条件的课程基本信息
                    '''kcrwdms = []
                    index = 1
                    for i in rows:
                        last = str(int(i['pkrs']) - int(i['jxbrs']))
                        if last != '0':
                            if i['kcflmc'] == kcflmc:
                                # 通过调用fore_add课程时间的函数，请求上课的具体时间
                                data_list = add_time(i['kcrwdm'], cookies)
                                if zc_input == data_list[0]['zc'] and jcdm2_input == data_list[0]['jcdm2']:
                                    print(
                                        str(index) + " 课程名称：" + i['kcmc'] + " 课程代码：" + str(i['kcrwdm']) + " 课程板块：" +
                                        i[
                                            'kcflmc'] + " 学分：" + str(
                                            i['xf']) + " 还有" + last + "个名额" + " 该课程共有" + str(
                                            data_list[-1]['kxh']) + "节课，" + '第' + str(data_list[0]['zc']) + '-' + str(
                                            data_list[-1]['zc']) + '周的' + '星期' + str(data_list[0]['xq']) + '的第' + str(
                                            data_list[0]['jccdm2']) + '节要上课')
                                    i['kcrwdm'].append(kcrwdms)
                                else:
                                    print("当前时间段没有目标类型的课程！")
                                add(cookies)'''
            # 定时课程
            elif add_way == 2:
                print("------------------------定时选课------------------------")
                kcrwdms = input("输入目标选课的课程代码：").split(" ")
                kcmcs = input("输入目标选课的课程名称：").split(" ")
                print(f"选课时间：{start_time}")
                kcrwdms = [int(kcrwdms) for kcrwdms in kcrwdms]
                kcmcs = [int(kcmcs) for kcmcs in kcmcs]
                for i in range(len(kcrwdms)):
                    # 获取预定的时间
                    time_object = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                    hour = time_object.hour
                    minute = time_object.minute
                    # 获取当前时间
                    current_time = datetime.now().replace(microsecond=0)
                    print(f"当前时间：{current_time}")
                    # 判断输入的时间是否合法，小时大于等于当前，分钟大于当前
                    if hour < current_time.hour or minute <= current_time.minute:
                        adding(cookies, kcrwdms[i], url, kcmcs[i])
                    else:
                        desired_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        time_to_wait = (desired_time - current_time).total_seconds()
                        print("正在等待达到选课时间...")
                        time.sleep(time_to_wait)
                        # 调用adding选课函数开始选课
                        adding(cookies, kcrwdms[i], url, kcmcs[i])
            # 已选课程
            elif add_way == 4:
                print("------------------------已选课程------------------------")
                added_response = requests.post(url + '/yxkc', data={'sort': ' kcrwdm', 'order': 'asc'}, cookies=cookies,
                                               headers=headers).json()
                rows = added_response['rows']
                if len(rows) != 0:
                    for i in rows:
                        print(i['kcrwdm'] + i['kcmc'])
                else:
                    print("当前类型没有已选课程")
            # 课程信息
            elif add_way == 3:
                print("------------------------课程信息------------------------")
                print("正在生成信息文件，请稍后...")
                # 课程代码列表
                kcdm = []
                # 遍历所有课程 获取课程代码
                for row in rows:
                    kcdm.append(row['kcrwdm'])
                index = 1
                # 每一个课程的所有键
                sum_keys = []
                for key in add_time(kcdm[0], cookies)[-1].keys():
                    sum_keys.append(key)
                # 需要保留的键
                save_keys = xq_keys['save_keys']
                # 修改键名称
                save_keys_zh = xq_keys['save_keys_zh']
                # 获取需要删除的键值
                delete_keys = list(set(sum_keys) - set(save_keys))
                # 格式化后的课程信息
                kcmls = []
                if len(add_time(kcdm[0], cookies)) != 0:
                    # 遍历每一个课程代码
                    for i in kcdm:
                        # 获取每一个课程代码的具体信息
                        timec = add_time(i, cookies)[-1]
                        # 删除键
                        for j in delete_keys:
                            timec.pop(j, '没有该键')
                            kcmls.append(timec)
                        print(f"[{index}] {timec}")
                        index = index + 1
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
                else:
                    print("课程信息为空，生成失败")
                fun(cookies)
            # 退出选课
            else:
                fun(cookies)
        else:
            print("请先检查是否具有选择该类型课程的权限！")


# 抢课函数
def adding(cookies, kcrwdm, url, kcmc):
    lx = url.split("/")[-1]
    data = {
        'kcrwdm': kcrwdm,
        'kcmc': kcmc,
        'qz': '-1',
        'hlct': '0'
    }
    # 请求选课的url
    res_add = requests.post(url=url + '/add', headers=headers, data=data, cookies=cookies).json()
    code = res_add['code']
    print(res_add['message'], code)  # 输出结果


# 程序可能运行出的结果如下：
# {"code":-1,"data":"","message":"《NULL》 与 您的《数学分析Ⅱ》上课时间有冲突"}
# {"code":-1,"data":"","message":"选课人数超出，请选其他课程"}
# {"code": 0,"data":"","message":"选课成功"}


# 获取课程表函数
def getCalendarWeekDatas(cookies):
    get_name(cookies)
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
        print("-------------------------")


# 获取考试成绩函数
def score(cookies):
    get_name(cookies)
    print("------------------------课程成绩------------------------")
    term_xnxqdm = int(input("请输入要查询的学期（示例：大一第二学期就输入 202202）："))
    data = {
        'source': 'kccjlist',
        'xnxqdm': term_xnxqdm
    }
    score_response = \
        requests.post('https://jwc.htu.edu.cn/new/student/xskccj/kccjDatas', cookies=cookies, headers=headers,
                      data=data).json()["rows"]
    if len(score_response) != 0:
        cjjd_sum = 0
        cjjd_index = 0
        for scores in score_response:
            cjjd_index = cjjd_index + 1
            print("[{:<2}] 课程名称: {:<15}总成绩: {:<10}绩点: {:<5}".format(cjjd_index, scores['kcmc'], scores['zcj'],
                                                                             scores['cjjd']))
            cjjd_sum = cjjd_sum + scores['cjjd']
        print(f'平均绩点为：{cjjd_sum / cjjd_index}')
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


# 智慧教务获取学分
def haved_score():
    if LOGIN['token'] != '':
        token = LOGIN['token']
    else:
        token = new_jw()['user']['token']
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
    if score_message.json()['code'] == 200:
        index = 1
        for i in score_message.json()['list']:
            print(f"[{index}] {i['kcdlmc']} {i['xf']}分")
            index = index + 1
    else:
        print("查询失败！")


# 教学评价
def teacher_pj():
    if LOGIN['token'] != '':
        token = LOGIN['token']
    else:
        token = new_jw()['user']['token']
    print("------------------------教学评价------------------------")
    json_data = {
        'xnxqdm': xnxqdm,
    }
    login_headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 9; ASUS_X00TD; Flow) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/359.0.0.288 Mobile Safari/537.36',
        'token': token,
    }
    response = requests.post('https://jwc.htu.edu.cn/dev-api/appapi/Studentpjwj/teacher', cookies=new_login_cookies,
                             headers=login_headers, json=json_data).json()

    if response['msg'] == '未安排评价时间':
        print(f"评价状态：{response['msg']}，请等待教务处通知")
    else:
        print(f"评价状态：{response['msg']}")
        y = input("输入[y/Y/回车]开始自动评价当前学期：")
        if y == 'y' or "Y" or "\n":
            print("已开始")


# 智慧教务获取个人信息
def person_message():
    login_message = new_jw()
    print("------------------------登录信息------------------------")
    if login_message['code'] == 500:
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
            username()
        elif choice == '4':
            haved_score()
            username()
        elif choice == '6':
            teacher_pj()
            username()
        elif choice == '\n':
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
        name_elements = get_name(cookies)
        if name_elements:
            name = name_elements[0].strip()
            if name in white_names:
                print("用户姓名：" + name)
                fun(cookies)
                return cookies
            else:
                main()
        else:
            if os.path.exists(r"./login_message\pwd.txt"):
                username()
            else:
                main()
    else:
        if os.path.exists(r"./login_message\pwd.txt"):
            username()
        else:
            main()


# 密码登录
def username():
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
    aes_response = requests.get(gitee_url + '/aes.js')
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
    # 新建会话，保持登录状态
    session = requests.Session()
    # 发送登录请求
    login_url = 'https://jwc.htu.edu.cn/new/login'  # 替换为实际的登录页面URL
    login_response = session.post(url=login_url, data=login_data, headers=login_headers, cookies=cookies)
    name_elements = get_name(cookies)
    if name_elements:
        name = name_elements[0].strip()
        if name in white_names:
            print(f"用户姓名：{name.strip()}")
            print(f"登录状态：{login_response.json()['message']}")
            # print("Cookies:"+jsessionid)
            encrpt(password, public_key)
            renew_LOGIN('cookies', jsessionid)
            fun(cookies)
            return cookies
        else:
            print("登录失败！请检查学号后重新输入")
            renew_LOGIN('id', '')
            renew_LOGIN('pwd', '')
            main()
    else:
        print('登录失败！')
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
    name_elements = get_name(cookies)
    if name_elements:
        name = name_elements[0].strip()
        if name in white_names:
            print("登录状态：登录成功！")
            renew_LOGIN('cookies', jsessionid)
            return cookies
        else:
            print('登录状态：登录失败')
            main()
    else:
        print('登录状态：登录失败')
        main()


# 登录函数
def main():
    print("------------------------登录系统------------------------")
    print("请选择登录方式：[1]密码登录   [2]Cookies登录   [3]退出登录")
    login_way = input("输入数字：")
    if login_way == '1':
        cookies = username()
        fun(cookies)
    elif login_way == '2':
        cookies = jsession()
        fun(cookies)
    elif login_way == '\n':
        input("按回车键退出...")
        sys.exit()
    else:
        input("按回车键退出...")
        sys.exit()


if __name__ == "__main__":
    cookies = cookies_read()
