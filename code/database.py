import requests
import json
import constant
import inspect
import math
import csv
import copy

import datetime
import weekdates
import constant
import json
from unidecode import unidecode

from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa

from helpers import *
from classes import *

def update_schedules():
	print(f"{myself()}: Updating schedules...")

	masterSchedule = []

	for teamCode in constant.TEAM_CODES:
		req = f"https://api-web.nhle.com/v1/club-schedule-season/{teamCode}/20252026"
		resp = requests.get(req)

		if(resp.status_code != 200):
			print(f"{myself()}: Response for {req} not OK, terminating with code {resp.status_code}...")
			exit()
		else:
			print(f"updating {teamCode}...")

		jason = json.loads(resp.text)

		jason["teamCode"] = teamCode

		masterSchedule.append(jason)
	
	print(f"Writing to {constant.RAW_SCHEDULE_FILE}...")

	json_dump(constant.RAW_SCHEDULE_FILE, masterSchedule)

def update_game_objects():
	scheduleJson = json_load(constant.RAW_SCHEDULE_FILE)

	allGameObjects = {}

	for team in scheduleJson:
		for game in team["games"]:
			if(game["gameType"] == 2):
				temp = Game(
					game["id"],
					game["gameDate"],
					[game["awayTeam"]["abbrev"],game["homeTeam"]["abbrev"]]
				)
				allGameObjects[game["id"]] = temp.__json__()
				#break

	json_dump(constant.SCHEDULE_FILE, allGameObjects)

def get_game_objects():
	scheduleJson = json_load(constant.SCHEDULE_FILE)

	gameObjects = []

	for game in scheduleJson:
		temp = Game()
		temp.construct_from_json(scheduleJson[game])
		gameObjects.append(temp)

	return gameObjects

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

	json_dump(constant.ROSTER_FILE, masterTeamRosters)

	print('Process finished.')

def update_player_objects(years, stats):
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

		#remove accents
		fullName = unidecode(f"{playerData["firstName"]["default"]} {playerData["lastName"]["default"]}")

		positions = get_yahoo_position(fullName)

		if(positions == -1):
			continue
		
		if("Util" in positions):
			positions.remove("Util")
		if("IR+" in positions):
			positions.remove("IR+")

		yahooId = get_yahoo_id(fullName)

		nhlSeasons = {}
		for season in playerData["seasonTotals"]:
			#This 'if' block catches the fact that players traded midseason have multiple entries for the same season
			if(season["leagueAbbrev"] == "NHL" and season["gameTypeId"] == 2 and (season["season"] in nhlSeasons.keys()) and str(season["season"]) in years):
				#print(nhlSeasons[season["season"]])
				
				#don't need to add mp stats since they're season totals
				tempSeason = {
									"gp" : season["gamesPlayed"],
									"goals" : season["goals"],
									"assists" : season["assists"],
									"points" : season["points"],
									"fanPts" : 3 * season["goals"] + 2 * season["assists"],
									"shp" : season["shootingPctg"],
									"PPP" : season["powerPlayPoints"],
									"shots" : season["shots"]
								}
				for key in tempSeason.keys():
					nhlSeasons[season["season"]][key] += tempSeason[key]

			elif(season["leagueAbbrev"] == "NHL" and season["gameTypeId"] == 2):
				nhlSeasons[season["season"]] = {
													"gp" : season["gamesPlayed"],
													"goals" : season["goals"],
													"assists" : season["assists"],
													"points" : season["points"],
													"fanPts" : 3 * season["goals"] + 2 * season["assists"],
													"shp" : season["shootingPctg"],
													"PPP" : season["powerPlayPoints"],
													"shots" : season["shots"]
												}
				#add all other stats to season (hits, blocks, foW)
				if(str(season["season"]) in years):
					otherStats = get_other_stats(playerID, str(season["season"]), stats)
					for stat in otherStats:
						nhlSeasons[season["season"]][stats[stat]] = otherStats[stat]

		allPlayerList.append(
				{
				"id" : playerData["playerId"],
				"name" : fullName,
				"surname" : unidecode(playerData["lastName"]["default"]),
				"seasonsPlayed" : len(nhlSeasons),
				"seasons" : nhlSeasons,
				"age" : 2025 - int((playerData["birthDate"]).split('-')[0]),
				"team" : playerData["currentTeamAbbrev"],
				"positions" : positions,
				"yahooId" :yahooId
				}
			)

	json_dump(constant.PLAYER_OBJECTS_FILE, allPlayerList)

