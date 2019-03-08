#!/bin/bash
olddate=$(</users/fjh1997/date.txt)
olddate=${olddate:0:11}
curdate="$(date)"
curdate=${curdate:0:11}
if [[ "$olddate" != "$curdate" ]] ; then
 date >/users/fjh1997/date.txt
 shutdown -h now
fi
