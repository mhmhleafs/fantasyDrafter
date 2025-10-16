from gameOptimizer import *#GAME WEEKS FILE CURRENTLY NERFED FOR TESTING
allGameWeeks = get_game_weeks()

myTeamJson = json_load(constant.MY_TEAM_FILE)

myTeam = {}

#create my team as a dict of player objects (key = id)
for player in myTeamJson:
	temp = Player()
	temp.construct_from_json(player)
	myTeam[temp.id] = temp

filledWeeks = fill_weeks(allGameWeeks, myTeam)

for week in filledWeeks:
	print(week)