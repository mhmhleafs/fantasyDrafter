from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa

import json
import constant

sc = OAuth2(None, None, from_file='oauth2.json')

#have to run in cmd for some reason

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