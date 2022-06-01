# coding: utf-8

import requests
import json
import sys, os, time
import pandas as pd
import random

sys.path.append('..')
from db.model import Model


query_hash = 'bc3296d1ce80a24b1b6e40b1e72903f5'
headinfo={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        #'cookie': 'ig_did=ED2C5F0D-A802-4D99-AC09-6CFB5B5B7252; mid=Xn2_NQALAAG-rn1NahxGXXun6taL; fbm_124024574287414=base_domain=.instagram.com; csrftoken=5GauAxaQEwXnxajoK2oifJmuhGHwMlVy; ds_user_id=2907910601; sessionid=2907910601%3AlftD15c02p6v1P%3A14; shbid=1701; shbts=1592360010.4655972; urlgen="{\"75.140.93.238\": 20115}:1jlNan:KmLOTtTCq1toBj8AQOoAyW8Myjs"',
        # 'cookie': 'ig_did=4B80AEBF-A25D-42B2-8B23-3A5D2B0A76DF; mid=Xq2zFQALAAHIcm_RiqjlC-D1xJ32; fbm_124024574287414=base_domain=.instagram.com; fbsr_124024574287414=kb0KZgyIcfGqXySpoe77U7bLvAAGwljvHOsBcIDLxqw.eyJ1c2VyX2lkIjoiMTAwMDA1MzMyMzkxMTcwIiwiY29kZSI6IkFRQ2IxcXMySGNoZVphUlJXdmppdWpIenc5QXlraWZLbjB2cUpjR0NRZHdaNUZMTWtEOW9idzRtNGQwTHE5Y3B0LV95UEdLdzktX1lfQmFFMUpJV1FxNmRHWnFoeHdSYy1NaW1KeENDbVE0bXJKUDdDQzdIejhxSDB3NXpqLXZ3UHFHbVBXRFNyX0FXNXdXODdSNXdHaW1zb01VcjNhdzhCRE0wWDZONGI5QkthSXdPdjRYREc0aEtpczdzMkRXOGN6MjBuUkpyX0kzVExvdkF1QkhwZHBTWk9TUEFpdTdwb09OSWhEUmFqbmYxWUhGc1kyTENRZElJVmlHbjdhRG1KNEtVOXNESmdZZ19YMVFEdTJYQXNaQWpfV0xfNlp4RHRiOG9WTWNVTEhWQjBVRTgxWDhITWZWd0haZFlBWXdOS0lEUTRFR0xtWXdLcDg0QVVOajZadERpIiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCQUpNN2syajBzZVhaQk92aGw4bFVyck02Zk85NVZoVm9QOEdVNzBVMlpDQmNaQjJ6U2hWVXBMYlpCZ0lUMVpBeUVxN2szS1dnalpBOFU1T0ZnU1pBaVVaQlhPNUJxWkNqR0VCUGFsZTl4aDlQMmlEMU1Gckp2b0NWMHdtanppQ2l5a252dWhsVFpCY3ZqN3lzdVM3dEVMWWpmUGs1ZjRkODlvSTRVNW1idlJBTmNvIiwiYWxnb3JpdGhtIjoiSE1BQy1TSEEyNTYiLCJpc3N1ZWRfYXQiOjE1ODg0NDE4ODF9; csrftoken=1qdyiSS9zDnouW3m26eMoExT9b9L5FiA; ds_user_id=18092336506; sessionid=18092336506%3Ax74jueSanSnhiJ%3A3; shbid=9329; rur=FTW; datr=gC7PXvLd2TFdy25fxxDLkTJn; shbts=1592277692.4268649; urlgen="{\"98.239.146.233\": 7922}:1jlZZ2:skf07ZjFvl_RHUBNqeYFHLH_YF4"',
}
pic_root = "/home/lab321/weixiao/code/drug_tracking/pic_data"
model = Model()

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

def get_json_paid_proxy(url, head = None):
    '''
        url = https://www.instagram.com/dmvsno1slim/
    ''' 
    r = requests.get(f'https://api.proxycrawl.com/?token=EV8n79XDFl7TAWkbb6ISYg&url={url}?__a=1', headers = head)
    if r.status_code != 200:
        print('request bad url=', url, ' status_code=', r.status_code)
        return None
    return r

