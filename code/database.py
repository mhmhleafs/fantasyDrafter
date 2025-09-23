import requests
import json
import constant
import inspect
import math
import csv

from unidecode import unidecode

from helpers import *
from classes import *

def update_rosters():
	print(f"{myself()}: Updating rosters...")

	masterTeamRosters = []

	for teamCode in constant.TEAM_CODES:

		req = f"https://api-web.nhle.com/v1/roster/{teamCode}/current"
		resp = requests.get(req)

		if(resp.status_code != 200):
			print(f"{myself()}: Response for {req} not OK, terminating with code {resp.status_code}...")
			exit()
		else:
			print(f"updating {teamCode}...")

		jason = json.loads(resp.text)

		masterTeamRosters.append(jason)
	
	print(f"Writing to {constant.ROSTER_FILE}...")

	fp = open(f"../db/{constant.ROSTER_FILE}", "w+")
	json.dump(masterTeamRosters, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=3, separators=None)
	fp.close()

	print('Process finished.')


def update_player_objects():
	print(f"{myself()}: updating player stats...")

	allPlayerList = []

	playerList = get_all_player_ids()

	count = 0
	for playerID in playerList:
		req = f"https://api-web.nhle.com/v1/player/{playerID}/landing"
		resp = requests.get(req)

		try:
			playerData = json.loads(resp.text)
		except:
			print(f"ERROR ON {playerID}")
			continue

		#progress bar logic
		current = math.ceil(count / 20)
		target = math.ceil(len(playerList) / 20)
		print(f"Populating stats: [{count}/{len(playerList)}] {current * '|'}{(target - current) * '.'}", end='\r')
		count += 1
		
		#some players no longer in NHL will error out, skip them
		try:
			playerData["currentTeamAbbrev"]
		except:
			continue

		positions = get_yahoo_position(f"{playerData["firstName"]["default"]} {playerData["lastName"]["default"]}")

		nhlSeasons = {}
		for season in playerData["seasonTotals"]:
			if(season["leagueAbbrev"] == "NHL" and season["gameTypeId"] == 2):
				nhlSeasons[season["season"]] = {
													"gp" : season["gamesPlayed"],
													"goals" : season["goals"],
													"assists" : season["assists"],
													"points" : season["points"],
													"fanPts" : 3 * season["goals"] + 2 * season["assists"],
													"shp" : season["shootingPctg"]
												}
		allPlayerList.append(
				{
				"id" : playerData["playerId"],
				"name" : f"{playerData["firstName"]["default"]} {playerData["lastName"]["default"]}",
				"surname" : playerData["lastName"]["default"],
				"seasonsPlayed" : len(nhlSeasons),
				"seasons" : nhlSeasons,
				"age" : 2025 - int((playerData["birthDate"]).split('-')[0]),
				"team" : playerData["currentTeamAbbrev"],
				"position" : playerData["position"],
				"positions" : positions
				}
			)

	fp = open(f"../db/{constant.PLAYER_OBJECTS_FILE}", "w+")
	json.dump(allPlayerList, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=3, separators=None)
	fp.close()

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
	return ["Util"]
	#quit()

def get_player_objects(seasons=-1):
	print(f"{myself()}(seasons={seasons})")
	fp = open(f"../db/{constant.PLAYER_OBJECTS_FILE}", "r")
	playerObjects = json.load(fp)

	allPlayers = []

	for player in playerObjects:
		#THIS IS WHERE FILTRATION HAPPENS
		if(len(player["seasons"]) >= seasons):
			temp = Player()
			temp.construct_from_json(player)

			if("20242025" in temp.seasons and "20232024" in temp.seasons):
				allPlayers.append(temp)

	return allPlayers

def add_stats(allPlayers, years, ignoreCurrentYear=False):
	print(f"{myself()}(allPlayers[{len(allPlayers)}], years={years})")
	#for each player
	for player in allPlayers[:]:
		if(player.surname in ["Petrovic"]):
			allPlayers.remove(player)
			continue
		player.weigh_stat('shp', years, ignoreCurrentYear)

