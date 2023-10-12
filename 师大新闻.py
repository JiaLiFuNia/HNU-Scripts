import requests

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58',
}

params = {
    'articleTitle': '',
    'newClassId': '1',
    'pageSize': '12',
    'pageNum': '1',
}

response_1 = requests.get('http://app.htu.edu.cn/appapi/article/page', params=params, headers=headers).json()
print(response_1)

'''import requests
from bs4 import BeautifulSoup
headers = {
    'authority': 'www.htu.edu.cn',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    # Requests sorts cookies= alphabetically
    # 'cookie': 'language=; JSESSIONID=11195D168A72B2338EE5257ECE3A79C9; route=199de3b79879775ce87815ec35013c9f',
    'pragma': 'no-cache',
    'referer': 'https://www.htu.edu.cn/',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Microsoft Edge";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58',
}

url = 'https://www.htu.edu.cn/8955/list.htm'

response = requests.post(url=url, headers=headers).text
print(response)'''
'''
soup = BeautifulSoup(response, 'html.parser')
titles = soup.select('span.Article_Title a')

for title in titles:
    print(title.text)
'''