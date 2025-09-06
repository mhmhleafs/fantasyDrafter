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
		f"[{self.id}] {self.name}\n"
		f"--surname : {self.surname}\n"
		f"--seasonsPlayed : {self.seasonsPlayed}\n"
		f"--position : {self.position}\n"
		f"--age : {self.age}\n")

		for season in self.seasons:
			retString += f"--{season} : {self.seasons[season]}\n"

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
	
	def update_xg(self, season, xg):
		try:
			self.seasons[season]["xg"] = xg
		except:
			return
			

	def get_last_x_seasons(self, seasonCount):
		ret = []

		for season in range(constant.CURRENT_SEASON, constant.CURRENT_SEASON - (10001 * seasonCount), -10001):
			try:
				tempSeason = self.seasons[str(season)]
				tempSeason["season"] = season
				tempSeason["id"] = self.id
				tempSeason["name"] = self.name
				ret.append(tempSeason)
			except:
				#ends loop if target out of range of seasons played
				break
		
		return ret

	def export_as_lines(self, count):
		lines = []

		for season in self.get_last_x_seasons(count):
			lines.append(season)

		return lines