def get_player_objects(minSeasons=-1, age_included = -1):
	print(f"{myself()}(minSeasons={minSeasons})")
	playerObjects = json_load(constant.PLAYER_OBJECTS_FILE)

	allPlayers = []

	for player in playerObjects:
		#FILTRATION FOR DATABASE HAPPENS HERE
		if(len(player["seasons"]) >= minSeasons):
			temp = Player()
			temp.construct_from_json(player)

			if(age_included > 0):
				if(("20242025" in temp.seasons or "20232024" in temp.seasons) or temp.age >= age_included):
					allPlayers.append(temp)
			elif("20242025" in temp.seasons and "20232024" in temp.seasons):
				allPlayers.append(temp)

	return allPlayers

def predictions_to_csv_points(players, bangers):
	print(f"{myself()}(players[{len(players)}])")

	predictionLines = []

	for player in players:
		temp = player.to_prediction_line()

		#FILTRATION ON EXPORT HAPPENS HERE
		if(temp["gp"] > 35):
			predictionLines.append(temp)

	print(f"exporting: {len(predictionLines)} players...")
	#print(predictionLines)

	if(bangers):
		filepath = f"../db/BANGERS_{constant.PREDICTION_FILE}"
	else:
		filepath = f"../db/{constant.PREDICTION_FILE}"

	with open(filepath, mode='w', newline='') as file:
		fieldnames = predictionLines[0].keys()
		writer = csv.DictWriter(file, fieldnames=fieldnames)

		writer.writeheader()

		for line in predictionLines:
			writer.writerow(line)


#for debugging I guess
def lines_to_json(lines):
	fp = open(f"../db/{constant.LINES_OBJECTS_FILE}", "w+")

	print(f"Writing to {constant.LINES_OBJECTS_FILE}")
	
	json_dump(lines, fp)
	
	with open(f"../db/{constant.LINES_EXPORT_FILE}", mode='w', newline='') as file:
		fieldnames = lines[0].keys()
		writer = csv.DictWriter(file, fieldnames=fieldnames)

		writer.writeheader()

		for line in lines:
			writer.writerow(line)
	
	fp.close()

def update_game_weeks(sc):
	masterSchedule = json_load(constant.SCHEDULE_FILE)

	all_weeks = weekdates.ALL_WEEKS

	date_format = "%b %d %Y"

	time_delta = datetime.timedelta(days=1)

	#availablePositions = yh_get_available_positions(sc)

	sc = OAuth2(None, None, from_file='oauth2.json')
	positionMaximums = yh_get_available_positions(sc)

	gameWeeks = []

	#for each week
	for i in range(1,constant.REG_SZN_WEEKS + 1):
		tempWeek = GameWeek(i)

		start_time = datetime.datetime.strptime(all_weeks[i]["Start"], date_format).date()
		end_time = datetime.datetime.strptime(all_weeks[i]["End"], date_format).date()

		currentDate = start_time

		#for each day in the week:
		while (currentDate <= end_time):
			#create a new day of games
			tempTeamsPlaying = []

			#for each game
			for game in masterSchedule.values():
				#if the game is on the current date
				if(game["date"] == str(currentDate)):
					#add it to today's games
					tempTeamsPlaying += game["teams"]
			
			#create GameDay object
			tempGameDay = GameDay(str(currentDate), tempTeamsPlaying, positionMaximums)
			
			#add all games on current date to 
			tempWeek.add_games(tempGameDay.__json__())
			currentDate += time_delta

		gameWeeks.append(tempWeek.__json__())
		#print(tempWeek.__json__())

	json_dump(constant.GAME_WEEKS_FILE, gameWeeks)

