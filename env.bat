@echo off
setlocal ENABLEDELAYEDEXPANSION

set env_name=py
set condapath=C:\ProgramData\Anaconda3\Scripts\activate.bat
set condapath2=C:\Users\%username%\Anaconda3\Scripts\activate.bat
set condapath3=C:\Users\%username%\miniconda3\Scripts\activate.bat


if exist %condapath% (
	echo %windir%\System32\cmd.exe "/K" %condapath% %env_name%
	%windir%\System32\cmd.exe "/K" %condapath% %env_name%
) else if exist %condapath2% (
	echo %windir%\System32\cmd.exe "/K" %condapath2% %env_name%
	%windir%\System32\cmd.exe "/K" %condapath2% %env_name%
) else if exist %condapath3% (
	echo %windir%\System32\cmd.exe "/K" %condapath3% %env_name%
	%windir%\System32\cmd.exe "/K" %condapath3% %env_name%
) 


