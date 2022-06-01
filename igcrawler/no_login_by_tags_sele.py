# coding: utf-8

import requests
import json
import sys, os, time
import argparse
import random
import platform
import logging as log

sys.path.append('..')
from db.model import Model

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

from .utils import randmized_sleep
from .utils import Gcnt

class Browser():
    
    def __init__(self, has_screen, counter):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        service_args = ["--ignore-ssl-errors=true"]
        chrome_options = Options()
        if not has_screen:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")
        os_type = platform.system()
        chrome_path = "%s/bin/%s" % (dir_path, "chromedriver" if os_type=="Linux" else "chromedriver.exe")
        self.driver = webdriver.Chrome(
            executable_path = chrome_path,
            service_args = service_args,
            chrome_options = chrome_options,
        )
        self.driver.implicitly_wait(5)
        self.counter = counter
        self.timer = time.time()


    @property
    def page_height(self):
        return self.driver.execute_script("return document.body.scrollHeight")

    def get(self, url, t=0):
        self.driver.get(url)
        if t != 0:
            randmized_sleep(t)

    @property
    def current_url(self):
        return self.driver.current_url

    def implicitly_wait(self, t):
        self.driver.implicitly_wait(t)
    
    def get_json_text(self):
        try:
            return self.driver.find_element_by_tag_name('pre').text
        except:
            log.error('URL=%s error!', self.driver.current_url)
            return {'status':'fail'}

    def find_one_by_xpath(self, selector,  elem=None, waittime=0):
        return self.find_one(selector, stype='xpath', elem=elem, waittime=waittime)

    def find_one_by_css(self, selector, elem=None, waittime=0):
        return self.find_one(selector, stype='css', elem=elem, waittime=waittime)

    def find_by_xpath(self, selector, elem=None, waittime=0):
        return self.find(selector, stype='xpath', elem=elem, waittime=waittime)

    def find_by_css(self, selector, elem=None, waittime=0):
        return self.find(selector, stype='css', elem=elem, waittime=waittime)


    def find_one(self, selector, stype='css', elem=None, waittime=0):
        obj = elem or self.driver
        if stype == 'css':
            selector_type = By.CSS_SELECTOR
        elif stype == 'xpath':
            selector_type = By.XPATH
        elif stype == 'id':
            selector_type == By.ID

        if waittime:
            WebDriverWait(obj, waittime).until(
                EC.presence_of_element_located((selector_type, selector))
            )
        try:
            return obj.find_element(selector_type, selector)
        except NoSuchElementException:
            log.error('%s NoSuchElementException', selector, exc_info=True)
            return None

    def find(self, selector, stype='css', elem=None, waittime=0):
        obj = elem or self.driver
        if stype == 'css':
            selector_type = By.CSS_SELECTOR
        elif stype == 'xpath':
            selector_type = By.XPATH
        elif stype == 'id':
            selector_type == By.ID

        try:
            if waittime:
                WebDriverWait(obj, waittime).until(
                    EC.presence_of_element_located((selector_type, selector))
                )
        except TimeoutException:
            log.error('%s TimeoutException', selector, exc_info=True)
            return None

        try:
            return obj.find_elements(selector_type, selector)
        except NoSuchElementException:
            log.error('%s NoSuchElementException', selector, exc_info=True)
            return None

    def see_posts_anyway(self):
        try:
            btns = self.driver.find_elements_by_xpath(\
                '//button[@class="sqdOP  L3NKy    _8A5w5    "]')
            for btn in btns:
                if btn.text == "See Posts Anyway":
                    btn.click()
        except NoSuchElementException as no:
            pass

    def get_js_data(self, typex, shortcode="", retrycnt=3):  
        """
        tag : window._sharedData.entry_data.TagPage[0].graphql.hashtag
        post : window.__additionalData["/p/B8zPVu0l9bE/"]["data"]["graphql"]["shortcode_media"]
        """

        media_type = {
            "tag" : "window._sharedData.entry_data.TagPage[0].graphql.hashtag",
            "post" : 'window.__additionalData["/p/%s/"]["data"]["graphql"]["shortcode_media"]'%shortcode,
            "nonce" : "window._sharedData.nonce",
            "user" : 'window._sharedData.entry_data.ProfilePage[0]["graphql"].user',
        }

        retry = 0
        sleeptime = 15
        while retry < retrycnt:
            try:
                error = self.driver.find_element_by_xpath(\
                    '//div[@class="error-container -cx-PRIVATE-ErrorPage__errorContainer -cx-PRIVATE-ErrorPage__errorContainer__"]')
                # coming here, there must be errors
                # we need to determine the type of error.
                msg = error.find_element_by_tag_name('h2').text
                if msg == "Sorry, this page isn't available.":
                    log.error('URL is broken: %s', self.driver.current_url)
                    return {}

                msg = error.find_element_by_tag_name('p').text
                if msg.startswith('Please wait a few'):
                    log.error('Please wait a few minutes before you try again. Sleep for %s secs', sleeptime)
                    time.sleep(sleeptime)
                    self.driver.refresh()
                    sleeptime *= 2
            except NoSuchElementException as no:
                break
            retry += 1
        
        if retry == retrycnt:
            log.error('Even though I wait for %s seconds, I still cannot get the desired page. So I give up.', sleeptime)
            return None
        # there is a chance that this hashtag has been removed by Instagram.
        # so we need to have a if-condition here.
        # try:
        #     # if not found the element, this calling will be time-consuming.
        #     self.driver.find_element(By.TAG_NAME, 'button')
        # except NoSuchElementException:
        #     log.error('link=[%s] is broken!', self.driver.current_url)
        #     return {}
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//img[@class="FFVAD"]'))
            )
        except TimeoutException:
            try:
                WebDriverWait(self.driver, 4).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="PyenC"]'))
                )
            except TimeoutException:
                log.error('waiting for %s, TimeoutException', media_type[typex])
                return None
        return self.driver.execute_script("return %s" % media_type[typex])
        #return self.driver.execute_script( "return window._sharedData.entry_data." "PostPage[0].graphql.shortcode_media." "edge_media_to_comment.count")


    def scroll_down(self, wait=0.3):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        randmized_sleep(wait)

    def scroll_up(self, offset=-1, wait=2):
        if offset == -1:
            self.driver.execute_script("window.scrollTo(0, 0)")
        else:
            self.driver.execute_script("window.scrollBy(0, -%s)" % offset)
        randmized_sleep(wait)

    def js_click(self, elem):
        self.driver.execute_script("arguments[0].click();", elem)

    def open_new_tab(self, url, t = 0):
        unit = 185 / 3600
        duration = round(time.time() - self.timer)
        should = self.counter.lcnt / unit

        reset = False
        while self.counter.lcnt / duration > unit:
            log.info('counter=%s, %s/%s > %s', self.counter.gcnt, self.counter.lcnt, duration, unit)
            randmized_sleep(should - duration)
            duration = round(time.time() - self.timer)
            reset = True
        
        if reset:
            self.timer = time.time()
            self.counter.lcnt = 0

        self.driver.execute_script("window.open('%s');" % url)
        self.counter.lcnt += 1
        self.counter.gcnt += 1
        n = len(self.driver.window_handles)
        self.driver.switch_to.window(self.driver.window_handles[n-1])
        if t != 0:
            randmized_sleep(t)

    def open_new_tab2(self, url, t = 0):
        unit = 190 / 3600
        duration = round(time.time() - self.timer)
        should = self.counter.gcnt / unit
        while self.counter.gcnt / duration > unit:
            log.info('counter, %s/%s > %s', self.counter.gcnt, duration, unit)
            randmized_sleep(should - duration)
            duration = round(time.time() - self.timer)

        self.driver.execute_script("window.open('%s');" % url)
        self.counter.gcnt += 1
        n = len(self.driver.window_handles)
        self.driver.switch_to.window(self.driver.window_handles[n-1])
        if t != 0:
            randmized_sleep(t)
        

    def close_current_tab(self):
        self.driver.close()
        n = len(self.driver.window_handles)
        self.driver.switch_to.window(self.driver.window_handles[n-1])

    def get_html(self):
        return self.driver.page_source
        
    def __del__(self):
        try:
            self.driver.quit()
        except Exception:
            pass


