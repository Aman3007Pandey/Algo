from datetime import datetime

now = datetime.now()
WORKSHEET_NAME = now.strftime("%B ") + str(now.day)
print (WORKSHEET_NAME)