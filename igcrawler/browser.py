# coding: utf-8
import os
import platform
import time
import logging as log

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

from .utils import randmized_sleep

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
