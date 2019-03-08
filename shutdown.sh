#!/bin/bash
olddate=$(<date.txt)
olddate=${olddate:0:11}
curdate="$(date)"
curdate=${curdate:0:11}
if [[ "$olddate" != "$curdate" ]] ; then
 date >date.txt
 shutdown now
fi