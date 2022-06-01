# coding: utf-8

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

import time


service_args = ["--ignore-ssl-errors=true"]
chrome_options = Options()
# if not has_screen:
#     chrome_options.add_argument("--headless")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--no-sandbox")

chrome_path =  "./igcrawler/bin/chromedriver" 
driver = webdriver.Chrome(
    executable_path = chrome_path,
    service_args = service_args,
    chrome_options = chrome_options,
)
driver.implicitly_wait(5)


driver.get(r'https://www.instagram.com/explore/tags/fit/')


time.sleep(3)
# rhx_gis = driver.get_js_data(typex='nonce')
jsdata = driver.execute_script("window._sharedData")

# ppc = re.search(r'ProfilePageContainer.js/(.*?).js', self.browser.get_html()).group(1)
# r = requests.get('https://www.instagram.com/static/bundles/es6/ProfilePageContainer.js/' + ppc + '.js').text
# query_hash = re.findall(r'{value:!0}\);(?:var|const|let) .=\"([0-9a-f]{32})\"', r)[0]
# return tuple((rhx_gis, query_hash))

print(jsdata)