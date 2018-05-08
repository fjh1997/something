#coding=utf-8
import time
import threading as thd
from splinter import Browser

def splinter(url):
	browser = Browser('firefox',headless=True)
	#browser = Browser()
	#login 126 email websize
	
	browser.visit(url)
    #wait web element loading
	time.sleep(0.5)
	#fill in account and password
	browser.find_by_name('luci_password').fill('root')
     #click the button of login
	browser.find_by_value('登录').click()
	time.sleep(0.5)
	#close the window of brower
	def fn():
		x=hash(browser.find_by_id('ZSTUVPN-ifc-description').first.value)
		if(x==-174366572):browser.execute_script("iface_shutdown('ZSTUVPN', true)")
		thd.Timer(10,fn).start()
	fn()
    
    
if __name__ == '__main__':
    websize ='http://192.168.1.1/cgi-bin/luci/admin/network/network'
    splinter(websize)
