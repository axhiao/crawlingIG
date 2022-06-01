from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

import time
import random
from time import sleep

from tqdm import tqdm
from collections import OrderedDict

chromepath = r'E:\\chromedriver.exe'
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(
            executable_path = chromepath,
            service_args=["--ignore-ssl-errors=true"],
            options=chrome_options,
        )
# //*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[2]/div/label/input
logurl = r'https://www.instagram.com/accounts/login/?source=auth_switcher'
driver.get(logurl)

WebDriverWait(driver, 9).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"]'))
            )

u_input = driver.find_element_by_xpath('//input[@name="username"]')
u_input.send_keys('chenyisheng0725')
u_input = driver.find_element_by_xpath('//input[@name="password"]')
u_input.send_keys('eT*&ExBQ:sC+Je9')
login_btn =driver.find_element(By.CSS_SELECTOR, '.L3NKy')
login_btn.click()

time.sleep(3)
try:
    btn_tmp = driver.find_element_by_xpath('//button[@class="aOOlW   HoLwm "]')
    print('find button')
    btn_tmp.click()
except NoSuchElementException:
    print('not find button')
    pass



print('driver ------->>>>>  get ')
driver.get(r'https://www.instagram.com/explore/tags/music/')


#elems = driver.find_elements(By.CSS_SELECTOR, '.v1Nh3 a')
#elems = driver.find_elements_by_css_selector('.FFVAD')
# s = set()
# t = 0
# for i in range(10):
#     elems = driver.find_elements(By.CSS_SELECTOR, '.v1Nh3 a')

#     for e in elems:
#         # print(e.get_attribute("href"))
#         id = e.get_attribute("href").split('p/')[1]
#         if id not in s:
#             t += 1
#             print(t, '==>', id)
#             s.add(id)
        
#     driver.execute_script('''
#         window.scrollBy({
#             top: 963,
#             left: 100,
#             behavior: 'smooth'
#         });
#     ''')
#     time.sleep(3)

# print(s)


# driver.close()

"""
    To get posts, we have to click on the load more
    button and make the browser call post api.
"""
TIMEOUT = 600
browser = driver
key_set = set()
posts = []
pre_post_num = 0
wait_time = 1

num = 50
pbar = tqdm(total = num)

def fetch_initial_comment(browser, dict_post):
    comments_elem = browser.find_element(By.CSS_SELECTOR, "ul.XQXOT")
    first_post_elem = comments_elem.find_element(By.CSS_SELECTOR, ".ZyFrc")
    try:
        caption = first_post_elem.find_element(By.CSS_SELECTOR, "span")
    except NoSuchElementException:
        caption = first_post_elem.find_element_by_xpath('//div[@class="C4VMK"]//h1')
    if caption:
        dict_post["description"] = caption.text

def randmized_sleep(average=1):
    _min, _max = average * 1 / 2, average * 3 / 2
    sleep(random.uniform(_min, _max))

def fetch_details(browser, dict_post):
    # browser.open_new_tab(dict_post["key"])
    browser.execute_script("window.open('%s');" % dict_post["key"])
    browser.switch_to.window(browser.window_handles[1])

    try:
        username = browser.find_element(By.CSS_SELECTOR, "a.FPmhX")
        location = None#browser.find_element(By.CSS_SELECTOR, "a.O4GlU")
    except NoSuchElementException:
        print('link=[%s] is broken.' % browser.current_url)
        browser.close()
        browser.switch_to.window(browser.window_handles[0])
        return

    if username:
        dict_post["username"] = username.text
    if location:
        dict_post["location"] = location.text

    fetch_initial_comment(browser, dict_post)
    # browser.close_current_tab()
    browser.close()
    browser.switch_to.window(browser.window_handles[0])

    

def start_fetching(pre_post_num, wait_time):
    scoll_no = 0
    ele_posts = browser.find_elements(By.CSS_SELECTOR, ".v1Nh3 a")
    print('>>>>', len(ele_posts), '<<<<<<<<<====')
    try:
        for ele in ele_posts:
            key = ele.get_attribute("href")
            if key not in key_set:
                dict_post = { "key": key }
                ele_img = ele.find_element(By.CSS_SELECTOR, ".KL4Bh img")
                dict_post["caption"] = ele_img.get_attribute("alt")
                # print(ele_img.get_attribute("srcset"))
                dict_post["img_url"] = ele_img.get_attribute("srcset").split(',')[0].split(' ')[0] # get minimal resolution pic
                # fetch details of a post
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
            # browser.scroll_up(300)
            browser.execute_script("window.scrollBy(0, -%s)" % 300)
        else:
            wait_time = 1

        pre_post_num = len(posts)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        scoll_no += 1
        randmized_sleep(0.3)
    except StaleElementReferenceException:
        print('some element has been stale.')

    return pre_post_num, wait_time, scoll_no





if __name__ == '__main__':
    pbar.set_description("fetching")
    while len(posts) < num and wait_time < TIMEOUT:
        post_num, wait_time, scoll_no = start_fetching(pre_post_num, wait_time)
        # if post_num == pre_post_num:
        #     browser.get(r'https://www.instagram.com/explore/tags/music/')
        #     browser.execute_script("window.scrollTo(0, document.body.scrollHeight * %d)" % scoll_no)
        pbar.update(post_num - pre_post_num)
        pre_post_num = post_num

        # loading = browser.find_element(By.CSS_SELECTOR, ".W1Bne")
        # if not loading and wait_time > TIMEOUT / 2:
        #     break

    pbar.close()
    print("Done. Fetched %s posts." % (min(len(posts), num)))

    print( posts[:num] )

    with open('a.txt', 'a+') as f:
        f.write(str(posts))
        f.write('\n')
    pass
