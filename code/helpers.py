import json
import constant
import inspect
import csv
from unidecode import unidecode
import yahoo_fantasy_api as yfa

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
		pass
		#print(f"no match for {playerName}")
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

def get_by_property(list=None, property=None, value=None):
	if(list is None or property is None or value is None):
		return None

	for player in list:
		if(getattr(player, property) == value):
			return player

	return 0

#def cumulative_teams(teamJson):

def json_load(filepath):
	fp = open(f"../db/{filepath}", "r")
	retObject = json.load(fp)
	fp.close()

	return retObject

def json_dump(filepath, content):
	fp = open(f"../db/{filepath}", "w+")
	json.dump(content, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=3, separators=None)
	fp.close()

def add_average_stats(allPlayers, years, ignoreCurrentYear=False, bangers=False):
	print(f"{myself()}(allPlayers[{len(allPlayers)}], years={years})")
	#for each player
	for player in allPlayers[:]:
		#if(player.surname in ["Petrovic"]):
		#	allPlayers.remove(player)
		#	continue
		player.weigh_stat('shp', years, ignoreCurrentYear)
		if(bangers):
			player.weigh_stat('PPP', years, ignoreCurrentYear)
			player.weigh_stat('blocks', years, ignoreCurrentYear)
			player.weigh_stat('hits', years, ignoreCurrentYear)
			player.weigh_stat('faceoffWins', years, ignoreCurrentYear)
			player.weigh_stat('goals', years, ignoreCurrentYear)
			player.weigh_stat('assists', years, ignoreCurrentYear)
			player.weigh_stat('points', years, ignoreCurrentYear)
			player.weigh_stat('shots', years, ignoreCurrentYear)
			player.weigh_stat('fanPts', years, ignoreCurrentYear)


def get_target_stat_columns(year, targets):
	fp = open(f"../db/moneypuck/{year}_stats.csv")

	targetStatColumns = {}

	columns = fp.readline().split(',')
	for stat in targets:
		targetStatColumns[stat] = columns.index(stat)

	fp.close()

	return targetStatColumns


def update_mp_stats_map(years):
	master_mp_data = {}
	for year in years:
		singleYearData = {}
		with open(f"../db/moneypuck/{year}_stats.csv") as fp:
			reader = csv.DictReader(fp)
			for row in reader:
				#data adds {12345 : {stats as dictionary}}
				for key in row.keys():
					try:
						row[key] = int(row[key])
					except:
						try:
							row[key] = float(row[key])
						except:
							pass
				if(row["situation"] == "all"):
					singleYearData[row["playerId"]] = row
		master_mp_data[year] = singleYearData

	json_dump(f"{constant.MONEYPUCK_MASTER_STATS}", master_mp_data)

	
def get_other_stats(pid, year, stats):
	
	mpStats = json_load(f"{constant.MONEYPUCK_MASTER_STATS}")

	ret = {}

	for stat in stats:
		ret[stat] = mpStats[year][str(pid)][stat]
 
	return ret

#get positions that are usable (e.g. 2x C, 4x D, 1x Util)
def yh_get_available_positions(sc):

	#creates Game object (game refers to which sport, i.e. hockey)
	game = yfa.Game(sc, 'nhl')

	#creates League object out of kiki's wittle hockey weague
	lg = game.to_league('465.l.50290')

	positions = lg.positions()

	positionCounts = {}

	for posn in positions:
		if(posn not in ["IR+", "G", "BN"]):
			positionCounts[posn] = positions[posn]["count"]

	return positionCounts

def player_array_to_string(players):
	retString = "["
	for player in players:
		retString += f"({player.surname} {player.positions})"

		#if there are more players
		if(player != players[-1]):
			retString += ", "
	retString += "]"

	return retString

def lists_share_element(list1, list2):
	ret = False
	for l in list1:
		if(l in list2):
			ret = True

	return ret