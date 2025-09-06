import requests
import json
import constant
import inspect
import math
import csv

from classes import *

myself = lambda: inspect.stack()[1][3]

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

		nhlSeasons = {}
		for season in playerData["seasonTotals"]:
			if(season["leagueAbbrev"] == "NHL" and season["gameTypeId"] == 2):
				nhlSeasons[season["season"]] = {
													"gp" : season["gamesPlayed"],
													"goals" : season["goals"],
													"assists" : season["assists"],
													"points" : season["points"],
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
				"position" : playerData["position"]
				}
			)

	fp = open(f"../db/{constant.PLAYER_OBJECTS_FILE}", "w+")
	json.dump(allPlayerList, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=3, separators=None)
	fp.close()

def get_player_objects():
	fp = open(f"../db/{constant.PLAYER_OBJECTS_FILE}", "r")
	playerObjects = json.load(fp)

	allPlayers = []

	for player in playerObjects:
		#THIS IS WHERE FILTRATION HAPPENS
		if(len(player["seasons"]) >= 5):
			temp = Player()
			temp.construct_from_json(player)

			allPlayers.append(temp)

	return allPlayers

def get_target_stat_columns(targets):
	fp = open("../db/moneypuck/20202021_stats.csv")

	targetStatColumns = {}

	columns = fp.readline().split(',')
	for stat in targets:
		targetStatColumns[stat] = columns.index(stat)

	fp.close()

	return targetStatColumns

def add_xg(allPlayers):

	years = [
		"20202021",
		"20212022",
		"20222023",
		"20232024",
		"20242025"
	]

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

	for player in allPlayers:
		for year in focusedMpData:
			for mpPlayerStats in year:
				if(mpPlayerStats["playerId"] == str(player.id)):
					player.update_xg(mpPlayerStats["season"], mpPlayerStats["I_F_xGoals"])

def lines_to_json(lines):
	fp = open(f"../db/{constant.LINES_OBJECTS_FILE}", "w+")

	json.dump(lines, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=3, separators=None)

	print(lines[0])
	print(lines[1])
	print(lines[2])
	print(lines[3])
	print(lines[-1])

	with open(f"../db/{constant.LINES_EXPORT_FILE}", mode='w', newline='') as file:
		fieldnames = lines[0].keys()
		writer = csv.DictWriter(file, fieldnames=fieldnames)


		writer.writeheader()

		for line in lines:
			writer.writerow(line)
	
	fp.close()