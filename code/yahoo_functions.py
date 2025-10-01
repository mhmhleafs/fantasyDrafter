from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa

import json
import constant

from database import *

def yh_update_my_team(sc):
	#creates Game object (game refers to which sport, i.e. hockey)
	game = yfa.Game(sc, 'nhl')

	#gets all leagues I've done
	#leagues = game.league_ids()

	#creates League object out of kiki's wittle hockey weague
	lg = game.to_league('465.l.50290')

	team = lg.get_team(constant.YAHOO_TEAM_NAME)[constant.YAHOO_TEAM_NAME]

	roster = team.roster()

	allPlayerObjects = get_player_objects(age_included=18)

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

		myTeam.append(temp.toJson_withoutSeasons())

	#print the team
	for i in range(0, len(myTeam)):
		print(f"{i + 1} : {myTeam[i]["name"]}", end="\t")
		if(len(myTeam[i]["name"]) < 11):
			print("\t", end="")
		if(i % 3 == 2):
			print()
	print()

	numPlayers = len(myTeam)

	#prompt user to remove shitters
	#if IR spot used (more than 12 players) add an extra elimination
	while(numPlayers > 11):
		inp = int(input(f"Select player to eliminate[1-{numPlayers}]: "))

		while(inp not in range(1, numPlayers)):
			inp = int(input(f"Invalid Input. Select player to eliminate[1-{numPlayers}]: "))
		
		del myTeam[inp - 1]
		numPlayers = len(myTeam)

		for i in range(0, len(myTeam)):
			print(f"{i + 1} : {myTeam[i]["name"]}", end="\t")
			if(len(myTeam[i]["name"]) < 12):
				print("\t", end="")
			if(i % 3 == 2):
				print()
		print()



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
	}

	for player in fas[:]:
		if(player["name"] in nameMap):
			player["name"] = nameMap[player["name"]]
		print(player)



	print(len(fas))

	fp = open(f"../db/{constant.YAHOO_RAW}", "w+")
	json.dump(fas, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=3, separators=None)
	fp.close()

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