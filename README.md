# 校园网openwrt自动拨号器 #
  校园网安装路由，刷入openwrt，通过l2tP协议成功登入校园网，但是有时会出现15分钟左右掉线的情况，每次都要打开浏览器192.168.1.1访问路由器拨号，于是打算完善一下路由器的功能，但路由器里面的代码看不太懂，转念一想不如用一个笨办法，简单粗暴，使用爬虫替我拨号不就行了？？

## 一、安装python27 ##
  注意其中用到的splinter的python包只适用python27，python3不行
## 二、安装火狐浏览器 ##
  这个不用多讲
## 三、安装pip ##
  pip是python包管理器，一般是自带的，如果没有也可参考别人教程https://blog.csdn.net/huhuang/article/details/60873882
## 四、使用pip安装splinter爬虫工具 ##
  按住shift+鼠标右键，可以在任一目录下打开cmd，在命令行里输入
         pip install splinter
	 
  如果报错，那可能是pip或者python的环境变量没设置好
## 五、下载geckodriver.exe ##
  这个在我的版本库中有，请自行下载，并放置在和python同一个环境变量的目录下
## 六、修改python脚本 ##
  用记事本打开post.js看里面的注释自行修改
## 六、启动python脚本 ##
	 python post.js
  可以根据浏览器的实际情况更改脚本，如果还有问题（很大概率），尝试使用启动图形化界面的脚本，一步步分析哪里错了。
