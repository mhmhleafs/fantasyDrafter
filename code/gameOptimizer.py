#use myTeam to set which players are "permanently" on my team (should myTeam be yahoo ids?)
#somehow figure out how to maximise gp with a set number of adds/drops, and prioritizing forwards
#perhaps output static total gp vs maximized total gp

import classes
import datetime
import weekdates
import constant
import json

from yahoo_functions import *

sc = OAuth2(None, None, from_file='oauth2.json')
#yh_update_my_team(sc)

fp = open(f"../db/{constant.SCHEDULE_FILE}", "r")
masterSchedule = json.load(fp)
fp.close()


seasonStart = datetime.date(2025, 10, 6)

week_delta = datetime.timedelta(days=7)

all_weeks = weekdates.ALL_WEEKS

date_format = "%b %d %Y"


time_delta = datetime.timedelta(days=1)

availablePositions = yh_get_available_positions(sc)
print(availablePositions)

gameWeeks = []

#for each week
for i in range(1,2):#constant.REG_SZN_WEEKS + 1):
	print(f"---------START OF WEEK {i}---------")

	tempWeek = GameWeek(i)

	start_time = datetime.datetime.strptime(all_weeks[i]["Start"], date_format).date()
	print(i, start_time)
	end_time = datetime.datetime.strptime(all_weeks[i]["End"], date_format).date()
	print(i, end_time)

	currentDate = start_time

	dayNo = 0
	#for each day in the week:
	while (currentDate <= end_time):
		tempGameDay = []


		tempWeek.add_day()
		for game in masterSchedule.values():
			if(game["date"] == str(currentDate)):
				print(game)
				tempGameDay.append(game["teams"])
				
		tempWeek.add_game(dayNo, tempGameDay)
		print(currentDate)
		currentDate += time_delta
		dayNo += 1

	gameWeeks.append(tempWeek)
for w in gameWeeks:
	print(w)
#print(allWeeks)

#TOO MANY LAYERS OF [] BNEIGN ADDED RN