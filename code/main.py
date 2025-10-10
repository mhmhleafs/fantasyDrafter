from database import *

years = [
		"20222023",
		"20232024",
		"20242025"
	]

stats = {
	"I_F_faceOffsWon" : "faceoffWins",
	"shotsBlockedByPlayer" : "blocks",
	"I_F_hits" : "hits"
}

bangerLeague = True

#update_rosters()
#update_player_objects(years, stats)

#update_schedules()
#update_game_objects()
#update_mp_stats_map(years)

sc = OAuth2(None, None, from_file='oauth2.json')
#yh_update_players( DO NOT USE AFTER START OF SEASON
update_game_weeks(sc)
#yh_update_my_team(sc, years, ignoreCurrentYear=False, bangers=bangerLeague)
quit()

############################
# END OF DATABASE UPDATING #
############################

allPlayers = get_player_objects(len(years))

print(len(allPlayers))

#print(get_other_stats(8479318, "20242025", stats))

#print(get_target_stat_columns("20242025", ["I_F_faceOffsWon"]))

add_average_stats(allPlayers, years, ignoreCurrentYear=False, bangers=bangerLeague)
#print(allPlayers[0].to_prediction_line())
predictions_to_csv_points(allPlayers, bangerLeague)
