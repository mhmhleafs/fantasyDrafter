import json
import constant
import inspect
from unidecode import unidecode

myself = lambda: inspect.stack()[1][3]

def get_all_player_ids():
	#go through every team
	masterList = []
	fp = open(f"../db/{constant.ROSTER_FILE}")
	allRosters = json.load(fp)

	for team in allRosters:
		for player in (team["forwards"] + team["defensemen"]):
			masterList.append(player["id"])
	
	print(f"{myself()}: ...all player list returning with count: {len(masterList)}")
	return masterList

def get_yahoo_position(playerName):
	fp = open(f"../db/{constant.YAHOO_RAW}", "r")
	playerData = json.load(fp)
	fp.close()

	if(not (any(unidecode(playerName) in pdata["name"] for pdata in playerData))):
		print(f"no match for {playerName}")
	else:
		for yplayer in playerData:
			if(unidecode(playerName) == yplayer["name"]):
				return yplayer["eligible_positions"]
	return -1

def get_yahoo_id(playerName):
	fp = open(f"../db/{constant.YAHOO_RAW}", "r")
	playerData = json.load(fp)
	fp.close()

	if(not (any(unidecode(playerName) in pdata["name"] for pdata in playerData))):
		print(f"no match for {playerName}")
	else:
		for yplayer in playerData:
			if(unidecode(playerName) == yplayer["name"]):
				return yplayer["player_id"]
	return -1

def add_stats(allPlayers, years, ignoreCurrentYear=False):
	print(f"{myself()}(allPlayers[{len(allPlayers)}], years={years})")
	#for each player
	for player in allPlayers[:]:
		if(player.surname in ["Petrovic"]):
			allPlayers.remove(player)
			continue
		player.weigh_stat('shp', years, ignoreCurrentYear)

def get_by_property(list=None, property=None, value=None):
	if(list is None or property is None or value is None):
		return None

	for player in list:
		if(getattr(player, property) == value):
			return player

	return 0
