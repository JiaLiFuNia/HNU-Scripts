import json
import requests
from bs4 import BeautifulSoup
from gne import GeneralNewsExtractor
import re

m = 1


# 格式化文章内容
def init_text(text):
    text = re.sub('。[\n\r]+', 'TEMPCHAR', text)  # 标记句号后换行
    text = re.sub('[\n\r]+', '', text)
    text = re.sub('TEMPCHAR', '。\n\n', text)  # 句号后换行
    text = re.sub(';', ';\n', text)  # 分号后添加换行
    text = re.sub(':', ':\n', text)  # 冒号后添加换行
    return '\n' + text


# 获取每个链接对应的内容
def get_details(url):
    global m
    if url.split('/')[2] != 'web.htu.edu.cn':
        res = requests.get(url)
        res.encoding = "utf-8"
        extractor = GeneralNewsExtractor()
        detail = extractor.extract(res.text, with_body_html=True)
        detail_list = {
            "code": 200,
            "message": "success",
            "data": {
                "id": m,
                "title": "",
                "time": "",
                "content": ""
            }
        }
        detail_list['data']['title'] = detail['title']
        detail_list['data']['time'] = detail['publish_time']
        detail_list['data']['content'] = init_text(detail['content'])
        return detail_list


# 获取每条新闻的链接
def get(url):
    global m
    json_list = {
        "code": 200,
        "message": "success",
        "data":
            [

            ]
    }
    pages = 10
    id = 280
    i = 0
    for page in range(pages):
        print(url)
        url_list = str(url) + str(page + 1) + ".htm"
        print(url_list)
        response = requests.get(url_list)
        soup = BeautifulSoup(response.content, 'html.parser')
        titles = urls = soup.select('div#wp_news_w15 ul.wp_article_list li.list_item div.fields span.Article_Title a')
        times = soup.select('div#wp_news_w15 ul.wp_article_list li.list_item div.fields span.Article_PublishDate')
        for a_title in titles:
            json_dict = {
                "id": id + 1,
                "title": a_title.get('title')
            }
            json_list['data'].append(json_dict)
            id = id + 1

        for time in times:
            json_list['data'][i]["time"] = time.text
            i = i + 1

        for news_url in urls:
            print(news_url)
            if news_url.get('href').startswith('h'):
                detail = get_details(news_url.get('href'))
            else:
                detail = get_details('https://www.htu.edu.cn' + news_url.get('href'))
            print(detail)
            save(detail, f'news/article&id={m}')
            m = m + 1
    return json_list


# 保存文件
def save(text, filename):
    json_str = json.dumps(text)
    with open(fr"{filename}.json", 'w') as file:
        file.write(json_str)


# 生成json
def save_list(url, file_name):
    list = get(url)
    save(list, file_name)
    print(list)
    print('success')


save_list('https://www.htu.edu.cn/8954/list', 'activenewslist')
save_list('https://www.htu.edu.cn/8957/list', 'othernewslist')
save_list('https://www.htu.edu.cn/8955/list', 'newslist')
