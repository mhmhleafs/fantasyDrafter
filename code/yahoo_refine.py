import json
import constant
from unidecode import unidecode

fp = open(f"../db/{constant.YAHOO_RAW}", "r")
playerData = json.load(fp)
fp.close()

fp2 = open(f"../db/{constant.PLAYER_OBJECTS_FILE}", "r")
playerObjects = json.load(fp2)
fp2.close()

for player in playerObjects:
	if(not (any(unidecode(player["name"]) in pdata["name"] for pdata in playerData))):
		print(player["name"])

print()
for player in playerData:
	if(player["player_id"] == 7534):
		print(player["name"])