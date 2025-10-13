#use myTeam to set which players are "permanently" on my team (should myTeam be yahoo ids?)
#somehow figure out how to maximise gp with a set number of adds/drops, and prioritizing forwards
#perhaps output static total gp vs maximized total gp


#"source .venv/bin/activate" to engage virtual environment to use unidecode

import itertools
from database import *

#GAME WEEKS FILE CURRENTLY NERFED FOR TESTING
allGameWeeks = get_game_weeks()

myTeamJson = json_load(constant.MY_TEAM_FILE)

myTeam = {}

#create my team as a dict of player objects (key = id)
for player in myTeamJson:
	temp = Player()
	temp.construct_from_json(player)
	myTeam[temp.id] = temp


def maximize_spots(team, gameDay):
	availablePlayers = copy.deepcopy(team)

	gameDay.print_lineup()
	#remove players already slotted from availablePlayers
	for position in gameDay.dailyRoster:
		for player in gameDay.dailyRoster[position]:
			del availablePlayers[player.id]

	options = create_options(availablePlayers, gameDay)

	positionCombos = list(itertools.product(*options))
	
	optimalConfigs = []

	minOpenSlotCount = gameDay.open_slot_count()
	print(minOpenSlotCount)
	for configuration in positionCombos:
		#print(player_array_to_string(configuration))
		tempGd = copy.deepcopy(gameDay)
		for playerClone in configuration:
			posn = playerClone.positions[0]
			if(posn not in tempGd.open_positions()):
				if("Util" in tempGd.open_positions()):
					#print(f"slotting {playerClone.surname} at Util")
					tempGd.add_player('Util', playerClone)
				else:
					#print(f"too many cooks at {posn}, no Util available")
					tempGd.add_player('BN', playerClone)
			else:
				tempGd.add_player(posn, playerClone)
				#print(f"slotting {playerClone.surname} at {posn}")
			pass#print(playerClone)
		print(player_array_to_string(configuration))
		print(tempGd.open_slot_count())
		print(tempGd.open_slot_count() < minOpenSlotCount)
		if(tempGd.open_slot_count() < minOpenSlotCount):
			optimalConfigs.clear()
			minOpenSlotCount = tempGd.open_slot_count()
			optimalConfigs.append(copy.deepcopy(tempGd))
		elif(tempGd.open_slot_count() == minOpenSlotCount):
			optimalConfigs.append(copy.deepcopy(tempGd))
		print()

	return optimalConfigs



def create_options(players, gameDay):
	configs = []
	for player in players.values():
		clones = []
		for position in player.positions:
			playerCopy = copy.deepcopy(player)
			playerCopy.positions = [position]
			clones.append(playerCopy)
		configs.append(clones[:])
	return configs

def fork_optionsSAVE(players, gameDay):
	for player in players.values():
		for position in range(0, len(player.positions)):
			playersCopy = copy.deepcopy(players)

			#if no options remain
			if(not any((len(player.positions) > 1) for player in playersCopy.values())):
				print(player_dict_to_string(playersCopy))
				return playersCopy
			
			del playersCopy[player.id].positions[position]

			#if player is out of positions, gtfo
			if(len(playersCopy[player.id].positions) == 0):
				return
			
			fork_options(playersCopy, gameDay)
				

#for every week in the season
for gameWeek in allGameWeeks[0:1]:
	#for every day in the week
	for gameDay in gameWeek.gameDays[0:1]:
		teamSortedByPositionCOunt = sorted(myTeam.values(), key = lambda player: player.position_count())

		print("|-------------------MAXIMIZE TIME-------------------|")
		print()
		optimalConfigs = maximize_spots(myTeam, gameDay)
		for oc in optimalConfigs:
			print(oc)


#assign single posn players to positions
#assign multi posn players in permutations
#record which players have options
#create some kind of tree from that for duplicate optionals
#go over several times seeing if a player can be swapped

#can_swap function to open_position? that way I can guarantee multis work?
#permutations?
'''

wait actually i cant designate as droppers cause what if they
play on Monday, need to account for optimally keeping the streams from the previous week


so,  designate two players as "shitters" and then calculate openings from there?

'''