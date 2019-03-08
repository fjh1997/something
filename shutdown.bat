for /f "delims=" %%t in ('type date.log') do set str=%%t
if "%str%"=="%date%" (echo "haha"
) else ( 
>date.log echo %date%
C:\Windows\System32\shutdown.exe -s -t 10
)
pause