query_hash = 'bc3296d1ce80a24b1b6e40b1e72903f5'
query_hash = '9b498c08113f1e09617a1703c22b2f32'

headinfo={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',

}
pic_root = "/home/lab321/weixiao/code/drug_tracking/pic_data"
model = Model()



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

def get_json_by_url(url, data = None, proxy = None):
    while True:
        if data:
            r = requests.get(url, params = data, headers=headinfo, proxies = proxy)
        else:
            print(url, proxy)
            r = requests.get(url, headers=headinfo, proxies = proxy)
            
        if r.status_code != 200:
            print('request bad url=', url, ' status_code=', r.status_code)
            return None
        try:
            js_data = json.loads(r.text)
        except:
            # time.sleep(2.5)
            continue
        break
    
    return js_data

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

def fetch_post(shortcode, proxy = None):
    url  = f'https://www.instagram.com/p/{shortcode}/'
    if model.exist_post_by_shortcode(shortcode):        
        print('post exists: ', url)
        return True
    
    # resp = requests.get(url+'?__a=1', headers=headinfo, proxies=proxy)
    # resp = get_json_result(url)
    resp = get_json_by_url(url+'?__a=1', proxy=proxy)
    if resp is None:
        return False
    
    jsdata = resp['graphql']['shortcode_media']
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
        'is_drug_related': 9,
        'address_json': address_json,
    }

    # insert post
    model.insert_post(**post)
    # insert user info of the post
    fetch_user_info(post['owner_name'], proxy=proxy)
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
        # resp = requests.get(r'https://www.instagram.com/graphql/query/', params = data, headers=headinfo, proxies=proxy)
        resp = get_json_by_url(r'https://www.instagram.com/graphql/query/', data = data, proxies=proxy)
        # d = json.loads(resp.text)
        d = resp
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

