#use myTeam to set which players are "permanently" on my team (should myTeam be yahoo ids?)
#somehow figure out how to maximise gp with a set number of adds/drops, and prioritizing forwards
#perhaps output static total gp vs maximized total gp


#"source .venv/bin/activate" to engage virtual environment to use unidecode

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


def maximize_spots(team, gameDay, recursionString=""):
	availablePlayers = copy.copy(team)
	gDay = copy.copy(gameDay)

	gDay.print_lineup()
	#remove players already slotted from availablePlayers
	for position in gDay.dailyRoster:
		for player in gDay.dailyRoster[position]:
			del availablePlayers[player.id]
			#print(position, player.surname)
	for ap in availablePlayers.values():
		print(ap.surname, end=" ")
	print(recursionString)


#for every week in the season
for gameWeek in allGameWeeks[0:1]:
	#for every day in the week
	for gameDay in gameWeek.gameDays[0:1]:
		teamSortedByPositionCOunt = sorted(myTeam.values(), key = lambda player: player.position_count())
		#print(gameDay)
		#one position
		#for every player in my team
		for player in myTeam.values():
			#if player plays that day
			if(player.team in gameDay.teamsPlaying):
				#if they're a one trick nancy
				if(player.position_count() == 1):
					posn = player.positions[0]
					if(posn not in gameDay.open_positions()):
						if("Util" in gameDay.open_positions()):
							#print(f"too many cooks at {posn}")
							gameDay.add_player('Util', player)
						else:
							#print(f"too many cooks at {posn}, no Util available")
							gameDay.add_player('BN', player)
					else:
						gameDay.add_player(posn, player)
						print(f"slotting {player.surname} at {posn}")
		'''
		for player in myTeam.values():
			#if player plays that day
			if(player.team in gameDay.teamsPlaying):
				#if they're a two trick pony (check for pigeonhole)
				if(player.position_count() == 2):
					#if one of the player's positions is already filled
					if(lists_share_element(player.positions, gameDay.full_positions())):
						#they're now a one trick pony so slot them
						for posn in player.positions:
							if(posn in gameDay.open_positions()):
								print(f"{player.surname} must play {posn}")
								gameDay.add_player(posn, player)
		'''
					

		#print(gameDay.positionMax)
		#print('\t', gameDay.current_lineup())
		#print('\t', gameDay)
		gdcopy = copy.copy(gameDay)
		print("|-------------------MAXIMIZE TIME-------------------|")
		print()
		maximize_spots(myTeam, gdcopy)


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