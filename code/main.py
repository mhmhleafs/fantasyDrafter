from database import *

#update_rosters()
#update_player_objects()

years = [
		"20222023",
		"20232024",
		"20242025"
	]

allPlayers = get_player_objects(len(years))

add_stats(allPlayers, years, ignoreCurrentYear=False)
#add_xg(allPlayers, years)

predictions_to_csv(allPlayers)

#lines_to_json(allLines)

#matthews = 8479318

#TODO: calculate and spit out weighted xg/gp as export
#use 20242025 as benchmark to determine if that or shp regression is better predictor
