#use myTeam to set which players are "permanently" on my team (should myTeam be yahoo ids?)
#somehow figure out how to maximise gp with a set number of adds/drops, and prioritizing forwards
#perhaps output static total gp vs maximized total gp


#"source .venv/bin/activate" to engage virtual environment to use unidecode

import itertools
from database import *


def maximize_spots(team, gameDay):
	availablePlayers = copy.deepcopy(team)

	gameDay.print_lineup()

	bench = set()

	for player in team.values():
		#if the player has no game on the day
		if(not playing_on_day(player, gameDay)):
			print(f"no game for {player.surname}")
			bench.add(copy.deepcopy(player))
			del availablePlayers[player.id]
	optimalConfigs = []

	minOpenSlotCount = gameDay.open_slot_count()
	print(player_set_to_string(bench))


	options = create_options(availablePlayers)
	#print(availablePlayers)
	positionCombos = list(itertools.product(*options))


	#for every permutation of every (playing) player at every possible position
	for configuration in positionCombos:

		tempGd = copy.deepcopy(gameDay)

		tempGd.dailyRoster["BN"].extend(bench)

		#for each playerSlice in the current configuration
		for playerClone in configuration:

			#posn sets from the player's only position
			posn = playerClone.positions[0]

			#if their posn is filled
			if(posn not in tempGd.open_positions()):
				#they go util if possible
				if("Util" in tempGd.open_positions()):
					tempGd.add_player('Util', playerClone)

				#else, they're benched
				else:
					tempGd.add_player('BN', playerClone)
			#if their posn is available, add them to that spot
			else:
				tempGd.add_player(posn, playerClone)
				
		#if the current amount of openslots is lower than the previous low
		if(tempGd.open_slot_count() < minOpenSlotCount):
			#reset the optimal configs and sets the new low
			optimalConfigs.clear()
			minOpenSlotCount = tempGd.open_slot_count()

			#add config
			optimalConfigs.append(tempGd)

		#if equal to min open spots, add config
		elif(tempGd.open_slot_count() == minOpenSlotCount):
			#print(tempGd.open_slot_count())
			optimalConfigs.append(tempGd)

		#if bad config, ignore
		else:
			pass#print(tempGd.open_slot_count())
	
	return optimalConfigs



def create_options(players):
	configs = []
	for player in players.values():
		clones = []
		for position in player.positions:
			playerCopy = copy.deepcopy(player)
			playerCopy.positions = [position]
			clones.append(playerCopy)
		configs.append(clones[:])
	return configs
				

def fill_weeks(allGameWeeks, myTeam):
	bestLineups = []

	#for every week in the season
	for gameWeek in allGameWeeks[0:1]:
		#for every day in the week
		for gameDay in gameWeek.gameDays[0:1]:
			print("|-------------------MAXIMIZE TIME-------------------|")
			print()
			optimalConfigs = maximize_spots(myTeam, gameDay)

		#get all possible open positions?

		for cfg in optimalConfigs:
			if("Util" in cfg.open_positions()):
				#print(cfg.open_positions())
				bestLineups.append(cfg)
			#print(len(cfg.open_positions()))
	return bestLineups

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