def DEPRECATED_add_xg(allPlayers, years):

	mpData = {}

	for year in years:
		with open(f"../db/moneypuck/{year}_stats.csv") as fp:
			reader = csv.reader(fp)
			mpData[year] = list(reader)

	targetStats = [
		"playerId",
		"season",
		"situation",
		"I_F_xGoals"
	]

	targetStatCols = get_target_stat_columns(targetStats)

	focusedMpData = []
	#for each year
	for year in mpData.values():
		singleYearTempStats = []
		
		#for each line in the csv
		for line in year:

			#exclude 4v5,5v4,etc.
			if(line[targetStatCols['situation']] == "all"):
				singlePlayerTempStats = {}

				#for each stat to pull
				for targetStat in targetStatCols:

					#don't include situation in stats pulled
					if(targetStat != "situation"):

						#adjust season from 20xx format to 20xx20xy format
						if(targetStat == "season"):
							#below line does the following"2024" ==> "2024" + str(2024 + 1) ==> 20242025
							singlePlayerTempStats[targetStat] = line[targetStatCols[targetStat]] + str(int(line[targetStatCols[targetStat]]) + 1)
						else:
							singlePlayerTempStats[targetStat] = line[targetStatCols[targetStat]]
				singleYearTempStats.append(singlePlayerTempStats)
		focusedMpData.append(singleYearTempStats)

	#for each player
	for player in allPlayers[:]:

		#for every year of moneypuck data
		for year in focusedMpData:

			#for every line in the year's data
			for mpPlayerStats in year:

				#if current line matches current player, add xg to their season data
				if(mpPlayerStats["playerId"] == str(player.id)):
					player.update_xg(mpPlayerStats["season"], mpPlayerStats["I_F_xGoals"])
					player.update_gPERxg(mpPlayerStats["season"])
		try:
			cur = player.seasons[str(constant.CURRENT_SEASON)]
		except:
			allPlayers.remove(player)
			continue

		try:
			prev = player.seasons["20232024"]
		except:
			allPlayers.remove(player)
			continue

		ignoreCurYear = True

		#player.add_avg_gPERxg(ignoreCurYear)

		player.weigh_stat("shp", ignoreCurYear)

		'''
		try:
			player.pred_gPERgp_shp = ((prev["goals"]) * (player.AVGshp / prev["shp"])) / prev["gp"]
		except:
			allPlayers.remove(player)
			player.pred_gPERgp_shp = -1
			player.pred_gPERxg = -1
			player.avg_gPERgp = -1

		player.add_avg_gPERgp(ignoreCurYear)
		'''

def predictions_to_csv(players):
	print(f"{myself()}(players[{len(players)}])")

	predictionLines = []

	for player in players:
		temp = player.to_prediction_line()
		if(temp["gp"] > 40 and temp["goals"] > 13):
			predictionLines.append(temp)

	print(f"exporting: {len(predictionLines)} players...")
	#print(predictionLines)

	with open(f"../db/{constant.PREDICTION_FILE}", mode='w', newline='') as file:
		fieldnames = predictionLines[0].keys()
		writer = csv.DictWriter(file, fieldnames=fieldnames)

		writer.writeheader()

		for line in predictionLines:
			writer.writerow(line)
	

def shp_to_csv(players):
	predictionLines = []

	for player in players:
		temp = player.to_shp_data()
		if(temp["gp"] > 40 and temp["goals"] > 13):
			predictionLines.append(temp)

	#print(predictionLines)

	with open(f"../db/shp_pred.csv", mode='w', newline='') as file:
		fieldnames = predictionLines[0].keys()
		writer = csv.DictWriter(file, fieldnames=fieldnames)

		writer.writeheader()

		for line in predictionLines:
			writer.writerow(line)

def lines_to_json(lines):
	fp = open(f"../db/{constant.LINES_OBJECTS_FILE}", "w+")

	print(f"Writing to {constant.LINES_OBJECTS_FILE}")
	
	json.dump(lines, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=3, separators=None)

	with open(f"../db/{constant.LINES_EXPORT_FILE}", mode='w', newline='') as file:
		fieldnames = lines[0].keys()
		writer = csv.DictWriter(file, fieldnames=fieldnames)

		writer.writeheader()

		for line in lines:
			writer.writerow(line)
	
	fp.close()