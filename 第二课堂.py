import requests

cookies = {
    'sid': '10164b71-12fb-4592-a3b3-4372893978d0',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # 'Cookie': 'sid=10164b71-12fb-4592-a3b3-4372893978d0',
    'Origin': 'http://dekt.htu.edu.cn',
    'Pragma': 'no-cache',
    'Referer': 'http://dekt.htu.edu.cn/syslogin',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58',
}

data = {
    'username': '6666',
    'password': '',
    'password2': 'Mkvluu0wHbD8cvYIB8FED9NcgNzBVFwRJgIij8R+8jGGf3M6HbEc4uOppBI+isK6zGB/rrWYtfFLDLnMWwCldAX/yjDRxpXFQKLcUE+vc8sbQRyvw2qw6YQix+99x/KBUv75cixjl9MDDp+NxbeNRUJauzVkK+0RKE1I5Nq/4RI=',
    'tk': '5ECF7157913C44C997A6D1ACEF7457BB',
    'verifycode': 'tg9x',
}

response = requests.post('http://dekt.htu.edu.cn/syslogin', cookies=cookies, headers=headers, data=data, verify=False)
print(response.text)
