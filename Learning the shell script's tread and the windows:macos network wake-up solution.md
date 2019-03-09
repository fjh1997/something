# Learning the shell script's tread and the windows/macos network wake-up solution

## problem to solve

I am studying at a university in China, and the network and electricity of the dormitory are often severely restricted. For example, at 11:30 on weekdays, the network and electricity must be off on time, which prevents me  remotely waking up my computer through the network card.  (The NVRAM information of the network card will be lost after power off, you need to power on and restart once to reconfigure NVRAM)。 but  since it‘s inconvenient get up every morning to open the computer just for this. It is better to let it start automatically when the power is restored every morning. However, the problem is coming again.  It is unnecessary to keep the computer on when nobody uses it. So I should make the computer  automatically shutdown for the first time power on every day.
## solution
### 0.prerequisites 
<br>1.a computer that supports Wake on LAN
<br>2.A VPS, Alibaba Cloud or Tencent Cloud both ok，which should have installed the Linux system.
<br>3.there is an embedded device that can send wake-up packages  in the LAN where the computer is woken up (the router with OpenWrt installed, etc.)
### 1.Setting the network card / BIOS / operating system
First, you need to enable a network wakeup feature in bios. There are many ways to do this you can find on Google. I won't say much here. Another point to note is that you must disable the fast-boot feature, which often blocks network wake-ups.  you should also set the network card through the device manager of windows, to enable the features of network wake-up, magic packet, etc. And also disable the feature of energy saving，this feature often causes the power supply of the network card to be canceled after computer being turned off for a period of time, resulting in failure to wake up normally. Of course, the BIOS must also enable the restore (power on)after AC Power Loss function.
### 2.Install Wake on LAN software
In order to be able to wake up the computer remotely, the best way is to have an active machine on the LAN to send a network wake-up packet consisting of several MAC addresses of the target machine and FFFFFFFFFs to the target machine. This protocol was created long time ago. Although there are few people  use it, it still exists.
Currently, you can find many software online that supports Wake on LAN :
<br>1.Depicus' Wake on LAN (https://www.depicus.com/wake-on-lan/) supports port forwarding and other functions. After port mapping, Even Wake on WAN can be implemented. However, it is a graphical interface software, so, keep an  machine  on to wake up another power-offed machine violates my intention of energy saving . Fortunately, It is open-source, you can modify it as your wish.
<br>2.Etherwake or WOL in openwrt. I use etherwake, the specific method of use is not listed here.
### 3. Penetration NAT to connect openwrt using VPS’s Reverse tunnel
After implemented Password-free login between openwrt and vps via a couple of public key, creating the following script in openwrt as follows:
```shell
#!/bin/sh
icount=`ps -w|grep "ssh -Nfg"|grep -v grep|wc -l`
if [ $icount == 0 ];then
logger -t "ssh_remote" "ssh remote restart!"
ssh -Nfg -K 120 -R *:667:192.168.1.1:22 114.114.114.114 -p 26259 -l root
fi
```

114.114.114.114 and 26259 are the ip and ssh ports of vps. Since this reverse tunnel is relatively easy to break, it is recommended that you set the keepalive packet send time in sshd config. This keepalive function is to send a 0byte payload to the target host every once in a while. The keepalive packet tells the target host "I am still alive".
Just in case the ssh connction timeout and failed, you can also set up the following script to disconnect the reconnected reverse tunnel every hour.
```shell
#!/bin/sh
echo 'starting....'
echo "kill"
id=`ps -w | grep "ssh -Nfg" | grep -v grep | awk '{print $1;}' `
echo $id
kill $id
echo 'finish....'
```
The above scripts can be executed once per minute and every hour in the crontab. This will be able to control the router through the 667 port of the vps. Then start the software to wake up the host.


### 4.Set  task scheduler of windows or launchd of MacOs

The two system softwares in the above title can easily implement the  script execute on boot function. The required scripts are as follows:
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
olddate=$(</users/fjh1997/date.txt)
olddate=${olddate:0:11}
curdate="$(date)"
curdate=${curdate:0:11}
if [[ "$olddate" != "$curdate" ]] ; then
 date >/users/fjh1997/date.txt
 shutdown -h now
fi
```
The functions of the above two scripts are similar. They check the date recorded in the file first. If the date is different from the current date, indicating that the script has not been executed today, execute it (shutdown) and record the date.
<br>The setting of windows is relatively simple. Set the script  starts every time the user logs on weekday in the task scheduler is OK. The mac os setting is more complicated. You need to configure a file named com.shutdown.plist as follows (the
Script path needs to be inclueded ):

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
Put the above plist file into the following directory, change the owner, and make sure that there is root privileges (after all, the shutdown command need super user), then use launchdctl to load.

><br> 	/Library/LaunchDaemons/
<br>/System/Library/LaunchDaemons/

```shell
sudo chown root /Library/LaunchDaemons/com.shutdown.plist
sudo chown root /System/Library/LaunchDaemons/com.shutdown.plist
sudo launchdctl load /System/Library/LaunchDaemons/com.shutdown.plist
```

## Points need to be noted
The most important issue is the issue of shell scripts, which is also the most frequently encountered problem. A shell script is equivalent to a way to automatically invoke system commands in a script file. System commands often require ** parameters**, which is doomed that Every symbol and even a string in a shell script is treated as a ** parameter**, so you should not leave a space, as shown below.

- if [[ "aaa" != "aaa" ]]
- if [[ "aaa" != "aaa"]]
-  if [[ "aaa" !="aaa" ]]
-  if[[ "aaa" != "aaa" ]]
<br>These four shell commands for comparing strings, only the first one is correct, the rest will be wrong, because when the shell script runs, each command is parsed into program + parameters to run, even including [[ Such symbols, these symbols are run as parameters. Therefore, parameters and parameters, parameters and programs must be separated by ** spaces **, only then the script can be executed smoothly!
<br>The second thing to note is that the scripts should run with permissions. This is  known to all, I just briefly mention it as below.

```shell
sudo chmod a+x /users/fjh1997/shutdown.sh
```

### My github repository and script file

Link: [github](https://github.com/fjh1997/something).
