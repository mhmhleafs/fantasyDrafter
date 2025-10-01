from database import *
from yahoo_functions import *

#update_rosters()
#update_player_objects()

#update_schedules()
#update_game_objects()

#sc = OAuth2(None, None, from_file='oauth2.json')
#yh_update_players( DO NOT USE AFTER START OF SEASON

years = [
		"20222023",
		"20232024",
		"20242025"
	]

allPlayers = get_player_objects(len(years))

print(len(allPlayers))

allPlayers = get_player_objects(len(years))

add_stats(allPlayers, years, ignoreCurrentYear=False)
predictions_to_csv(allPlayers)

#lines_to_json(allLines)
