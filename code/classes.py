import json
import constant

class Player:
	def __init__(self, id=None, name=None, surname=None, seasonsPlayed=None, seasons=[], age=None, team=None, position=None):
		self.id = id
		self.name = name
		self.surname = surname
		self.seasonsPlayed = seasonsPlayed
		self.seasons = seasons
		self.age = age
		self.team = team
		self.position = position

	def construct_from_json(self, playerJson):
		self.id = playerJson["id"]
		self.name = playerJson["name"]
		self.surname = playerJson["surname"]
		self.seasonsPlayed = playerJson["seasonsPlayed"]
		self.seasons = playerJson["seasons"]
		self.age = playerJson["age"]
		self.team = playerJson["team"]
		self.position = playerJson["position"]

	def __str__(self):
		retString = (
		f"[{self.id}] {self.name}:\n")

		for key, value in self.__dict__.items():
			if(key not in ["id", "name", "seasons"]):
				retString += f"\t{key}: {value}\n"

		retString += "\tSeasons:\n"
		for season in self.seasons:
			retString += f"\t\t{season} : {self.seasons[season]}\n"

		return retString
	
	def __json__(self):
			return {
				"id" : self.id,
				"name" : self.name,
				"surname" : self.surname,
				"seasonsPlayed" : self.seasonsPlayed,
				"seasons" : self.seasons,
				"age" : self.age,
				"team" : self.team,
				"position" : self.position
			}			

	def get_last_x_seasons(self, seasonCount):
		ret = []

		for season in range(constant.CURRENT_SEASON, constant.CURRENT_SEASON - (10001 * seasonCount), -10001):
			try:
				tempSeason = {}
				
				tempSeason["id"] = self.id
				tempSeason["season"] = season
				tempSeason["name"] = self.name
				tempSeason.update(self.seasons[str(season)])

				ret.append(tempSeason)
			except:
				#ends loop if target out of range of seasons played
				continue
		
		return ret

	def export_as_lines(self, count):
		lines = []

		for season in self.get_last_x_seasons(count):
			lines.append(season)

		return lines

	def weigh_stat(self, stat, years, excludeCurrentYear=False):
		totalGP = 0
		totalStat = 0.0
		for season in self.seasons:
			if(excludeCurrentYear and season == "20242025"):
				continue
			if(season in years): #if recent enough season
				curSeason = self.seasons[season]
				totalGP += curSeason['gp']
				totalStat += curSeason['gp'] * curSeason[stat]

		try:
			setattr(self, f"AVG{stat}", totalStat / totalGP)
		except:
			print(self)
			quit()

	#print shp and xg predicted goals (from before 20242025) and then the 20242025 stats as well, to compare methods
	def to_prediction_line(self):
		retDict = {	"id"	:	self.id,
					"position"	:	self.position,
					"name"	:	self.name,
					"surname"	:	self.surname,
					"AVGshp"	:	self.AVGshp
			 }
		retDict = retDict | self.seasons[str(constant.CURRENT_SEASON)] #merge
		
		return retDict
	