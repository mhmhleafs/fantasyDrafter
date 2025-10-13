import json
import constant
from helpers import *

class Player:
	def __init__(self, id=None, name=None, surname=None, seasonsPlayed=None, seasons=[], age=None, team=None, position=None):
		self.id = id
		self.name = name
		self.surname = surname
		self.seasonsPlayed = seasonsPlayed
		self.seasons = seasons
		self.age = age
		self.team = team

	def construct_from_json(self, playerJson):
		for attr in playerJson.keys():
			setattr(self, attr, playerJson[attr])

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
		return self.__dict__

	def toJson_withoutSeasons(self):
		retDict = self.__dict__
		del retDict["seasons"]

		return retDict

	def toStr_withoutSeasons(self):
		retString = (
		f"[{self.id}] {self.name}:\n")

		for key, value in self.__dict__.items():
			if(key not in ["id", "name", "seasons"]):
				retString += f"\t{key}: {value}\n"

		return retString

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
			setattr(self, f"AVG_{stat}", totalStat / totalGP)
		except:
			#print(self)
			#print("ERR_WEIGH_STAT")
			setattr(self, f"AVG_{stat}", None)

	#print shp and xg predicted goals (from before 20242025) and then the 20242025 stats as well, to compare methods
	def to_prediction_line(self):

		posnString = ""
		for posn in self.positions:
			posnString += posn.replace("W", "")
			
		retDict = {	"id"	:	self.id,
			 		"age"	:	self.age,
					"team"	:	self.team,
					"positions"	:	posnString,
					"name"	:	self.name,
					"surname"	:	self.surname
			 }
		
		for key in self.__dict__.keys():
			if("AVG" in key):
				retDict[key] = getattr(self, key)

		retDict = retDict | self.seasons[str(constant.CURRENT_SEASON)] #merge
		
		return retDict
	
	def position_count(self):
		return len(self.positions)


class Game:
	def __init__(self, id=None, date=None, teams=None):
		self.id = id
		self.date = date
		self.teams = teams

	def construct_from_json(self, gameJson):
		for attr in gameJson.keys():
			setattr(self, attr, gameJson[attr])

	def __str__(self):
		retString = (f"[{self.id}]: {self.date} : {self.teams[0]} @ {self.teams[1]}")

		return retString
	
	def __json__(self):
		return self.__dict__

#gameDays contains GameDay objects
class GameWeek:
	def __init__(self, week=-1):
		self.week = week
		self.gameDays = []

	def construct_from_json(self, gameWeekJson):
		for attr in gameWeekJson.keys():
			if(attr == "gameDays"):
				for day in gameWeekJson[attr]:
					tempGD = GameDay(day["date"], day["teamsPlaying"], day["positionMax"])
					self.gameDays.append(tempGD)
			else:
				setattr(self, attr, gameWeekJson[attr])

		#print(self)
	
	def __str__(self):
		retString = f"{self.week} : "
		for day in self.gameDays:
			retString += day.__str__()
		return retString
	
	def __json__(self):
		return self.__dict__
	
	#does this even get used?
	def add_day(self):
		self.gameDays.append([])

	def add_games(self, gameDay):
		self.gameDays.append(gameDay)


class GameDay:
	def __init__(self, date, teamsPlaying, posnMax=None):
		self.date = date
		self.teamsPlaying = teamsPlaying
		self.dailyRoster = {
			'C' : [],
			'RW' : [],
			'LW' : [],
			'D' : [],
			'Util' : [],
			'BN' : []
		}
		self.positionMax = posnMax
		self.options = []

	def __json__(self):
		return self.__dict__
	
	def __str__(self):
		retString = f"{self.date}: {self.teamsPlaying} "

		retString += "["
		for slot in self.dailyRoster:
			for player in self.dailyRoster[slot]:
				retString += f"{slot} : {player.surname}\t"
		retString += "]"

		return retString
	
	def construct_from_json(self, gameWeekJson):
		for attr in gameWeekJson.keys():
			setattr(self, attr, gameWeekJson[attr])

	def add_player(self, position, player):
		if(position not in self.open_positions() and position != "BN"):
			#return
			print(f"illegal addition: {player.surname} at {position}")
		else:
			self.dailyRoster[position].append(player)

	def get_position(self, position):
		return self.dailyRoster[position]
	
	def max_posn(self, position):
		return self.positionMax[position]
	
	def open_positions(self):
		openSlots = {}
		for posn in self.dailyRoster:
			if(posn != "BN" and len(self.dailyRoster[posn]) < self.positionMax[posn]):
				#print(f"slot open at {posn}")
				openSlots[posn] = self.positionMax[posn] - len(self.dailyRoster[posn])
		return openSlots
	
	def open_slot_count(self):
		total = 0
		for posn in self.open_positions().values():
			print(self.open_positions())
			total += posn

		return total
	
	
	def full_positions(self):
		fullSlots = {}
		for posn in self.dailyRoster:
			if(posn != "BN" and len(self.dailyRoster[posn]) == self.positionMax[posn]):
				#print(f"slot open at {posn}")
				fullSlots[posn] = self.positionMax[posn] - len(self.dailyRoster[posn])
		return fullSlots
	
	def remaining_players(self, team):
		playerPool = set(team.values())
		for posn in self.dailyRoster.values():
			for player in posn:
				playerPool.discard(player)
		return playerPool
	
	#needs to return a GameDay object
	def current_lineup(self):
		return self.dailyRoster
	
	def print_lineup(self):
		retLines = {
				'F' : "",
				'D' : "",
				'X' : "",
				'B' : "",
			}

		for posn in self.dailyRoster:
			for player in self.dailyRoster[posn]:
				line = "B"
				if(posn in ['RW', 'LW', 'C']):
					line = 'F'
				elif(posn in ['D']):
					line = 'D'
				elif(posn in ['Util', 'F']):
					line = 'X'
				else:
					line = 'B'
				retLines[line] += f"{posn}: {player.surname}\t"

		for line in retLines.values():
			print(line)