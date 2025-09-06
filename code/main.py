from database import *

#update_rosters()
#update_player_objects()
allPlayers = get_player_objects()

add_xg(allPlayers)

allLines = []

for player in allPlayers:
	lines = player.export_as_lines(20)
	for line in lines:
		allLines.append(line)

lines_to_json(allLines)

#matthews = 8479318