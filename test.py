# coding: utf-8


import requests
import json,random


# data = {
#     "query_hash": "bc3296d1ce80a24b1b6e40b1e72903f5",
#     "variables": '{"shortcode":"B6ivHJFFBOG","first":12,"after":"QVFEWjZ1MlBoczdkRWgwVUREc3lJak5uQ0g0MFVBZjBXUmRqWGZaOW5McDk0QUM2S0NSUm1sem9aRDBsTWRSdUVhWTlQMmRqc3FkNVRrS0JldC1TREFfZQ=="}',
# }
# resp = requests.get(r'https://www.instagram.com/graphql/query/', 
#     params= data,
#     headers={
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0'}
#     )


# a = json.loads(resp.text)

# print(a)



headinfo = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
}

url = 'https://www.instagram.com/dmvsno1slim/?__a=1'

# r = requests.get(url, headers = headinfo)

# print(r.text)
# print(r.status_code)


session = requests.session()
session.proxies = {}
session.proxies['http'] =  'proxy.proxycrawl.com:9000'
session.proxies['https'] = 'proxy.proxycrawl.com:9000'
# session.proxies['http'] = '157.182.212.39:8888'
# session.proxies['https'] = '157.182.212.39:8888'
# session.proxies['http'] = 'socks5h://localhost:9050'
# session.proxies['https'] = 'socks5h://localhost:9050'


sess1 = requests.session()
sess1.proxies = {}
sess1.proxies['http'] = '157.182.212.39:8888'
sess1.proxies['https'] = '157.182.212.39:8888'
sess2 = requests.session()
sess2.proxies = {}
sess2.proxies['http'] = '157.182.212.67:8888'
sess2.proxies['https'] = '157.182.212.67:8888'
sess_pool = [sess1, sess2]

def get_session():
    n = len(sess_pool)
    r = random.randint(0, n-1)
    return sess_pool[r]


# url = 'http://httpbin.org/ip'
# # r = get_session().get(url, headers = headinfo)
# print(session.proxies)
# r = session.get(url, headers = headinfo)
# print(r.text)
# url = 'https://www.instagram.com/dmvsno1slim/?__a=1'
# r2 = session.get(url, headers= headinfo)
# print(r2.text)


proxies = [
    {
        # xuan
        'http':  '157.182.212.47:8888',
        'https': '157.182.212.47:8888',
    },
    {
        # xiong
        'http':  '157.182.212.39:8888',
        'https': '157.182.212.39:8888',
    },
    {
        # mindi
        'http':  '157.182.212.67:8888',
        'https': '157.182.212.67:8888',
    },
    {
        # minglei
        'http':  '157.182.212.97:8888',
        'https': '157.182.212.97:8888',
    }
]

def get_random_proxy(proxies):
    n = len(proxies)
    r = random.randint(0, n-1)
    return proxies[r]

url = 'http://httpbin.org/ip'
# url = 'https://www.instagram.com/dmvsno1slim/?__a=1'
# url = 'https://www.google.com'
# url = 'https://www.baidu.com'
# r = requests.get(url, headers=headinfo, proxies=get_random_proxy(proxies))
# print(r.text)

def get_json_paid_proxy(url, head = None):
    '''
        url = https://www.instagram.com/dmvsno1slim/
    ''' 
    r = requests.get(f'https://api.proxycrawl.com/?token=EV8n79XDFl7TAWkbb6ISYg&url={url}?__a=1', headers = head)
    if r.status_code != 200:
        print('request bad url=', url, ' status_code=', r.status_code)
        return ''
    return r.text
























# cookie setting
# r = requests.post("http://pythonscraping.com/pages/cookies/welcome.php", params)
# print("Cookie is set to:")
# print(r.cookies.get_dict())
# print("-----------")
# print("Going to profile page...")
# r = requests.get("http://pythonscraping.com/pages/cookies/profile.php",
# cookies=r.cookies)
# print(r.text)

# # use session to track and manage cookie
# session = requests.Session()
# params = {'username': 'username', 'password': 'password'}
# s = session.post("http://pythonscraping.com/pages/cookies/welcome.php", params)
# print("Cookie is set to:")
# print(s.cookies.get_dict())
# print("-----------")
# print("Going to profile page...")
# s = session.get("http://pythonscraping.com/pages/cookies/profile.php")
# print(s.text)