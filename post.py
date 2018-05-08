#coding=utf-8
import time
import threading as thd
from splinter import Browser

def splinter(url):
	browser = Browser('firefox',headless=True)
	#browser = Browser()
	#以上两个方式选择是否调用图形化界面的浏览器帮你拨号，第一种带图形化界面，用于测试问题
	
	browser.visit(url)
    #等待网页加载
	time.sleep(0.5)
	#加载后出现登录页面，需要输入密码才能访问
	browser.find_by_name('luci_password').fill('root')
     #点击登录按钮
	browser.find_by_value('登录').click()
	time.sleep(0.5)
	#以下启动一个无限循环用于检测是否掉线
	def fn():
		x=hash(browser.find_by_id('ZSTUVPN-ifc-description').first.value)
		#这里的id要根据你opwnwrt网页上的html元素修改，使用开发人员工具（基本所有浏览器都有）查看，主要是看返回的网络连接信息的hash值和网络连接失败的信息的hash值是否一样。
		if(x==-174366572):browser.execute_script("iface_shutdown('ZSTUVPN', true)")
		#在网页上调用javascript接口，相当于点击了连接按钮，后面的script也是用开发人员工具在网页上查看，把连接按钮组件onclick=“”这里面的函数复制下来
		thd.Timer(10,fn).start()#设置每十秒检测一次
	fn()
    
    
if __name__ == '__main__':
    websize ='http://192.168.1.1/cgi-bin/luci/admin/network/network'#设置成你要登录的网页
    splinter(websize)
