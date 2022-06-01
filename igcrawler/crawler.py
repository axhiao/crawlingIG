# coding: utf-8
from __future__ import unicode_literals

import glob
import json
import os
import re
import sys
import time
import traceback
from builtins import open
from time import sleep
import logging as log
import requests
import uuid

from tqdm import tqdm
from requests.utils import quote

from igcrawler import secret
from igcrawler.browser import Browser
from igcrawler.exceptions import RetryException
from igcrawler.fetch import fetch_caption
from igcrawler.fetch import fetch_comments
from igcrawler.fetch import fetch_datetime
from igcrawler.fetch import fetch_imgs
from igcrawler.fetch import fetch_likers
from igcrawler.fetch import fetch_likes_plays
from igcrawler.fetch import fetch_details
from igcrawler.utils import instagram_int
from igcrawler.utils import randmized_sleep
from igcrawler.utils import retry
from igcrawler.utils import const_gis
from igcrawler.settings import HEAD
from igcrawler.settings import Relation, DrugTypeNew
from nnmodel.discriminator import Disc
from igcrawler.utils import Gcnt

import sys
sys.path.append('..')
from db.model import Model

class InsCrawler(object):
    URL = "https://www.instagram.com"
    RETRY_LIMIT = 10

    def __init__(self, weight_path, \
        user_name, user_pwd, \
        crawl_tag_cnt=100, has_screen=False, pic_dir = ""):
        super().__init__()
        self.browser = Browser(has_screen, Gcnt())
        self.page_height = 0
        self.crawl_tag_cnt = crawl_tag_cnt
        self.authtokens = tuple()
        self.login(user_name, user_pwd)
        # self.music()
        self.model = Model()
        self.ipaddr = re.compile(r'href="(?P<jsaddr>.+?)"')
        self.headers = HEAD
        if pic_dir == "":
            pwd = os.path.dirname(os.path.realpath(__file__))
            pic_dir = os.path.dirname(pwd) + os.sep + "pic_data"
        if not os.path.exists(pic_dir):
            os.makedirs(pic_dir)
        self.pic_root = pic_dir
        self.tagre = re.compile(r'#\w+\b')
        # self.discriminator = Disc(weight_path)
        self.timecheck = time.time()
        

    def music(self):
        url = 'https://www.instagram.com/explore/tags/music/'
        browser = self.browser
        browser.get(url)
        self.authtokens = self.get_tokens()
        log.info('get authtokens=%s', self.authtokens)


    def run_timecheck(self, tm = 600, sm = 600):
        # duration = time.time() - self.timecheck
        # if duration > tm:
        #     log.info('%s seconds has elapsed since %s. Sleep for %s seconds',\
        #          duration, self.timecheck, sm)
        #     time.sleep(sm)
        #     self.timecheck = time.time()
        return True


    def login(self, user_name, user_pwd):
        logurl = r'https://www.instagram.com/accounts/login/?source=auth_switcher'
        browser = self.browser
        browser.get(logurl)

        u_input = browser.find_one_by_xpath('//input[@name="username"]')
        # u_input.send_keys(secret.USERNAME)
        u_input.send_keys(user_name.strip())
        p_input = browser.find_one_by_xpath('//input[@name="password"]')
        # p_input.send_keys(secret.PASSWORD)
        p_input.send_keys(user_pwd)

        login_btn = browser.find_one_by_css(".L3NKy")
        login_btn.click()
        randmized_sleep(3)

        try:
            btn_tmp = browser.find_one_by_xpath('//button[@class="aOOlW   HoLwm "]')
            log.info('find promt div windown after log in')
            btn_tmp.click()
            randmized_sleep(2)
        except Exception:
            pass

        try:
            btn_tmp = browser.find_one_by_xpath('//button[@class="sqdOP yWX7d    y3zKF     "]')
            log.info("find promt info")
            btn_tmp.click()
            randmized_sleep(3)
        except Exception:
            pass

        try:
            btn_tmp = browser.find_one_by_xpath('//button[@class="_9-kt _9-kw"]')
            log.info("find promt info")
            btn_tmp.click()
            randmized_sleep(1)
        except Exception:
            pass


        @retry()
        def check_login():
            if browser.find_one_by_xpath('//input[@name="username"]'):
                raise RetryException()
            log.info('>>>login finished!!!<<<')
        try:
            check_login()
        except Exception as e:
            log.error("check_login(): %s", str(e))
            pass

        # browser.get('https://instagram.com/explore/tags/music', t=1)
        # self.authtokens = self.get_tokens()

    def get_tokens(self):
        self.browser.get(r'https://www.instagram.com/explore/tags/music/', t=1)
        randmized_sleep(3)
        rhx_gis = self.browser.get_js_data(typex='nonce')
        ppc = re.search(r'ProfilePageContainer.js/(.*?).js', self.browser.get_html()).group(1)
        r = requests.get('https://www.instagram.com/static/bundles/es6/ProfilePageContainer.js/' + ppc + '.js').text
        query_hash = re.findall(r'{value:!0}\);(?:var|const|let) .=\"([0-9a-f]{32})\"', r)[0]
        return tuple((rhx_gis, query_hash))

    def usernameToUserId(self, user):
        r = requests.get('https://www.instagram.com/web/search/topsearch/?query=' + user, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0'}).text

        if json.loads(r).get("message") == 'rate limited':
            print(
                '[x] Rate limit reached!\n[#] Unchecked Username: {}\n[!] Try again in a few minutes.\n'.format(user))
            exit()

        try:
            if json.loads(r)['users'][0]['user']['username'] == user:
                return json.loads(r)['users'][0]['user']['pk']
        except:
            return False

    def useridToUsername(self, userid):
        query_variable = '{"user_id":"' + str(userid) + '","include_reel":true}'
        header = {
            'X-Instagram-GIS': const_gis(self.authtokens, query_variable),
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        r = requests.get(
            'https://www.instagram.com/graphql/query/?query_hash=' + self.authtokens[1] + '&variables=' + query_variable,
            headers=header).text
        if json.loads(r).get("message") == 'rate limited':
            log.error('[x] Rate limit reached!\n[#] Unchecked ID: {}\n'.format(userid))
            return ""
        try:
            return json.loads(r)['data']['user']['reel']['user']['username']
        except:
            return ""


    def crawl_hashtag_233(self, hashtag):
        browser = self.browser
        url = 'https://www.instagram.com/explore/tags/%s/' % hashtag
        browser.open_new_tab(url, t=4)
        

        for div in browser.find_by_xpath('//div[@class="v1Nh3 kIKUG _bz0w"]'):
            # div.find_element_by_xpath('//a').click()
            div.find_element_by_css_selector("a").click()
            randmized_sleep(5)
            browser.find_one_by_xpath('//div[@class="NOTWr"] //button[@class="wpO6b  "]').click()
            

        pass


    def crawl_hashtag(self, hashtag):
        """
            crawl by hashtag.
        """
        browser = self.browser
        url = 'https://www.instagram.com/explore/tags/%s/' % hashtag
        browser.open_new_tab(url, t=4)
        log.info('crawl hashtag URL=%s', url)
        userset = set()
        try:
            tags = browser.get_js_data(typex='tag')
            if tags is None:
                log.error('%s server error !!! ', url)
                return
            if len(tags) == 0:
                log.error('URL=%s broken', url)
                # update hashtag status
                # if updating failed, insert a new broken one.
                self.model.update_tag_status(hashtag)
                return
            # insert related tags into db
            for x in tags['edge_hashtag_to_related_tags']['edges']:
                hashtag = x['node']['name']
                tag_dict = {
                    'id': uuid.uuid1().int>>80,
                    'name' : hashtag,
                }
                self.model.insert_hashtag(**tag_dict)

            tagcnt = 1e-7
            drugcnt = 0
            # 1. cache hashId for later iteration
            # https://www.instagram.com/explore/tags/mdmatherapy/
            # location word of queryId is 't.tagMedia.byTagName.get(n)).pagination'
            queryId = self._get_query_id(r't.tagMedia.byTagName.get(n)).pagination',\
                r'PageContainer.js')
            # 2. access top posts
            top_list = tags['edge_hashtag_to_top_posts']['edges']
            for x in top_list:
                # if not self.model.exist_post(x['node']['id']) \
                if self.is_drug_related(x['node']['thumbnail_src'])\
                    and self.fetch_post(x['node']['shortcode'])\
                    and self.run_timecheck():
                        drugcnt += 1
                        userid = x['node']['owner']['id']
                        if userid not in userset:
                            self.fetch_user_profile(userid)
                            userset.add(userid)

            tagcnt += len(top_list)    

            # 3. iterate post list
            recent_list = tags['edge_hashtag_to_media']['edges']
            for x in recent_list:
                # if not self.model.exist_post(x['node']['id']) \
                if self.is_drug_related(x['node']['thumbnail_src'])\
                    and self.fetch_post(x['node']['shortcode'])\
                    and self.run_timecheck():
                    drugcnt += 1
                    userid = x['node']['owner']['id']
                    if userid not in userset:
                        self.fetch_user_profile(x['node']['owner']['id'])
                        userset.add(userid)

            tagcnt += len(recent_list)

            url_parent = r'https://www.instagram.com/graphql/query/?'
            pageinfo = tags['edge_hashtag_to_media']['page_info']

            while pageinfo['has_next_page'] and tagcnt < self.crawl_tag_cnt:
                variables = {
                    "tag_name": hashtag,
                    "first": 18,
                    "after": pageinfo['end_cursor']
                }
                url = '{}query_hash={}&variables={}'.format(
                    url_parent, queryId, json.dumps(variables)
                )
                log.info('graphql tag URL: %s ', url)
                browser.open_new_tab(url, t=4)
                jsn = json.loads(browser.get_json_text())
                browser.close_current_tab()
                if jsn['status'] != 'ok':
                    log.error('get more tags graphql fail, url=%s', url)
                    break
                media = jsn['data']['hashtag']['edge_hashtag_to_media']
                for x in media['edges']:
                    # if not self.model.exist_post(x['node']['id']) \
                    if self.is_drug_related(x['node']['thumbnail_src'])\
                        and self.fetch_post(x['node']['shortcode'])\
                        and self.run_timecheck():
                        drugcnt += 1
                        userid = x['node']['owner']['id']
                        if userid not in userset:
                            self.fetch_user_profile(x['node']['owner']['id'])
                            userset.add(userid)
                tagcnt += len(media['edges'])
                pageinfo = media['page_info']

            # insert into hashtag table 
            try:
                tag_dict = {
                    'id' : tags['id'],
                    'name' : tags['name'],
                    'pic_url': tags['profile_pic_url'],
                    'post_no' : tags['edge_hashtag_to_media']['count'], # use this field to compute prob.
                    'related_tags': ','.join([x['node']['name'] for x in tags['edge_hashtag_to_related_tags']['edges']]),
                    'prob' : drugcnt / tagcnt,
                }
                # insert OR update
                self.model.insert_hashtag(**tag_dict)
            except Exception as e:
                log.error('insert hashtag failed. %s \n-- %s', str(tag_dict), str(e))
                return 
        except Exception as e:
            log.error('crawl hashtag=%s error=%s', hashtag, e, exc_info=True)
        finally:
            browser.close_current_tab()
        pass
    
    def is_drug_related(self, url):
        resp = requests.get(url, headers=HEAD)
        if resp.status_code == 200:
            classidx = self.discriminator.predict(resp)
            idx = classidx.item()
            if idx == DrugTypeNew.UNRELATED.value:
                return False
            return True
            

    def store_pic(self, store_path, url):
        pic_name = url.split('?')[0].split('/')[-1]
        sub_dir = pic_name[0:3]
        store_path.rstrip(os.sep)
        full_dir = store_path + os.sep + sub_dir
        if not os.path.exists(full_dir):
            os.makedirs(full_dir)
        full_path = full_dir + os.sep + pic_name
        resp = requests.get(url, headers=HEAD)
        if resp.status_code == 200:
            classidx = self.discriminator.predict(resp)
            if classidx.item() == DrugTypeNew.UNRELATED.value:
                return "", ""
            with open(full_path, 'wb') as fp:
                fp.write(resp.content)
            return sub_dir + os.sep + pic_name, classidx.item()
        else:
            return None, None

    def _query_api(self, queryId, variables):
        url_parent = r'https://www.instagram.com/graphql/query/?'
        url = '{}query_hash={}&variables={}'.format(
                url_parent, queryId, json.dumps(variables)
            )
        self.browser.open_new_tab(url, t=4)
        randmized_sleep(1)
        jsn = json.loads(self.browser.get_json_text())
        self.browser.close_current_tab()
        return jsn


    def _get_query_id(self, location_word, jsfile):
        """
        Must first access tag link: https://instagram.com/explore/tags/mdmatherapy
        or post link,
        or something like that.
        """
        browser = self.browser
        html = browser.get_html()
        idx = html.find(jsfile)
        if idx == -1:
            log.error('did not find PageContainer.js in page:%s', browser.current_url)
            return
        hashjs = InsCrawler.URL + self.ipaddr.findall(html[idx-50 : idx+200])[0]
        jstext = requests.get(hashjs, self.headers).text
        idx = jstext.find(location_word)
        if idx == -1:
            log.error('did not find hashId in %s', hashjs)
            return
        queryId = jstext[idx: idx + 200].split(':"')[1].split('",')[0]
        return queryId

    # def _dismiss_login_prompt(self):
    #     ele_login = self.browser.find_one(".Ls00D .Szr5J")
    #     if ele_login:
    #         ele_login.click()

    def fetch_post(self, shortcode):
        """
            First confirm if this shortcode has been visited.
            Also before fetching, insert post -> hashtag relation,
            which should be calling fetch_post before.
        """

        if self.model.exist_post_by_shortcode(shortcode):
            return True

        url = 'https://www.instagram.com/p/%s/' % shortcode
        browser = self.browser
        browser.open_new_tab(url, t=4)
        try:
            classidx = 0
            comments_queryid = self._get_query_id(\
            r't.threadedComments.parentByPostId.get(n).pagination',\
            r'Consumer.js')
            jsdata = browser.get_js_data('post', shortcode)
            if not jsdata:
                log.error('get_js_data failed. link=%s', url)
                return
            try:
                if jsdata['location'] is None:
                    location_id = 0
                    address_json = ''
                else:
                    location_id = jsdata['location']['id']
                    address_json = jsdata['location']['address_json']
                caption = jsdata['edge_media_to_caption']['edges']
                if len(caption) == 0:
                    caption = ''
                else:
                    caption = caption[0]['node']['text']
                # determine whether the pic is realted to drug and store local.
                pic_path, classidx = self.store_pic(self.pic_root, jsdata['display_resources'][0]['src'])

                if pic_path is None:
                    log.error('download pic error:link= %s', jsdata['display_resources'][0]['src'])
                    return False
                if pic_path == "":
                    # drug unrelated!
                    return False
                pic_url = jsdata['display_resources'][-1]['src']
            except Exception as e:
                log.error('URL=%s, %s', url, str(e), exc_info=True)
                return False

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
                'is_drug_related': classidx,
                'address_json': address_json,
            }
            self.model.insert_post(**post)
            tag_list = self.tagre.findall(caption)
            if tag_list:
                self.model.insert_hashtags(list(map(lambda s:s.lstrip('#'), tag_list)))
            #  ---------------
            #  Fetch comments |
            #  ---------------
            self._fetch_comments(comments_queryid, shortcode, jsdata)
            return True
        finally:
            browser.close_current_tab()
        pass

    def _fetch_comments(self, cmt_queryid, post_shortcode, post_jsdata, cmtcnt=20):
        """
        https://www.instagram.com/graphql/query/?
        query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&
        variables={"shortcode": "B8zPVu0l9bE", "first": 12, "after": "{\"cached_comments_cursor\": \"17858162317738796\", \"bifilter_token\": \"KDEBDgA4ACAAGAAQAAgACAAIAOP_G-3vIff5DdnI9O9E0nsfv_89__cy79SUQ9j4sogAAA==\"}"}
        """
        retry = 0
        browser = self.browser
        json_data = post_jsdata['edge_media_to_parent_comment']

        has_next_page = True
        cnt = 0
        while json_data['count'] > 0 and cnt < cmtcnt:
            cmt_list = json_data['edges']
            if cmt_list is None or len(cmt_list) == 0:
                if has_next_page and retry < InsCrawler.RETRY_LIMIT:
                    randmized_sleep()
                    retry += 2
                else:
                    break
            # store data    
            for c in cmt_list:
                cmt = c['node']
                try:
                    did_report_as_spam = cmt['did_report_as_spam']
                except:
                    did_report_as_spam = False
                comment = {
                    'id':cmt['id'],
                    'text':cmt['text'],
                    'created_at':cmt['created_at'],
                    'owner_id': cmt['owner']['id'],
                    'user_name':cmt['owner']['username'],
                    'like_by_no':cmt['edge_liked_by']['count'],
                    'did_report_as_spam':did_report_as_spam,
                    'post_id': post_jsdata['id'],
                }
                # print(comment)
                if self.model.insert_comment(**comment) == 0:
                    log.error('Duplicate comments inserted:%s', str(comment))
                cnt += 1
                relation = {
                    'from_id': cmt['id'],          # comment id
                    'to_id': post_jsdata['id'],    # post id
                    'type': Relation.CMT_PST.value,# type
                }
                if self.model.insert_relation(**relation) == -1:
                    log.error('insert relation failed. %s', str(relation))
                
                taglist = self.tagre.findall(cmt['text'])
                if taglist:
                    self.model.insert_hashtags(list(map(lambda s:s.lstrip('#'), taglist)))

                # dealing with threaded comments
                # dealing with threaded comments
                self._fetch_sub_comments(cmt['id'], cmt['edge_threaded_comments'], post_jsdata['id'])

            # new page access
            has_next_page = json_data['page_info']['has_next_page']
            if not has_next_page:
                break
            cursor = json_data['page_info']['end_cursor']
            # This quote fucks me up!!!
            cur_str = json.dumps(cursor).strip('\"')
            qry_var = {"shortcode":post_shortcode,"first":12,"after": cur_str}
            url = 'https://www.instagram.com/graphql/query/?query_hash=%s&variables=%s' % \
                    (cmt_queryid, json.dumps(qry_var))   
            
            log.info('graphql comment URL:%s', url)
            browser.open_new_tab(url, t=4)
            jsn = json.loads(browser.get_json_text())
            browser.close_current_tab()
            if jsn['status'] != 'ok':
                log.error('fetch comments failed! link=%s', url)
                return
            if jsn['status'] == 'fail' and jsn['message'].startswith('Please wait'):
                log.error("access rate too high, sleep for a sec!, url=%s", url)
                time.sleep(20) 
                log.info('Again: graphql comment URL:%s', url)
                browser.open_new_tab(url, t=4)
                jsn = json.loads(browser.get_json_text())
                browser.close_current_tab()
                if jsn['status'] != 'ok':
                    log.error('again fetch comments failed! link=%s', url)
                    return
            # assign data for next iteration
            json_data = jsn['data']['shortcode_media']['edge_media_to_parent_comment']
        pass


    def _fetch_sub_comments(self, cmt_id, edge_threaded_comments, postid):
        """
            The same one comment not only belongs to one post_id(type=4),
            but also to comment_id(type=5). This happens when one person replies 
            in response and mention @another person. So this reply comment is also 
            a child-comment as @person's.
            +---------+-------+------+
            | from_id | to_id | type |
            +---------+-------+------+
            |     111 |   199 |   4  |
            +---------+-------+------+
            |     111 |   798 |   5  |
            +---------+-------+------+

        """
        retry = 0
        browser = self.browser
        has_next_page = True
        while edge_threaded_comments['count'] > 0:
            subcmt_list = edge_threaded_comments['edges']
            if subcmt_list is None or len(subcmt_list) == 0:
                if has_next_page and retry < InsCrawler.RETRY_LIMIT:
                    randmized_sleep()
                    retry += 3
                else:
                    break
            for edge in subcmt_list:
                cmt = edge['node']
                try:
                    did_report_as_spam = cmt['did_report_as_spam']
                except:
                    did_report_as_spam = False
                comment = {
                    'id':cmt['id'],
                    'text':cmt['text'],
                    'created_at':cmt['created_at'],
                    'owner_id': cmt['owner']['id'],
                    'user_name':cmt['owner']['username'],
                    'like_by_no':cmt['edge_liked_by']['count'],
                    'did_report_as_spam':did_report_as_spam,
                    'post_id': postid,
                }
                if self.model.insert_comment(**comment) == 0:
                    log.error('Duplicate sub-comments inserted:%s', str(comment))
                relation = {
                    'from_id': cmt['id'], # sub-comment id
                    'to_id': cmt_id,     # parent-comment id
                    'type': Relation.CMT_CMT.value, # type
                }
                if self.model.insert_relation(**relation) == -1:
                    log.error("insert relation failed. %s", str(relation))

                taglist = self.tagre.findall(cmt['text'])
                if taglist:
                    self.model.insert_hashtags(list(map(lambda s:s.lstrip('#'), taglist)))
            
            # new page access
            has_next_page = edge_threaded_comments['page_info']['has_next_page']
            if not has_next_page:
                break
            cursor = edge_threaded_comments['page_info']['end_cursor']
            cur_str = json.dumps(cursor).strip('\"')

            subcmt_queryid = self._get_query_id('t.threadedComments.childByParentId.get(n).pagination',\
                'Consumer.js')
            qry_var = {
                "comment_id":cmt_id,
                "first":6,
                "after":cur_str
            }
            url = 'https://www.instagram.com/graphql/query/?query_hash=%s&variables=%s' %\
                (subcmt_queryid, json.dumps(qry_var))
            log.info('graphql sub-comment URL:%s', url)
            browser.open_new_tab(url, t=4)
            jsn = json.loads(browser.get_json_text())
            browser.close_current_tab()
            if jsn['status'] != 'ok':
                log.error('fetch sub-comments failed! link=%s', url)
                return
            edge_threaded_comments = jsn['data']['comment']['edge_threaded_comments']
        pass

    # TODO 
    # find some condition when meeted fetching user profile.
    def fetch_user_profile(self, userid, postcnt = 20):
        # TODO change to update if exist(has done in insert function)
        if self.model.exist_user(userid):
            return

        browser = self.browser
        username = self.useridToUsername(userid)
        if username == "":
            log.error('useridToUsername failed!')
            return

        url = "%s/%s/" % (InsCrawler.URL, username)
        try:
            browser.open_new_tab(url, t=4)
            jsdata = browser.get_js_data('user') # get json data from window.
            if not jsdata:
                log.error('fetch user profile failed. URL=%s', url)
                return username
            query_id = self._get_query_id(\
                r't.profilePosts.byUserId.get(n))||void 0===s?void 0:s.pagination',
                r'ProfilePageContainer.js'
                ) # get query id from .js file
            if not query_id:
                log.error('get queryId from ProfilePageContainer.js failed. URL=%s', url)
                return username
            cnt = 1e-7
            retry = 0
            drugcnt = 0
            has_next_page = True
            media = jsdata['edge_owner_to_timeline_media']
            while media['count'] > 0:
                post_list = media['edges']
                if post_list is None or len(post_list) == 0:
                    if has_next_page and retry < InsCrawler.RETRY_LIMIT:
                        retry += 3
                    else:
                        break
                # --------------------------------
                # get each post under the user   |
                # --------------------------------
                for x in post_list:
                    if self.model.exist_post(x['node']['id']):
                        continue
                    if self.is_drug_related(x['node']['thumbnail_src'])\
                        and self.fetch_post(x['node']['shortcode']):
                        drugcnt += 1
                        continue
                cnt += len(post_list)
                has_next_page = media['page_info']['has_next_page']
                if not has_next_page or cnt >= postcnt:
                    break
                pageinfo = media['page_info']
                qryvar = {
                    "id":jsdata['id'],
                    "first":12,
                    "after":pageinfo['end_cursor'],
                }
                url = 'https://www.instagram.com/graphql/query/?query_hash=%s&variables=%s' %\
                    (query_id, json.dumps(qryvar))
                browser.open_new_tab(url, t=4)
                jsn = json.loads(browser.get_json_text())
                browser.close_current_tab()
                if jsn['status'] != 'ok':
                    log.error('fetch user-post failed! link=%s', url)
                    return
                media = jsn['data']['user']['edge_owner_to_timeline_media']

            user = {
                "id": userid,
                "user_name": username,
                "full_name": jsdata['full_name'],
                "follower_no": jsdata['edge_followed_by']['count'],
                "following_no": jsdata['edge_follow']['count'],
                "post_no": jsdata['edge_owner_to_timeline_media']['count'],
                "biography": jsdata['biography'],
                "external_url": jsdata['external_url'],
                "is_business_account": jsdata['is_business_account'],
                "is_joined_recently": jsdata['is_joined_recently'],
                "profile_pic": jsdata['profile_pic_url_hd'],
                "posts_drug_ratio": drugcnt/cnt
            }
            self.model.insert_user_duplicate_update(**user)
        finally:
            browser.close_current_tab()
        pass

    def get_user_profile(self, username):
        browser = self.browser
        url = "%s/%s/" % (InsCrawler.URL, username)
        browser.get(url)
        name = browser.find_one(".rhpdm")
        desc = browser.find_one(".-vDIg span")
        photo = browser.find_one("._6q-tv")
        statistics = [ele.text for ele in browser.find(".g47SY")]
        post_num, follower_num, following_num = statistics
        return {
            "name": name.text,
            "desc": desc.text if desc else None,
            "photo_url": photo.get_attribute("src"),
            "post_num": post_num,
            "follower_num": follower_num,
            "following_num": following_num,
        }

    def get_user_profile_from_script_shared_data(self, username):
        browser = self.browser
        url = "%s/%s/" % (InsCrawler.URL, username)
        browser.get(url)
        source = browser.driver.page_source
        p = re.compile(r"window._sharedData = (?P<json>.*?);</script>", re.DOTALL)
        json_data = re.search(p, source).group("json")
        data = json.loads(json_data)

        user_data = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]

        return {
            "name": user_data["full_name"],
            "desc": user_data["biography"],
            "photo_url": user_data["profile_pic_url_hd"],
            "post_num": user_data["edge_owner_to_timeline_media"]["count"],
            "follower_num": user_data["edge_followed_by"]["count"],
            "following_num": user_data["edge_follow"]["count"],
            "website": user_data["external_url"],
        }

    def get_user_posts(self, username, number=None, detail=False):
        user_profile = self.get_user_profile(username)
        if not number:
            number = instagram_int(user_profile["post_num"])

        # self._dismiss_login_prompt()

        if detail:
            return self._get_posts_full(number)
        else:
            return self._get_posts(number)

    def get_latest_posts_by_tag(self, tag, num):
        url = "%s/explore/tags/%s/" % (InsCrawler.URL, tag)
        self.browser.get(url)
        return self._get_posts(num)

    def auto_like(self, tag="", maximum=1000):
        self.login()
        browser = self.browser
        if tag:
            url = "%s/explore/tags/%s/" % (InsCrawler.URL, tag)
        else:
            url = "%s/explore/" % (InsCrawler.URL)
        self.browser.get(url)

        ele_post = browser.find_one(".v1Nh3 a")
        ele_post.click()

        for _ in range(maximum):
            heart = browser.find_one(".dCJp8 .glyphsSpriteHeart__outline__24__grey_9")
            if heart:
                heart.click()
                randmized_sleep(2)

            left_arrow = browser.find_one(".HBoOv")
            if left_arrow:
                left_arrow.click()
                randmized_sleep(2)
            else:
                break

    def _get_posts_full(self, num):
        @retry()
        def check_next_post(cur_key):
            ele_a_datetime = browser.find_one(".eo2As .c-Yi7")

            # It takes time to load the post for some users with slow network
            if ele_a_datetime is None:
                raise RetryException()

            next_key = ele_a_datetime.get_attribute("href")
            if cur_key == next_key:
                raise RetryException()

        browser = self.browser
        browser.implicitly_wait(1)
        browser.scroll_down()
        ele_post = browser.find_one(".v1Nh3 a")
        ele_post.click()
        dict_posts = {}

        pbar = tqdm(total=num)
        pbar.set_description("fetching")
        cur_key = None

        # Fetching all posts
        for _ in range(num):
            dict_post = {}

            # Fetching post detail
            try:
                check_next_post(cur_key)

                # Fetching datetime and url as key
                ele_a_datetime = browser.find_one(".eo2As .c-Yi7")
                cur_key = ele_a_datetime.get_attribute("href")
                dict_post["key"] = cur_key
                fetch_datetime(browser, dict_post)
                fetch_imgs(browser, dict_post)
                fetch_likes_plays(browser, dict_post)
                fetch_likers(browser, dict_post)
                fetch_caption(browser, dict_post)
                fetch_comments(browser, dict_post)

            except RetryException:
                sys.stderr.write(
                    "\x1b[1;31m"
                    + "Failed to fetch the post: "
                    + cur_key or 'URL not fetched'
                    + "\x1b[0m"
                    + "\n"
                )
                break

            except Exception:
                sys.stderr.write(
                    "\x1b[1;31m"
                    + "Failed to fetch the post: "
                    + cur_key if isinstance(cur_key,str) else 'URL not fetched'
                    + "\x1b[0m"
                    + "\n"
                )
                traceback.print_exc()

            # self.log(json.dumps(dict_post, ensure_ascii=False))
            dict_posts[browser.current_url] = dict_post

            pbar.update(1)
            left_arrow = browser.find_one(".HBoOv")
            if left_arrow:
                left_arrow.click()

        pbar.close()
        posts = list(dict_posts.values())
        if posts:
            posts.sort(key=lambda post: post["datetime"], reverse=True)
        return posts

    def _get_posts(self, num):
        """
            To get posts, we have to click on the load more
            button and make the browser call post api.
        """
        TIMEOUT = 600
        browser = self.browser
        key_set = set()
        posts = []
        pre_post_num = 0
        wait_time = 1

        pbar = tqdm(total=num)

        def start_fetching(pre_post_num, wait_time):
            ele_posts = browser.find(".v1Nh3 a")
            for ele in ele_posts:
                key = ele.get_attribute("href")
                if key not in key_set:
                    dict_post = { "key": key }
                    ele_img = browser.find_one(".KL4Bh img", ele)
                    dict_post["caption"] = ele_img.get_attribute("alt")
                    dict_post["img_url"] = ele_img.get_attribute("src")

                    fetch_details(browser, dict_post)

                    key_set.add(key)
                    posts.append(dict_post)

                    if len(posts) == num:
                        break

            if pre_post_num == len(posts):
                pbar.set_description("Wait for %s sec" % (wait_time))
                sleep(wait_time)
                pbar.set_description("fetching")

                wait_time *= 2
                browser.scroll_up(300)
            else:
                wait_time = 1

            pre_post_num = len(posts)
            browser.scroll_down()

            return pre_post_num, wait_time

        pbar.set_description("fetching")
        while len(posts) < num and wait_time < TIMEOUT:
            post_num, wait_time = start_fetching(pre_post_num, wait_time)
            pbar.update(post_num - pre_post_num)
            pre_post_num = post_num

            loading = browser.find_one(".W1Bne")
            if not loading and wait_time > TIMEOUT / 2:
                break

        pbar.close()
        print("Done. Fetched %s posts." % (min(len(posts), num)))
        return posts[:num]

