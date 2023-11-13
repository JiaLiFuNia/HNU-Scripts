import requests

url = 'http://10.101.2.199/portal.do?wlanuserip=10.102.17.206&wlanacname=HSD-BRAS-2&mac=9c:2f:9d:aa:3d:8d&vlan' \
      '=19981009&hostname=XuBoHan&rand=2ead1d29d70157&url=http%3A%2F%2Fedge-http.microsoft.com%2Fcaptiveportal' \
      '%2Fgenerate_20 '

cookies = {
    'JSESSIONID': 'F1336AC025C3B6A5A95B6444B4EF0739'
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # Requests sorts cookies= alphabetically 'Cookie': 'userName=2201214001; 2201214001=xubohan2004819;
    # useridtemp=2201214001@yd; JSESSIONID=63D7F0009BE6F1E47243AC501176DDC7',
    'Pragma': 'no-cache',
    'Referer': 'http://edge-http.microsoft.com/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 '
                  'Safari/537.36 Edg/114.0.1823.58',
}
res = requests.get(url=url, cookies=cookies, headers=headers).text

print(res)
