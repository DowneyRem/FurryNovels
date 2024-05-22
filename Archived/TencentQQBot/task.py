#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import datetime
import subprocess

import schedule

from config import testMode


count = 0
python = sys.executable
script = os.path.join(os.getcwd(), "bot.py")


def runBot():
	global count
	count += 1
	print(f"{count} Run  {datetime.datetime.now()}")
	popen = subprocess.Popen([python, script], creationflags=subprocess.CREATE_NEW_CONSOLE)
	
	if testMode:
		time.sleep(5)  # bot 运行时间；持续运行时间
	else:
		time.sleep(10*60)  # bot 运行时间
		
	print(f"{count} Kill {datetime.datetime.now()}\n")
	popen.kill()
	
	
def main():
	print(f"{testMode=}\n")
	runBot()
	schedule.every().seconds.do(runBot)
	while True:
		schedule.run_pending()
		time.sleep(1)

	
if __name__ == '__main__':
	main()
	