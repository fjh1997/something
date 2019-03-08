# 学习shell脚本的踩坑记以及windows/macos 网络唤醒的方案

## 问题出现

本人就读于国内某所普通一本的大学，宿舍的网络和电力经常受到严格的限制。比如工作日晚上11点半必定准时断电断网，导致我的网卡不能远程唤醒我的电脑（断电后网卡的NVRAM信息会丢失，需要开机关机一次以重新配置NVRAM），然而每天早上起来特地为了这个而开一次机实在太麻烦，不如等每天早上恢复供电的时候让他自然开机，然而问题又来了，开了机又不用岂不是耗费电能？所以要让电脑能够每天第一次启动自动关机才行。
## 解决方案
### 0.prerequisites 需要准备的东西
1.一台支持网络唤醒的电脑
2.一台VPS，阿里云腾讯云都行，安装了linux系统。
3.被唤醒电脑所在的局域网里有一个能发唤醒包的嵌入式设备（安装了openwrt的路由器等等）
### 1.设置网卡/BIOS/操作系统
首先，要在bios里设置网络唤醒，具体方法百度上有很多，这里不多说。另外要注意的一点是一定要关闭快速启动功能，这个功能常常让网络唤醒失效。还有windows的设备管理器里也要设置网卡，启用网络唤醒、魔术封包等功能，另外还要关闭环保节能的功能，这个功能往往导致网卡的供电在关机一段时间后取消，导致无法正常唤醒。当然，BIOS里也要设置断电来电开机功能。

### 2.安装网络唤醒软件
为了能够在远程唤醒电脑，最好的方法是在局域网里有一台活动的机器能够向待唤醒的机子发送由目标机的数个MAC地址和FFFFFFFFF组成的网络唤醒包，这个协议是很久以前遗留下来的，虽然用的人不多，但目前任然存在。
目前网上支持网络唤醒的软件有
<br>1.depicus 的Wake on LAN （https://www.depicus.com/wake-on-lan/）支持端口转发等功能，做好端口映射之后甚至可以实现Wake on WAN。遗憾的是这是个图形化界面的软件，让一台开着的机子去唤醒另一台关闭的机子违背了我们节能环保的初衷。不过据说源代码已经开放，大家可以去看看。
<br>2.openwrt里面的etherwake 以及WOL 。本人用的是etherwake，具体使用方法不加列述。
### 3.使用VPS公网反向穿透NAT连接openwrt
openwrt和vps之间实现免密钥登录后，在openwrt里创建以下脚本如下：

```shell
#!/bin/sh
icount=`ps -w|grep "ssh -Nfg"|grep -v grep|wc -l`
if [ $icount == 0 ];then
logger -t "ssh_remote" "ssh remote restart!"
ssh -Nfg -K 120 -R *:667:192.168.1.1:22 114.114.114.114 -p 26259 -l root
fi
```

其中114.114.114.114 和26259是vps的ip和ssh端口，由于这个反向隧道比较容易断，建议大家去sshd里设置一下keepalive的发送时间，这个keepalive功能在于每隔一段时间向目标主机发送一个0byte的数据包以告诉目标主机“我还活着”。
保险起见，还可以设置如下脚本来每小时断开重连反向隧道。

```shell
#!/bin/sh
echo 'starting....'
echo "kill"
id=`ps -w | grep "ssh -Nfg" | grep -v grep | awk '{print $1;}' `
echo $id
kill $id
echo 'finish....'
```
以上脚本分别每分钟和每小时在crontab里执行一次即可。这样就能够通过vps的667端口控制路由器进而启动软件唤醒主机。



### 4.设置windows任务计划或者macos的launchd

以上两个都能够简单实现开机启动功能，所需要的脚本分别如下：
windows：shutdown.bat

```bat
for /f "delims=" %%t in ('type date.log') do set str=%%t
if "%str%"=="%date%" (echo "haha"
) else ( 
>date.log echo %date%
C:\Windows\System32\shutdown.exe -s -t 10
)
pause
```
macOS：shutdown.sh

```bash
#!/bin/bash
olddate=$(<date.txt)
olddate=${olddate:0:11}
curdate="$(date)"
curdate=${curdate:0:11}
if [[ "$olddate" != "$curdate" ]] ; then
 date >date.txt
 shutdown now
fi
```
以上两个脚本的功能类似，都是先检查文件里记录的日期，如果日期和当前日期不一样，说明今天没有启动过该脚本，那就启动一下（关机呗）然后记录日期。
windows的设置较简单，在任务计划程序里设置工作日每次用户登录时启动该脚本就行了，mac os的则较复杂，需要配置一个plist文件如下（文件里需要写明脚本地址）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>com.shutdown</string>
	<key>Program</key>
	<array>
		<string>bash</string>
	</array>	<key>ProgramArguments</key>
	<array>
		<string>/users/fjh1997/shutdown.sh</string>
	</array>
	<key>RunAtLoad</key>
	<true/>
</dict>
</plist>
```
将上述的plist文件放入以下目录，确保有root权限执行（毕竟涉及shutdown命令）。

><br> 	/Library/LaunchDaemons/
<br>/System/Library/LaunchDaemons/


## 解决问题的过程中遇到的问题
其中最主要的问题是关于shell脚本的问题，也是踩坑最多的地方。shell脚本相当于在脚本文件中自动调用系统命令的一种方式，而系统命令往往是需要有**参数**的，这就注定了我们shell脚本中的每一个符号乃至字符串都是被当作**参数**来处理的，所以千万不能吝啬空格，举例如下。

- if [[ "aaa" != "aaa" ]]
- if [[ "aaa" != "aaa"]]
-  if [[ "aaa" !="aaa" ]]
-  if[[ "aaa" != "aaa" ]]
<br>这四句比较字符串的shell命令，只有第一个是对的，其余几个都会出错，因为shell脚本的运行是吧每一个命令解析为程序+参数来运行的，甚至包括了[[这样的符号，这些符号都是作为参数运行的，所以参数与参数，与程序之间都要有**空格**分开，脚本才能顺利执行！
第二个要注意的是脚本运行都是要加权限才能运行的，这个大家一般都知道，我就简单提一下。

```shell
sudo chmod a+x /users/fjh1997/shutdown.sh
```

### 我的github仓库地址以及脚本文件

链接: [github地址](https://github.com/fjh1997/something).
