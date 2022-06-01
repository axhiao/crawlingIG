from selenium import webdriver
from selenium.webdriver.chrome.options import Options
 
 
ops = Options()
# ops.add_argument('--headless')
# ops.add_argument('--no-sandbox')
# ops.add_argument('--disable-dev-shm-usage')
# ops.add_argument('--disable-gpu')
# print('--proxy-server=http://%s' % proxy)
ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36'
# ops.add_argument('--user-agent=%s' % ua)
# ops.add_argument('--proxy-server=http://@us.smartproxy.com:10000')


chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--user-agent=%s' % ua)
# chrome_options.add_argument('--proxy-server=http://@us.smartproxy.com:10000')
        
        
driver = webdriver.Chrome(executable_path=r"bin/chromedriver", options=chrome_options)

driver.delete_all_cookies()
driver.maximize_window()

driver.get("http://httpbin.org/get")
driver.get("https://www.instagram.com/johnn1016/?__a=1")
print(driver.page_source)
input()
driver.quit()