def get_json_paid_proxy_2(url, head = None):
    '''
        url = https://www.instagram.com/dmvsno1slim/
    ''' 
    r = requests.get(f'http://api.scraperapi.com?api_key=4833bb313b4af955c0aa78f8e3f0afab&url={url}?__a=1', headers = head)
    if r.status_code != 200:
        print('request bad url=', url, ' status_code=', r.status_code)
        return None
    return r

def get_json_result(url):
    if random.randint(0, 1):
        return get_json_paid_proxy(url, head = headinfo)
    else:
        return get_json_paid_proxy_2(url, head = headinfo)
        # proxy = get_random_proxy(proxies)
        # r = requests.get(url+'?__a=1', headers=headinfo)
        # if r.status_code != 200:
        #     print('request bad url=', url, ' status_code=', r.status_code)
        #     return None
        # return r
        


def store_pic(store_path, url):
    pic_name = url.split('?')[0].split('/')[-1]
    sub_dir = pic_name[0:3]
    store_path.rstrip(os.sep)
    full_dir = store_path + os.sep + sub_dir
    if not os.path.exists(full_dir):
        os.makedirs(full_dir)
    full_path = full_dir + os.sep + pic_name
    resp = requests.get(url, headers=headinfo)
    if resp.status_code == 200:
        with open(full_path, 'wb') as fp:
            fp.write(resp.content)
        return sub_dir + os.sep + pic_name
    else:
        return None


def store_thumb(pic_path, url):
    # print(url)
    pic_name = url.split('?')[0].split('/')[-1]
    resp = requests.get(url, headers = headinfo)
    if resp.status_code == 200:
        with open(pic_path+pic_name, 'wb') as fp:
            fp.write(resp.content)
    else:
        print('download pic error, url=', url, ', status code=', resp.status_code)

    return pic_name

def fetch_post(shortcode):
    url  = f'https://www.instagram.com/p/{shortcode}/'
    if model.exist_post_by_shortcode(shortcode):        
        print('post exists: ', url)
        return True
    
    resp = requests.get(url+'?__a=1', headers=headinfo)
    # resp = get_json_result(url)
    if resp is None:
        return False
    if resp.status_code != 200:
        print(url, 'return error code=', resp.status_code)
        return False
    
    jsdata = json.loads(resp.text)['graphql']['shortcode_media']
    # get location
    if jsdata['location'] is None:
        location_id = 0
        address_json = ''
    else:
        location_id = jsdata['location']['id']
        address_json = jsdata['location']['address_json']
    # get caption
    caption = jsdata['edge_media_to_caption']['edges']
    if len(caption) == 0:
        caption = ''
    else:
        caption = caption[0]['node']['text']
    # get pic_path
    pic_path = store_pic(pic_root, jsdata['display_resources'][0]['src'])
    if pic_path is None:
        print('download pic error:link= %s', jsdata['display_resources'][0]['src'])
        return False
    pic_url = jsdata['display_resources'][-1]['src']
    # post entity
    post = {
        'id' : jsdata['id'],
        'shortcode': jsdata['shortcode'],
        'location_id': location_id,
        'caption': caption,
        'owner_id': jsdata['owner']['id'],
        'owner_name': jsdata['owner']['username'],
        'like_count': jsdata['edge_media_preview_like']['count'],
        'comment_count':jsdata['edge_media_to_parent_comment']['count'],
        'pic_path': pic_path,
        'pic_url': pic_url,
        'taken_at_timestamp': jsdata['taken_at_timestamp'], 
        'is_ad': jsdata['is_ad'],
        'is_drug_related': 0,
        'address_json': address_json,
    }

    # insert post
    model.insert_post(**post)
    # insert user info of the post
    fetch_user_info(post['owner_name'])
    # fetch comments under this post
    postid = jsdata['id']
    edges =  jsdata['edge_media_to_parent_comment']['edges']
    for cmt in edges:
        info = cmt['node']
        record = {
            "id": info['id'],
            "text": info['text'],
            "created_at": info['created_at'],
            "owner_id": info['owner']['id'],
            "user_name": info['owner']['username'],
            "like_by_no": info['edge_liked_by']['count'],
            "did_report_as_spam": info['did_report_as_spam'],
            'post_id': postid,
        }
        try:
            ret_n = model.insert_comment(**record)
            if ret_n == 0:
                print('insert duplicate comment:', record)
            if ret_n == -1:
                print('insert coment failed:', record)
        except Exception as e:
            print(e)

    has_next = jsdata['edge_media_to_parent_comment']['page_info']['has_next_page']
    end_cursor = jsdata['edge_media_to_parent_comment']['page_info']['end_cursor']
    while has_next:
        data = {
            "query_hash": query_hash,
            "variables": '{"shortcode":"'+ url.rstrip('/').split('/')[-1]+'","first":12,"after":"'+ end_cursor +'"}',
        }
        resp = requests.get(r'https://www.instagram.com/graphql/query/', params = data, headers=headinfo)
        d = json.loads(resp.text)
        if d['status'] != 'ok':
            print('status=', d['status'])
            break
        edges =  d['data']['shortcode_media']['edge_media_to_parent_comment']['edges']
        if len(edges) == 0:
            print('return empty comment list, exit')
            break
        for cmt in edges:
            info = cmt['node']
            record = {
                "id": info['id'],
                "text": info['text'],
                "created_at": info['created_at'],
                "owner_id": info['owner']['id'],
                "user_name": info['owner']['username'],
                "like_by_no": info['edge_liked_by']['count'],
                "did_report_as_spam": info['did_report_as_spam'],
                'post_id': postid,
            }
            try:
                if model.insert_comment(**record) == 0:
                    print('insert duplicate comment: ', record)
            except Exception as e:
                print(e)

        has_next = d['data']['shortcode_media']['edge_media_to_parent_comment']['page_info']['has_next_page']
        end_cursor = d['data']['shortcode_media']['edge_media_to_parent_comment']['page_info']['end_cursor']

    return True