def get_game_weeks():
	gameWeeksJson = json_load(constant.GAME_WEEKS_FILE)

	gameObjects = []

	for week in gameWeeksJson:
		tempWeek = GameWeek()
		tempWeek.construct_from_json(week)

		gameObjects.append(tempWeek)

	return gameObjects



def yh_update_my_team(sc, years, ignoreCurrentYear, bangers):
	#creates Game object (game refers to which sport, i.e. hockey)
	game = yfa.Game(sc, 'nhl')

	#gets all leagues I've done
	#leagues = game.league_ids()

	#creates League object out of kiki's wittle hockey weague
	lg = game.to_league('465.l.50290')

	team = lg.get_team(constant.YAHOO_TEAM_NAME)[constant.YAHOO_TEAM_NAME]

	roster = team.roster()

	allPlayerObjects = get_player_objects(age_included=18)

	add_average_stats(allPlayerObjects, years, ignoreCurrentYear=False, bangers=bangers)

	myTeam = []

	for player in roster:
		#don't care about goalies
		if("G" in player["eligible_positions"]):
			continue
		
		if("IR+" in player["selected_position"]):
			continue

		temp = get_by_property(allPlayerObjects, "yahooId", player["player_id"])

		if(not temp):
			print(f"COULD NOT FIND: {player["name"]}")

		myTeam.append(temp.__json__())

	#print the team
	for i in range(0, len(myTeam)):
		print(f"{i + 1} : {myTeam[i]["name"]}", end="")
		print((21 - (len(myTeam[i]["name"])) - len(str(i + 1))) * " ", end="")
		if(i % 3 == 2):
			print()
	print()

	numPlayers = len(myTeam)

	#prompt user to remove shitters
	#if IR spot used (more than 12 players) add an extra elimination
	'''
	while(numPlayers > 11):
		inp = int(input(f"Select player to eliminate[1-{numPlayers}]: "))

		while(inp not in range(1, numPlayers + 1)):
			inp = int(input(f"Invalid Input. Select player to eliminate[1-{numPlayers}]: "))
		
		del myTeam[inp - 1]
		numPlayers = len(myTeam)

		for i in range(0, len(myTeam)):
			print(f"{i + 1} : {myTeam[i]["name"]}", end="")
			print((21 - (len(myTeam[i]["name"])) - len(str(i + 1))) * " ", end="")
			if(i % 3 == 2):
				print()
		print()
	'''


	fp = open(f"../db/{constant.MY_TEAM_FILE}", "w+")
	json.dump(myTeam, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=3, separators=None)
	fp.close()

#updates yahoo raw with all Free Agents
'''

ONLY USE BEFORE SEASON

'''
def yh_update_players(sc):
	sc = OAuth2(None, None, from_file='oauth2.json')

	game = yfa.Game(sc, 'nhl')

	leagues = game.league_ids()
	print(leagues)
	lg = game.to_league('465.l.50290')
	fas = lg.free_agents('CDRWLWG')


	nameMap = {
		"Joshua Norris" : "Josh Norris",
		"Christopher Tanev" : "Chris Tanev",
		"Zachary Bolduc" : "Zack Bolduc",
		"Anthony DeAngelo" : "Tony DeAngelo",
		"Zach Aston-Reese" : "Zachary Aston-Reese",
	}

	for player in fas[:]:
		if(player["name"] in nameMap):
			player["name"] = nameMap[player["name"]]
		print(player)



	print(len(fas))

	fp = open(f"../db/{constant.YAHOO_RAW}", "w+")
	json.dump(fas, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=3, separators=None)
	fp.close()