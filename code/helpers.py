import json
import constant
import inspect

myself = lambda: inspect.stack()[1][3]

def get_all_player_ids():
	#go through every team
	masterList = []
	fp = open(f"../db/{constant.ROSTER_FILE}")
	allRosters = json.load(fp)

	for team in allRosters:
		print(team["teamCode"])
		for player in (team["forwards"] + team["defensemen"]):
			masterList.append(player["id"])
	
	print(f"{myself()}: ...all player list returning with count: {len(masterList)}")
	return masterList