def fetch_user_info(user_name):
    url = f'https://www.instagram.com/{user_name}/'
    # resp = requests.get(url+'?__a=1', headers=headinfo)
    resp = requests.get(url+'?__a=1', headers=headinfo)
    # resp = get_json_result(url)
    if resp is None:
        return False
    if resp.status_code != 200:
        print(url, 'user return error code=', resp.status_code)
        return False

    if resp.text == '{}':
        print(f'user has been deleted!!!{user_name}')
        return 567
    try:
        jsdata = json.loads(resp.text)['graphql']['user']
    except Exception as e:
        print(e)
        print(resp.text)
    user = {
        "id": jsdata['id'],
        "user_name": jsdata['username'],
        "full_name": jsdata['full_name'],
        "follower_no": jsdata['edge_followed_by']['count'],
        "following_no": jsdata['edge_follow']['count'],
        "post_no": jsdata['edge_owner_to_timeline_media']['count'],
        "biography": jsdata['biography'],
        "external_url": jsdata['external_url'],
        "is_business_account": jsdata['is_business_account'],
        "is_joined_recently": jsdata['is_joined_recently'],
        "profile_pic": jsdata['profile_pic_url_hd'],
        "posts_drug_ratio": -1,
    }
    # fetch user thumb
    thumb_list = []
    posts = jsdata['edge_owner_to_timeline_media']['edges']
    count = jsdata['edge_owner_to_timeline_media']['count']
    has_next_page = jsdata['edge_owner_to_timeline_media']['page_info']['has_next_page']
    end_cursor = jsdata['edge_owner_to_timeline_media']['page_info']['end_cursor']
    counter = 0
    count = count if count < 10 else 10
    while len(posts) > 0 and counter < count:
        for post in posts:
            counter += 1
            pic_url = post['node']['thumbnail_resources'][-1]['src']            
            pic_name = store_thumb('/home/lab321/weixiao/code/drug_tracking/pic_data/user_thumb/', pic_url)
            thumb_list.append(pic_name)
        
        if has_next_page and end_cursor is not None:
            data = {
                "query_hash": '44efc15d3c13342d02df0b5a9fa3d33f',
                "variables": '{"id":"'+ jsdata['id'] +'","first":12,"after":"'+ end_cursor +'"}',
            }
            resp = requests.get(r'https://www.instagram.com/graphql/query/', params=data, headers=headinfo)
            if resp.status_code != 200:
                print(' sub query failed:', resp.status_code, data)
                return
            subjs = json.loads(resp.text)
            posts = subjs['data']['user']['edge_owner_to_timeline_media']['edges']
            has_next_page = subjs['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
            end_cursor = subjs['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
        else:
            posts = []
    
    # insert user info
    user["thumb"] = ','.join(thumb_list)
    return model.insert_user_duplicate_update(**user)





def fetch_user(user_name):
    url = f'https://www.instagram.com/{user_name}/'
    resp = requests.get(url+'?__a=1', headers=headinfo)
    if resp.status_code != 200:
        print(url, 'user return error code=', resp.status_code)
        return False
        
    jsdata = json.loads(resp.text)['graphql']['user']

    user = {
        "id": jsdata['id'],
        "user_name": jsdata['username'],
        "full_name": jsdata['full_name'],
        "follower_no": jsdata['edge_followed_by']['count'],
        "following_no": jsdata['edge_follow']['count'],
        "post_no": jsdata['edge_owner_to_timeline_media']['count'],
        "biography": jsdata['biography'],
        "external_url": jsdata['external_url'],
        "is_business_account": jsdata['is_business_account'],
        "is_joined_recently": jsdata['is_joined_recently'],
        "profile_pic": jsdata['profile_pic_url_hd'],
        "posts_drug_ratio": -1,
    }
    # insert user info
    model.insert_user_duplicate_update(**user)
    # fetch each post of this user

    posts = jsdata['edge_owner_to_timeline_media']['edges']
    has_next_page = jsdata['edge_owner_to_timeline_media']['page_info']['has_next_page']
    end_cursor = jsdata['edge_owner_to_timeline_media']['page_info']['end_cursor']

    while len(posts) > 0:
        for post in posts:
            shortcode = post['node']['shortcode']
            print(shortcode)
            fetch_post(shortcode)
        
        if has_next_page and end_cursor is not None:
            data = {
                "query_hash": '9dcf6e1a98bc7f6e92953d5a61027b98',
                "variables": '{"id":"'+ jsdata['id'] +'","first":12,"after":"'+ end_cursor +'"}',
            }
            resp = requests.get(r'https://www.instagram.com/graphql/query/', params=data, headers=headinfo)
            if resp.status_code != 200:
                print(' sub query failed:', data)
                return
            subjs = json.loads(resp.text)
            posts = subjs['data']['user']['edge_owner_to_timeline_media']['edges']
            has_next_page = subjs['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
            end_cursor = subjs['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
        else:
            posts = []

    



# /home/lab321/weixiao/code/drug_tracking/pic_data/user_thumb
# /home/lab321/weixiao/code/drug_tracking/pic_data/user_thumb2


if __name__ == "__main__":
    # B_BNLJ1nBzF
    # r = fetch_post("B1EmOdIAOs7")
    # print(r)
    # fetch_user_info('oriwa.d.brams')
    # links_path = '/home/lab321/weixiao/data/ig_links/new.csv'
    links_path = '/home/lab321/weixiao/data/ig_links/empty_text.csv'
    with open(links_path, 'r') as f:
        idx = 1
        for line in f:
            shortcode = line.strip().rstrip('/').split('/')[-1]
            r = fetch_post(shortcode)
            print(r, idx)
            time.sleep(14)
            idx += 1



    # names = [
    #     ]

    # df = pd.read_csv('name_remove.csv', header=None, names=['name'])
    # for idx, n in df.iterrows():
    #     r = fetch_user_info(n['name'])
    #     print(idx, r)
    #     time.sleep(30)
    # for n in names:
    #     r = fetch_user_info(n)
    #     print(r)
    del_list = []

    # with open('/home/lab321/weixiao/data/ig_links/negative_name.csv', 'r') as f:
    #     idx = 1
    #     for user_name in f:
    #         r = fetch_user_info(user_name.strip())
    #         if r == 567:
    #             del_list.append(user_name.strip())
    #         print(r, idx)
    #         time.sleep(17)
    #         idx += 1
    
    # with open('name_remove.csv', 'w') as f:
    #     for x in del_list:
    #         f.write(x+'\n')
    # pass