def fetch_user_info(user_name, proxy = None):
    url = f'https://www.instagram.com/{user_name}/'
    # resp = requests.get(url+'?__a=1', headers=headinfo)
    # resp = requests.get(url+'?__a=1', headers=headinfo)
    # resp = get_json_result(url)
    resp = get_json_by_url(url+'?__a=1', proxy=proxy)
    if resp is None:
        return False

    if resp == '{}':
        print(f'user has been deleted!!!{user_name}')
        return 567

    jsdata = resp['graphql']['user']

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
            pic_name = store_thumb('/home/lab321/weixiao/code/drug_tracking/pic_data/user_thumb2/', pic_url)
            thumb_list.append(pic_name)
        
        if has_next_page and end_cursor is not None:
            data = {
                "query_hash": '44efc15d3c13342d02df0b5a9fa3d33f',
                "variables": '{"id":"'+ jsdata['id'] +'","first":12,"after":"'+ end_cursor +'"}',
            }
            # resp = requests.get(r'https://www.instagram.com/graphql/query/', params=data, headers=headinfo, proxies=proxy)
            resp = get_json_by_url(r'https://www.instagram.com/graphql/query/', data=data, proxy=proxy)

            # subjs = json.loads(resp.text)
            subjs = resp
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



def fetch_by_tagname(tag, proxy=None):
    url = f'https://www.instagram.com/explore/tags/{tag}/?__a=1'
    print("start fetch tag = ", url)
    index = 0
    tag_json = get_json_by_url(url, proxy=proxy)

    # return
    # with open("tag_example.json", "r") as fp:
    #     tag_json = json.load(fp)
    
    media = tag_json['graphql']['hashtag']['edge_hashtag_to_media']
    count = media['count']
    edges = media['edges'] # data here
    end_cursor = media['page_info']['end_cursor']
    has_next_page = media['page_info']['has_next_page']
    

    for node in edges:
        shortcode = node['node']['shortcode']
        fetch_post(shortcode, proxy=proxy)
        index += 1
    
    while has_next_page:
        r = random.randint(2, 12)
        data = {
            "query_hash": query_hash,
            "variables": '{"tag_name":"'+ tag +'","first":'+ r +',"after":"'+ end_cursor +'"}',
        }
        # resp = requests.get(r'https://www.instagram.com/graphql/query/', params = data, headers=headinfo, proxies=proxy)
        
        resp = get_json_by_url(r'https://www.instagram.com/graphql/query/', data = data, proxies=proxy)
        
        media = resp['data']['hashtag']['edge_hashtag_to_media']
        has_next_page = media['page_info']['has_next_page']
        end_cursor = media['page_info']['end_cursor']
        for node in media['edges']:
            shortcode = node['node']['shortcode']
            fetch_post(shortcode, proxy=proxy)
            index += 1
        
        if (index % 20 == 0):
            print('index=', index)
            



proxy = {
    "http":  "http://sp8770a9df:caleb091453@us.smartproxy.com:10000",
    "https": "http://sp8770a9df:caleb091453@us.smartproxy.com:10000"
    # "http":  "http://hwimujtrjn64pkk:3tZgjIzM90JFmzbK@residential.proxyscrape.com:8080",
    # "https": "http://hwimujtrjn64pkk:3tZgjIzM90JFmzbK@residential.proxyscrape.com:8080",
}

def main(args):
    browser = Browser(True, Gcnt())
    
    for tag in args.tags.split(","):
        fetch_by_tagname(tag, proxy)



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tags", type=str, required=True, help="tags needed to be crawled. Multiple tags are seperated by comma.")
    args = parser.parse_args()
    return args

# /home/lab321/weixiao/code/drug_tracking/pic_data/user_thumb
# /home/lab321/weixiao/code/drug_tracking/pic_data/user_thumb2

if __name__ == "__main__":
    args = parse_args()
    print("args: {}".format(args))
    main(args)
    
    
    # pxy = {
    #     "http":  "http://sp8770a9df:caleb091453@us.smartproxy.com:10000",
    #     "https": "http://sp8770a9df:caleb091453@us.smartproxy.com:10000"
    # }
    # r = requests.get('https://www.instagram.com/johnn1016/?__a=1', headers=headinfo, proxies=pxy)
    # print(r.text)
    # print(r.status_code)
    # print(type(r.text))

    # proxy = f'http://sp8770a9df:caleb091453@us.smartproxy.com:10000'

    # r = requests.get('http://httpbin.org/get', proxies= pxy)
    # print(r.text)
    
    # r = fetch_post("B1EmOdIAOs7")
    # fetch_user_info('oriwa.d.brams')

    # links_path = '/home/lab321/weixiao/data/ig_links/empty_text.csv'
    # with open(links_path, 'r') as f:
    #     idx = 1
    #     for line in f:
    #         shortcode = line.strip().rstrip('/').split('/')[-1]
    #         r = fetch_post(shortcode)
    #         print(r, idx)
    #         time.sleep(14)
    #         idx += 1



