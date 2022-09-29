import Constants
from mysql import connector

"""DATA BASE ACCESS METHODS"""

class DBAccess:

	def __init__(self):
		pass

	def getSongsByGuildId(self, guildId):
		try:
			mydb = connector.connect(
				   host=Constants.HOST,
				   user=Constants.USER,
				   password=Constants.PASSWORD,
				   database=Constants.DATABASE
			)
			curs = mydb.cursor(prepared=True)
		except:
			mydb.close()
			return
		try:
			curs.execute("SELECT MUSIC, MUSIC_COUNT, MUSIC_LINK, USER_ID FROM PROFILES WHERE GUILD_ID = ?", (guildId,))
			result = curs.fetchall()
		except:
			mydb.close()
			return

		finalResult = []
		for value in result:
			finalResult.append(value)
			lst = list(finalResult[finalResult.index(value)])
			for value2 in result:

				if value == value2:
					continue
				if value[2] == value2[2]:
					lst[1] += value2[1]
					result.pop(result.index(value2))
			finalResult[finalResult.index(value)] = lst

		finalResult.sort(key=lambda x: x[1], reverse=True)
		return finalResult

	def getSongsByGuildAndUserId(self, guildId, userId):
		try:
			mydb = connector.connect(
				host=Constants.HOST,
				user=Constants.USER,
				password=Constants.PASSWORD,
				database=Constants.DATABASE
			)
			curs = mydb.cursor(prepared=True)
		except:
			mydb.close()
			return
		try:
			curs.execute("SELECT MUSIC, MUSIC_COUNT, MUSIC_LINK FROM PROFILES WHERE USER_ID = ? and GUILD_ID = ? ORDER BY MUSIC_COUNT DESC",
			(userId, guildId))
			result = curs.fetchall()
		except:
			mydb.close()
			return

		return result

	def getSongsByUserId(self, userId):
		try:
			mydb = connector.connect(
				host=Constants.HOST,
				user=Constants.USER,
				password=Constants.PASSWORD,
				database=Constants.DATABASE
			)
			curs = mydb.cursor(prepared=True)
		except:
			mydb.close()
			return
		try:
			curs.execute("SELECT MUSIC, MUSIC_COUNT, MUSIC_LINK FROM PROFILES WHERE USER_ID = ? ORDER BY MUSIC_COUNT DESC",(userId,))
			result = curs.fetchall()
			mydb.close
		except:
			mydb.close()
			return

		return result

	def insertNewLine(self, userId, musicName, guildId, url):
		try:
			mydb = connector.connect(
				host=Constants.HOST,
				user=Constants.USER,
				password=Constants.PASSWORD,
				database=Constants.DATABASE
			)
			curs = mydb.cursor(prepared=True)
		except:
			mydb.close()
			return
		try:
			musicName = musicName.replace("[", "(")
			musicName = musicName.replace("]", ")")
			curs.execute(
				"INSERT INTO PROFILES(USER_ID, MUSIC, MUSIC_COUNT, GUILD_ID, MUSIC_LINK) VALUES (%s, %s, %s, %s, %s)",
				(userId, musicName, 1, guildId, url))
			curs.execute("COMMIT;")
			mydb.close()
		except:
			mydb.close()


	def selectCountOfAMusic(self, musicName, userId, guildId):
		try:
			mydb = connector.connect(
				host=Constants.HOST,
				user=Constants.USER,
				password=Constants.PASSWORD,
				database=Constants.DATABASE
			)

			curs = mydb.cursor(prepared=True)
			curs.execute("SELECT MUSIC_COUNT FROM PROFILES WHERE MUSIC = ? and USER_ID = ? and GUILD_ID = ?",
			             (musicName, userId, guildId))

			result = curs.fetchone()
			result = result[0]
			mydb.close()
		except:
			mydb.close()
			return

		return result

	def selectIdOfCertainLine(self, musicName, userId, guildId):
		try:
			mydb = connector.connect(
				host=Constants.HOST,
				user=Constants.USER,
				password=Constants.PASSWORD,
				database=Constants.DATABASE
			)

			curs = mydb.cursor(prepared=True)
		except:
			mydb.close()
			return
		try:
			curs.execute("SELECT ID FROM PROFILES WHERE MUSIC=? and USER_ID=? and GUILD_ID=?",
			             (musicName, userId, guildId))
			ID = curs.fetchone()
			curs.execute("SELECT MUSIC_COUNT FROM PROFILES WHERE ID=?", ID)
			ID = ID[0]
			mydb.close()
		except:
			mydb.close()
			return
		return ID

	def updateLineMusicCount(self, musicCount, ID):
		try:
			mydb = connector.connect(
				host=Constants.HOST,
				user=Constants.USER,
				password=Constants.PASSWORD,
				database=Constants.DATABASE
			)
			curs = mydb.cursor(prepared=True)
		except:
			mydb.close()
			return

		try:
			curs.execute("UPDATE PROFILES SET MUSIC_COUNT = ? WHERE ID = ?", (musicCount, ID))
			curs.execute("COMMIT;")
			mydb.close()
		except:
			mydb.close()