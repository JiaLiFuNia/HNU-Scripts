import requests

headers = {
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # 'Cookie': 'sid=68544f21-8ebd-4f47-b8fc-3f41a1902b87',
    'Pragma': 'no-cache',
    'Referer': 'http://dekt.htu.edu.cn/sys/stu/center/changepwd',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
}

res = requests.get('http://dekt.htu.edu.cn/files/admin/199/20221117104135-244166313.png', headers=headers, verify=False)
print(res)
print("请求头:%s" % res.request.headers)
print("响应头:%s" % res.headers)
