#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import requests

url = 'http://www.instagram.com/johnn1016/?__a=1'

headinfo={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        #'cookie': 'ig_did=ED2C5F0D-A802-4D99-AC09-6CFB5B5B7252; mid=Xn2_NQALAAG-rn1NahxGXXun6taL; fbm_124024574287414=base_domain=.instagram.com; csrftoken=5GauAxaQEwXnxajoK2oifJmuhGHwMlVy; ds_user_id=2907910601; sessionid=2907910601%3AlftD15c02p6v1P%3A14; shbid=1701; shbts=1592360010.4655972; urlgen="{\"75.140.93.238\": 20115}:1jlNan:KmLOTtTCq1toBj8AQOoAyW8Myjs"',
        # 'cookie': 'ig_did=4B80AEBF-A25D-42B2-8B23-3A5D2B0A76DF; mid=Xq2zFQALAAHIcm_RiqjlC-D1xJ32; fbm_124024574287414=base_domain=.instagram.com; fbsr_124024574287414=kb0KZgyIcfGqXySpoe77U7bLvAAGwljvHOsBcIDLxqw.eyJ1c2VyX2lkIjoiMTAwMDA1MzMyMzkxMTcwIiwiY29kZSI6IkFRQ2IxcXMySGNoZVphUlJXdmppdWpIenc5QXlraWZLbjB2cUpjR0NRZHdaNUZMTWtEOW9idzRtNGQwTHE5Y3B0LV95UEdLdzktX1lfQmFFMUpJV1FxNmRHWnFoeHdSYy1NaW1KeENDbVE0bXJKUDdDQzdIejhxSDB3NXpqLXZ3UHFHbVBXRFNyX0FXNXdXODdSNXdHaW1zb01VcjNhdzhCRE0wWDZONGI5QkthSXdPdjRYREc0aEtpczdzMkRXOGN6MjBuUkpyX0kzVExvdkF1QkhwZHBTWk9TUEFpdTdwb09OSWhEUmFqbmYxWUhGc1kyTENRZElJVmlHbjdhRG1KNEtVOXNESmdZZ19YMVFEdTJYQXNaQWpfV0xfNlp4RHRiOG9WTWNVTEhWQjBVRTgxWDhITWZWd0haZFlBWXdOS0lEUTRFR0xtWXdLcDg0QVVOajZadERpIiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCQUpNN2syajBzZVhaQk92aGw4bFVyck02Zk85NVZoVm9QOEdVNzBVMlpDQmNaQjJ6U2hWVXBMYlpCZ0lUMVpBeUVxN2szS1dnalpBOFU1T0ZnU1pBaVVaQlhPNUJxWkNqR0VCUGFsZTl4aDlQMmlEMU1Gckp2b0NWMHdtanppQ2l5a252dWhsVFpCY3ZqN3lzdVM3dEVMWWpmUGs1ZjRkODlvSTRVNW1idlJBTmNvIiwiYWxnb3JpdGhtIjoiSE1BQy1TSEEyNTYiLCJpc3N1ZWRfYXQiOjE1ODg0NDE4ODF9; csrftoken=1qdyiSS9zDnouW3m26eMoExT9b9L5FiA; ds_user_id=18092336506; sessionid=18092336506%3Ax74jueSanSnhiJ%3A3; shbid=9329; rur=FTW; datr=gC7PXvLd2TFdy25fxxDLkTJn; shbts=1592277692.4268649; urlgen="{\"98.239.146.233\": 7922}:1jlZZ2:skf07ZjFvl_RHUBNqeYFHLH_YF4"',
}

def test_ig(url):
    response = requests.get(
        url,
        proxies={
            "https": "https://:@proxy.crawlera.com:8011/",
        },
    )
    print(response.text)

    
    
def getip_requests(url):
    print ("(+) Sending request with plain requests...")
    r = requests.get(url, headers=headinfo)
    print ("(+) IP is: " + r.text)


def getip_requesocks(url):
    print ("(+) Sending request with tor proxy...")
    
    # session.proxies = {'http': 'socks5://127.0.0.1:9050',
    #                    'https': 'socks5://127.0.0.1:9050'}
    
    sess = requests.session()
    sess.proxies = {}
    sess.proxies['http'] = 'socks5://127.0.0.1:9050'
    sess.proxies['https'] = 'socks5://127.0.0.1:9050'

    r = sess.get(url, headers=headinfo)
    print ("(+) IP is: " + r.text)


def main():
    print ("Running tests...")
    # getip_requests(url)
    getip_requesocks(url)
    # os.system("""(echo authenticate '"hello123"'; echo signal newnym; echo quit) | nc localhost 9051""")
    # getip_requesocks(url)


def test(url):

    url = "http://httpbin.org/ip"
    proxy_host = "proxy.crawlera.com"
    proxy_port = "8011"
    proxy_auth = ":" # Make sure to include ':' at the end
    proxies = {"https": "https://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
        "http": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port)}

    r = requests.get(url, headers=headinfo, proxies= proxies, verify=False)
    print(r.status_code)
    print(r.text)


if __name__ == "__main__":
    getip_requests(url)