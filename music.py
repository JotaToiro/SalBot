import nextcord as discord
from nextcord.ext import commands
from AuxMethods import AuxMethods
import datetime
import Constants
import yt_dlp as youtube_dl
import re
import urllib
import urllib.request
import requests
from DBAccess import DBAccess
from Buttons import queuePages, songInteractionsPlaying
import time
import GlobalMusicVariables as GMV

#ㅤcaracter bom NAO APAGAR
# import random
# from threading import Thread
# from memory_profiler import profile
# noinspection PyBroadException

class music(commands.Cog):

	def __init__(self):
		self.platformType = Constants.PlatformType
		self.auxMethods = AuxMethods()
		self.dbAccess = DBAccess()

	@commands.command(aliases=['s'])
	async def skip(self, ctx, option="1", index = None):  # skip para a proxima musica
		guildId = int(ctx.message.guild.id)
		self.auxMethods.generateLogString(str(datetime.datetime.now()),
										  str(ctx.message.author),
										  str(ctx.message.author.id),
										  str(ctx.message.guild),
										  str(ctx.message.guild.id),
										  str(ctx.message.content))

		voicC = ctx.voice_client

		if int(option) == 1:
			if len(GMV.guildMusicInfo[guildId].songsQueue) > 1:  # skip para a proxima musica
				voicC.stop()
				embedVar = discord.Embed(title=f"Skipped! <:skipicon:1006966592594260069>", color=0xe08a00)
				if GMV.guildMusicInfo[guildId].isStream:
					songName = GMV.guildMusicInfo[guildId].songsQueue[0]
					myStr = "ㅤㅤㅤㅤㅤㅤㅤㅤㅤ🔴  Streaming!"
					view = songInteractionsPlaying()
					view.children[2].disabled = True
				else:
					myStr, songName = self.auxMethods.generateProgressBarString(guildId)
					view = songInteractionsPlaying()
				if GMV.guildMusicInfo[guildId].isLoopActive:
					embedVar2 = discord.Embed(title="Playing now!  <:loopicon:1006005075652640811>", color=0xe08a00)
				else:
					embedVar2 = discord.Embed(title="Playing now!", color=0xe08a00)
				embedVar2.add_field(name=songName, value=myStr, inline=True)
				await ctx.send(embed=embedVar)
				await GMV.guildMusicInfo[guildId].timeLeftBar.delete()
				GMV.guildMusicInfo[guildId].timeLeftBar = await ctx.send(embed=embedVar2, view=view)
				view.message = GMV.guildMusicInfo[guildId].timeLeftBar
			else:
				if len(GMV.guildMusicInfo[guildId].songsQueue) == 0:  # nao faz nada porque nao ha nada a tocar
					embedVar = discord.Embed(title=f"There are no songs in queue or playing!", color=0xe08a00)
					await ctx.send(embed=embedVar)
					return
				voicC.stop()
				embedVar = discord.Embed(title=f"Skipped! <:skipicon:1006966592594260069>", color=0xe08a00)

				await ctx.send(embed=embedVar)
				await GMV.guildMusicInfo[guildId].timeLeftBar.delete()


		elif int(option) > 1:
			if len(GMV.guildMusicInfo[guildId].songsQueue) == int(option):
				voicC.stop()
				embedVar = discord.Embed(title=f"Skipped " + option + " songs! <:skipicon:1006966592594260069>", color=0xe08a00)
				await ctx.send(embed=embedVar)
				return
			if len(GMV.guildMusicInfo[guildId].songsQueue) < int(option):
				embedVar = discord.Embed(title=f"There are not that many songs in queue!", color=0xe08a00)
				await ctx.send(embed=embedVar)
				return
			for i in range(0, int(option) - 1):
				GMV.guildMusicInfo[guildId].songsQueue.pop(0)
			voicC.stop()

		if GMV.guildMusicInfo[guildId].songsQueue.type == Constants.QueuePositionType.STREAM:
			songName = GMV.guildMusicInfo[guildId].songsQueue[0]
			myStr = "ㅤㅤㅤㅤㅤㅤㅤㅤㅤ🔴  Streaming!"
			view = songInteractionsPlaying()
			view.children[2].disabled = True
		else:
			myStr, songName = self.auxMethods.generateProgressBarString(guildId)
			view = songInteractionsPlaying()
		if GMV.guildMusicInfo[guildId].isLoopActive:
			embedVar2 = discord.Embed(title="Playing now!  <:loopicon:1006005075652640811>", color=0xe08a00)
		else:
			embedVar2 = discord.Embed(title="Playing now!", color=0xe08a00)
		embedVar2.add_field(name=songName, value=myStr, inline=True)
		barReference = GMV.guildMusicInfo[guildId].timeLeftBar
		try:
			await barReference.delete()
		except:
			pass
		GMV.guildMusicInfo[guildId].timeLeftBar = await ctx.send(embed=embedVar2, view=view)
		view.message = GMV.guildMusicInfo[guildId].timeLeftBar



	@commands.command(aliases=['pr'])
	async def playrandom(self, ctx, *, url):
		guildId = int(ctx.message.guild.id)
		self.auxMethods.generateLogString(str(datetime.datetime.now()),
										  str(ctx.message.author),
										  str(ctx.message.author.id),
										  str(ctx.message.guild),
										  str(ctx.message.guild.id),
										  str(ctx.message.content))
		if ctx.author.voice is None:
			await ctx.send("`You are not in a voice channel!`")
			return
		"""CONNECTS TO VOICE CHANNEL IF USER IS IN A VOICE CHANNEL"""
		if url is None:
			embedVar = discord.Embed(description=f"Additional information needed:\n"
												 f"ex: >play (link)", color=0xe08a00)
			await ctx.send(embed=embedVar)
			return
		voice_channel = ctx.message.author.voice.channel
		if ctx.voice_client is None:
			await voice_channel.connect()
			GMV.resetMusicVariables(guildId)
			"""INITIALIZE ARRAYS IN DICTIONARY"""
		else:
			await ctx.voice_client.move_to(voice_channel)

		platformType = self.auxMethods.checkPlatformType(url)
		print(platformType)
		isQueued = False
		if platformType == self.platformType.SPOTIFY_PLAYLIST:
			isQueued = self.auxMethods.startPlaySpotifyPlaylist(guildId, url, ctx.voice_client, self, True)

		if isQueued:
			embedVar = discord.Embed(title=f"Added to queue", color=0xe08a00)
			await ctx.send(embed=embedVar)
			if GMV.guildMusicInfo[guildId].isStream:
				songName = GMV.guildMusicInfo[guildId].songsQueue[0].title
				myStr = "ㅤㅤㅤㅤㅤㅤㅤㅤㅤ**🔴  Streaming!**"
				view = songInteractionsPlaying()
				view.children[2].disabled = True
			else:
				myStr, songName = self.auxMethods.generateProgressBarString(guildId)
				view = songInteractionsPlaying()

			if GMV.guildMusicInfo[guildId].isLoopActive:
				embedVar = discord.Embed(title="Playing now!  <:loopicon:1006005075652640811>", color=0xe08a00)
			else:
				embedVar = discord.Embed(title="Playing now!", color=0xe08a00)
			embedVar.add_field(name=songName, value=myStr, inline=True)
			barReference = GMV.guildMusicInfo[guildId].timeLeftBar
			try:
				await barReference.delete()
			except:
				pass
			GMV.guildMusicInfo[guildId].timeLeftBar = await ctx.send(embed=embedVar, view=view)
			view.message = GMV.guildMusicInfo[guildId].timeLeftBar
		else:
			if GMV.guildMusicInfo[guildId].timeLeftBar is None:
				if GMV.guildMusicInfo[guildId].isStream:
					songName = GMV.guildMusicInfo[guildId].songsQueue[0].title
					myStr = "ㅤㅤㅤㅤㅤㅤㅤㅤㅤ🔴  **Streaming!**"
					view = songInteractionsPlaying()
					view.children[2].disabled = True
				else:
					myStr, songName = self.auxMethods.generateProgressBarString(guildId)
					view = songInteractionsPlaying()
				if GMV.guildMusicInfo[guildId].isLoopActive:
					embedVar = discord.Embed(title="Playing now!  <:loopicon:1006005075652640811>", color=0xe08a00)
				else:
					embedVar = discord.Embed(title="Playing now!", color=0xe08a00)
				embedVar.add_field(name=songName, value=myStr, inline=True)
				barReference = GMV.guildMusicInfo[guildId].timeLeftBar
				try:
					await barReference.delete()
				except:
					pass
				GMV.guildMusicInfo[guildId].timeLeftBar = await ctx.send(embed=embedVar, view=view)
				view.message = GMV.guildMusicInfo[guildId].timeLeftBar

	@commands.command(aliases=['p'])
	async def play(self, ctx, *, url=None):
		guildId = int(ctx.message.guild.id)
		userId = str(ctx.message.author.id)
		self.auxMethods.generateLogString(str(datetime.datetime.now()),
										  str(ctx.message.author),
										  str(ctx.message.author.id),
										  str(ctx.message.guild),
										  str(ctx.message.guild.id),
										  str(ctx.message.content))

		"""GETS DISCORD CHANNEL PERMISSIONS"""
		overwrite = ctx.message.author.voice.channel.overwrites_for(discord.utils.get(ctx.guild.roles, name="SalBot"))
		"""CHECKS DISCORD CHANNEL PERMISSIONS"""

		if ctx.author.voice is None:
			await ctx.send("`You are not in a voice channel!`")
			return
		"""CONNECTS TO VOICE CHANNEL IF USER IS IN A VOICE CHANNEL"""
		if url is None:
			embedVar = discord.Embed(description=f"Additional information needed:\n"
												 f"ex: >play (link)", color=0xe08a00)
			await ctx.send(embed=embedVar)
			return
		voice_channel = ctx.message.author.voice.channel
		if ctx.voice_client is None:
			await voice_channel.connect()
			GMV.resetMusicVariables(guildId)
			# --------------------------------
			"""INITIALIZE ARRAYS IN DICTIONARY"""

		else:
			await ctx.voice_client.move_to(voice_channel)

		"""CHECKS TYPE OF PLATFORM"""
		platformType = self.auxMethods.checkPlatformType(url)
		print(platformType)

		"""PLAYS THE SONG ACCORDINGLY AND WRITES ON DB"""
		isQueued = False

		if platformType == self.platformType.YOUTUBE:
			if "youtu.be/" in url:
				url = self.auxMethods.getLongUrlYoutube(url)
			isQueued, link, musicName = self.auxMethods.startPlayYoutubeSong(guildId, url, ctx.voice_client, self)
			self.auxMethods.writeOnDB(guildId, userId, musicName, link)

		elif platformType == self.platformType.SPOTIFY_TRACK:
			isQueued, link, musicName = self.auxMethods.startPlaySpotifyTrack(guildId, url, ctx.voice_client, self)
			self.auxMethods.writeOnDB(guildId, userId, musicName, link)

		elif platformType == self.platformType.SPOTIFY_PLAYLIST:
			isQueued = self.auxMethods.startPlaySpotifyPlaylist(guildId, url, ctx.voice_client, self, False)

		elif platformType == self.platformType.SPOTIFY_ALBUM:
			isQueued = self.auxMethods.startPlaySpotifyAlbum(guildId, url, ctx.voice_client, self)

		elif platformType == self.platformType.YOUTUBE_NO_LINK:
			isQueued, link, musicName = self.auxMethods.startPlayYoutubeSongNoUrl(guildId, url, ctx.voice_client, self)
			self.auxMethods.writeOnDB(guildId, userId, musicName, link)
			await ctx.send(link)

		elif platformType == self.platformType.YOUTUBE_PLAYLIST:
			isQueued = self.auxMethods.startPlayYoutubePlaylist(url, guildId, ctx.voice_client, self)

		elif platformType == self.platformType.YOUTUBE_MIX:
			return
			'''url = self.auxMethods.getLongUrlYoutube(url)
			isQueued = self.auxMethods.startPlayYoutubeMix(url, guildId, ctx.voice_client, self)'''
		if isQueued:
			embedVar = discord.Embed(title=f"Added to queue", color=0xe08a00)
			await ctx.send(embed=embedVar)
			if GMV.guildMusicInfo[guildId].isStream:
				songName = GMV.guildMusicInfo[guildId].songsQueue[0].title
				myStr = "ㅤㅤㅤㅤㅤㅤㅤㅤㅤ**🔴  Streaming!**"
				view = songInteractionsPlaying()
				view.children[2].disabled = True
			else:
				myStr, songName = self.auxMethods.generateProgressBarString(guildId)
				view = songInteractionsPlaying()

			if GMV.guildMusicInfo[guildId].isLoopActive:
				embedVar = discord.Embed(title="Playing now!  <:loopicon:1006005075652640811>", color=0xe08a00)
			else:
				embedVar = discord.Embed(title="Playing now!", color=0xe08a00)
			embedVar.add_field(name=songName, value=myStr, inline=True)
			barReference = GMV.guildMusicInfo[guildId].timeLeftBar
			try:
				await barReference.delete()
			except:
				pass
			GMV.guildMusicInfo[guildId].timeLeftBar = await ctx.send(embed=embedVar, view=view)
			view.message = GMV.guildMusicInfo[guildId].timeLeftBar
		else:
			if GMV.guildMusicInfo[guildId].isStream:
				songName = GMV.guildMusicInfo[guildId].songsQueue[0].title
				myStr = "ㅤㅤㅤㅤㅤㅤㅤㅤㅤ🔴  **Streaming!**"
				view = songInteractionsPlaying()
				view.children[2].disabled = True
			else:
				myStr, songName = self.auxMethods.generateProgressBarString(guildId)
				view = songInteractionsPlaying()
			if GMV.guildMusicInfo[guildId].isLoopActive:
				embedVar = discord.Embed(title="Playing now!  <:loopicon:1006005075652640811>", color=0xe08a00)
			else:
				embedVar = discord.Embed(title="Playing now!", color=0xe08a00)
			embedVar.add_field(name=songName, value=myStr, inline=True)
			barReference = GMV.guildMusicInfo[guildId].timeLeftBar
			try:
				await barReference.delete()
			except:
				pass
			GMV.guildMusicInfo[guildId].timeLeftBar = await ctx.send(embed=embedVar, view=view)
			view.message = GMV.guildMusicInfo[guildId].timeLeftBar

	@commands.command(aliases=['disc', 'dc'])
	async def disconnect(self, ctx):
		guildId = int(ctx.message.guild.id)
		self.auxMethods.generateLogString(str(datetime.datetime.now()),
										  str(ctx.message.author),
										  str(guildId),
										  str(ctx.message.guild),
										  str(guildId),
										  str(ctx.message.content))

		GMV.resetMusicVariables(guildId)

		ctx.voice_client.stop()
		await ctx.voice_client.disconnect()

	@commands.command(aliases=['q'])
	async def queue(self, ctx, option="all"):  # devolve as musicas em queue
		guildId = int(ctx.message.guild.id)
		self.auxMethods.generateLogString(str(datetime.datetime.now()),
										  str(ctx.message.author),
										  str(guildId),
										  str(ctx.message.guild),
										  str(guildId),
										  str(ctx.message.content))

		if option != "all" and option != "next":
			embedVar = discord.Embed(title=f"Invalid parameter!", color=0xe08a00)
			await ctx.send(embed=embedVar)
			return
		if ctx.message.guild.id in GMV.guildMusicInfo and len(GMV.guildMusicInfo[guildId].songsQueue) > 0:
			GMV.guildMusicInfo[guildId].currQueueMessagePage = 0
			if option == "next":  # devolve a proxima musica em queue

				musicName = GMV.guildMusicInfo[guildId].songsQueue[1].title
				embedVar = discord.Embed(title=f"Next song", description="- " + musicName, color=0xe08a00)
				await ctx.send(embed=embedVar)

			if option == "all":  # devolve todas as musicas em queue
				i = 0
				indexString = "**"
				songsString = ""
				changed = False

				for info in GMV.guildMusicInfo[guildId].songsQueue:
					songName = info.title
					while self.auxMethods.get_pil_text_size(songName, 12, "arial.ttf")[0] > 290:
						changed = True
						songName = songName[:-1]
					if changed:
						songName += "..."
						changed = False
					if i == 0:
						indexString += "Playing now" + "\n"
						if GMV.guildMusicInfo[guildId].songsQueue[i].type == Constants.QueuePositionType.PLAYLIST:
							songsString += "**(Playlist)**"
						if "youtube.com/watch?v=" in GMV.guildMusicInfo[guildId].songsQueue[i].reference:
							songsString += " " + "[" + songName + "]" + "(" + \
										   GMV.guildMusicInfo[guildId].songsQueue[i].reference + ")" + "\n"
						else:
							songsString += " " + songName + "\n"
					else:
						if i == 10:
							break
						indexString += str(i) + "\n"
						if GMV.guildMusicInfo[guildId].songsQueue[i].type == Constants.QueuePositionType.PLAYLIST:
							songsString += "**(Playlist)**"
						if "youtube.com/watch?v=" in GMV.guildMusicInfo[guildId].songsQueue[i].reference:
							songsString += " " + "[" + songName + "]" + "(" + \
										   GMV.guildMusicInfo[guildId].songsQueue[i].reference + ")" + "\n"
						else:
							songsString += " " + songName + "\n"

					i += 1
				totalPages, d = divmod((len(GMV.guildMusicInfo[guildId].songsQueue)) / 10, 1)
				indexString += "**"
				embedVar = discord.Embed(title=f"Next songs", description="", color=0xe08a00)
				embedVar.add_field(name="Queue position", value=indexString, inline=True)
				embedVar.add_field(name="Song", value=songsString, inline=True)
				embedVar.set_footer(text="page 1 of " + str(int(totalPages) + 1))
				view = queuePages()
				view.message = await ctx.send(embed=embedVar, view=view)

		else:
			embedVar = discord.Embed(title=f"There are no songs in queue", color=0xe08a00)
			await ctx.send(embed=embedVar)
		if GMV.guildMusicInfo[guildId].isStream:
			songName = GMV.guildMusicInfo[guildId].songsQueue[0].title
			myStr = "ㅤㅤㅤㅤㅤㅤㅤㅤㅤ🔴  Streaming!"
			view = songInteractionsPlaying()
			view.children[2].disabled = True
		else:
			myStr, songName = self.auxMethods.generateProgressBarString(guildId)
			view = songInteractionsPlaying()
		if GMV.guildMusicInfo[guildId].isLoopActive:
			embedVar2 = discord.Embed(title="Playing now!  <:loopicon:1006005075652640811>", color=0xe08a00)
		else:
			embedVar2 = discord.Embed(title="Playing now!", color=0xe08a00)
		embedVar2.add_field(name=songName, value=myStr, inline=True)
		try:
			await GMV.guildMusicInfo[guildId].timeLeftBar.delete()
		except:
			pass
		GMV.guildMusicInfo[guildId].timeLeftBar = await ctx.send(embed=embedVar2, view=view)
		view.message = GMV.guildMusicInfo[guildId].timeLeftBar

	@commands.command()
	async def top(self, ctx, isGlobal=None, userTag: discord.Member = None):
		guildId = int(ctx.message.guild.id)
		self.auxMethods.generateLogString(str(datetime.datetime.now()),
										  str(ctx.message.author),
										  str(guildId),
										  str(ctx.message.guild),
										  str(guildId),
										  str(ctx.message.content))
		if (isGlobal is None or isGlobal == "cur" or isGlobal == "global") and userTag == None:
			userId = ctx.author.id
			userId = str(userId)
			avatar = ctx.author.avatar
			userName = ctx.message.author
			userName = str(userName)[:-5]
		else:
			if isGlobal != "cur" and isGlobal != "global":
				embedVar = discord.Embed(title=f"Invalid arguments!", color=0xe08a00)
				await ctx.send(embed=embedVar)
				return
			else:
				userId = userTag.id
				userId = str(userId)
				avatar = userTag.avatar
				userName = str(userTag)[:-5]

		guildId = int(ctx.message.guild.id)
		result = ""
		globalOrLocal = ""
		myStrSongCount = ""
		if isGlobal is None or isGlobal == "cur":
			result = self.dbAccess.getSongsByGuildAndUserId(guildId, userId)
			globalOrLocal = ctx.guild.name
		if isGlobal == "global":
			result = self.dbAccess.getSongsByUserId(userId)
			globalOrLocal = "Global"
		top5 = []
		top5MusicCount = []
		top5MusicLink = []
		if len(result) > 0:
			if len(result) >= 5:
				max = 5
			else:
				max = len(result)
			for i in range(0, max):
				top5.append(result[i][0])
				top5MusicCount.append(str(result[i][1]))
				top5MusicLink.append(result[i][2])
			myStr = ""
			myStrSongCount = ""
			counter = 0
			for song in top5:
				if counter <= 2:
					length = 340
				else:
					length = 235
				musicStr = "" + Constants.NUMBERS[top5.index(song)] + " - " + '*' + "[" + song + "]"
				changed = False
				while self.auxMethods.get_pil_text_size(musicStr[4:], 12, "arial.ttf")[0] > length:
					changed = True
					musicStr = musicStr[:-1]
				if changed:
					musicStr += "...]"
				musicStr += "(" + top5MusicLink[top5.index(song)] + ")" + '*'
				myStr += musicStr + '\n'
				myStrSongCount += "ㅤ" + top5MusicCount[top5.index(song)] + "\n"
				counter += 1
		else:
			myStr = "ㅤ*Nothing to show!*"
		if userName[-1] == 's' or userName[-1] == 'S':
			endString = "'"
		else:
			endString = "'s"
		if len(result) > 0:
			embedVar = discord.Embed(title=userName + endString + " top 5  \n", description=globalOrLocal,
									 color=0xe08a00)
			embedVar.add_field(name="Song", value=myStr, inline=True)
			embedVar.add_field(name="ㅤTimes played", value=myStrSongCount, inline=True)
		else:
			embedVar = discord.Embed(title=userName + endString + " top 5  \n", description=myStr,
									 color=0xe08a00)
		embedVar.set_thumbnail(url=avatar)
		await ctx.send(embed=embedVar)

	@commands.command(aliases=['servert', 'servt', 'st'])
	async def servertop(self, ctx):
		guildId = int(ctx.message.guild.id)
		self.auxMethods.generateLogString(str(datetime.datetime.now()),
										  str(ctx.message.author),
										  str(guildId),
										  str(ctx.message.guild),
										  str(guildId),
										  str(ctx.message.content))
		guildName = ctx.guild.name
		finalResult = self.dbAccess.getSongsByGuildId(guildId)

		finalResult.sort(key=lambda x: x[1], reverse=True)
		myStr = ""
		avatar = ctx.guild.icon
		if len(finalResult) == 0:
			embedVar = discord.Embed(title=guildName + " top 10  \n", color=0xe08a00)
			embedVar.set_thumbnail(url=avatar)
			await ctx.send(embed=embedVar)
		else:
			top10 = []
			top10MusicCount = []
			top10MusicLink = []
			if len(finalResult) >= 10:
				max = 10
			else:
				max = len(finalResult)
			for i in range(0, max):
				top10.append(finalResult[i][0])
				top10MusicCount.append(str(finalResult[i][1]))
				top10MusicLink.append(finalResult[i][2])

			myStrSongCount = ""
			counter = 0
			for song in top10:
				musicStr = "" + Constants.NUMBERS[top10.index(song)] + " - " + '*' + "[" + song + "]"
				changed = False
				if counter <= 2:
					length = 340
				else:
					length = 235
				while self.auxMethods.get_pil_text_size(musicStr[4:], 12, "arial.ttf")[0] > length:
					changed = True
					musicStr = musicStr[:-1]
				if changed:
					musicStr += "...]"
				musicStr += "(" + top10MusicLink[top10.index(song)] + ")" + '*'
				myStr += musicStr + '\n'
				myStrSongCount += "ㅤ" + top10MusicCount[top10.index(song)] + "\n"
				counter += 1
			if len(finalResult) > 0:
				embedVar = discord.Embed(title=guildName + " top 10  \n",
										 color=0xe08a00)
				embedVar.add_field(name="Song", value=myStr, inline=True)
				embedVar.add_field(name="ㅤTimes played", value=myStrSongCount, inline=True)
			else:
				embedVar = discord.Embed(title=guildName + " top 10  \n", description="ㅤ*Nothing to show!*",
										 color=0xe08a00)
			if avatar is not None:
				embedVar.set_thumbnail(url=avatar)

			await ctx.send(embed=embedVar)

	@commands.command()
	async def pause(self, ctx):
		guildId = int(ctx.message.guild.id)
		self.auxMethods.generateLogString(str(datetime.datetime.now()),
										  str(ctx.message.author),
										  str(guildId),
										  str(ctx.message.guild),
										  str(guildId),
										  str(ctx.message.content))

		vc = ctx.voice_client
		vc.pause()
		GMV.guildMusicInfo[guildId].isPaused = True
		GMV.guildMusicInfo[guildId].currentSongTimeLeft = GMV.guildMusicInfo[guildId].endOfTheSongTime - int(
			time.time())
		embedVar = discord.Embed(title=f"Paused  ⏸", color=0xe08a00)
		await ctx.send(embed=embedVar)

	@commands.command()
	async def resume(self, ctx):
		guildId = int(ctx.message.guild.id)
		self.auxMethods.generateLogString(str(datetime.datetime.now()),
										  str(ctx.message.author),
										  str(guildId),
										  str(ctx.message.guild),
										  str(guildId),
										  str(ctx.message.content))

		vc = ctx.voice_client
		vc.resume()
		GMV.guildMusicInfo[guildId].isPaused = False
		GMV.guildMusicInfo[guildId].endOfTheSongTime = int(time.time()) + GMV.guildMusicInfo[
			guildId].currentSongTimeLeft
		embedVar = discord.Embed(title=f"Resumed  ▶", color=0xe08a00)
		await ctx.send(embed=embedVar)

	@commands.command(aliases=['l'])
	async def loop(self, ctx):
		guildId = int(ctx.message.guild.id)
		self.auxMethods.generateLogString(str(datetime.datetime.now()),
										  str(ctx.message.author),
										  str(guildId),
										  str(ctx.message.guild),
										  str(guildId),
										  str(ctx.message.content))

		if not GMV.guildMusicInfo[guildId].isLoopActive:
			GMV.guildMusicInfo[guildId].isLoopActive = True
			embedVar = discord.Embed(title=f" Loop enabled  🔁", color=0xe08a00)
			await ctx.send(embed=embedVar)
		else:
			GMV.guildMusicInfo[guildId].isLoopActive = False
			embedVar = discord.Embed(title=f" Loop disabled  🔁", color=0xe08a00)
			await ctx.send(embed=embedVar)

	@commands.command(aliases=['t'])
	async def time(self, ctx):
		guildId = int(ctx.message.guild.id)

		self.auxMethods.generateLogString(str(datetime.datetime.now()),
										  str(ctx.message.author),
										  str(guildId),
										  str(ctx.message.guild),
										  str(guildId),
										  str(ctx.message.content))

		if not GMV.guildMusicInfo[guildId].isPlaying:
			embedVar = discord.Embed(title=f"Nothing is playing!", color=0xe08a00)
			await ctx.send(embed=embedVar)
			return

		if GMV.guildMusicInfo[guildId].isStream:
			songName = GMV.guildMusicInfo[guildId].songsQueue[0].title
			myStr = "ㅤㅤㅤㅤㅤㅤㅤㅤㅤ**🔴  Streaming!**"
			view = songInteractionsPlaying()
			view.children[2].disabled = True
		else:
			myStr, songName = self.auxMethods.generateProgressBarString(guildId)
			view = songInteractionsPlaying()
		if GMV.guildMusicInfo[guildId].isLoopActive:
			embedVar = discord.Embed(title="Playing now!  <:loopicon:1006005075652640811>", color=0xe08a00)
		else:
			embedVar = discord.Embed(title="Playing now!", color=0xe08a00)

		embedVar.add_field(name=songName, value=myStr, inline=True)
		barReference = GMV.guildMusicInfo[guildId].timeLeftBar
		try:
			await barReference.delete()
		except:
			pass
		GMV.guildMusicInfo[guildId].timeLeftBar = await ctx.send(embed=embedVar, view=view)
		view.message = GMV.guildMusicInfo[guildId].timeLeftBar

	@commands.command(aliases=['r'])
	async def remove(self, ctx, *, index):
		guildId = int(ctx.message.guild.id)
		self.auxMethods.generateLogString(str(datetime.datetime.now()),
										  str(ctx.message.author),
										  str(guildId),
										  str(ctx.message.guild),
										  str(guildId),
										  str(ctx.message.content))

		if index == "all":
			if len(GMV.guildMusicInfo[guildId].songsQueue) > 1:
				auxList = GMV.guildMusicInfo[guildId].songsQueue[0]
				GMV.guildMusicInfo[guildId].songsQueue.clear()
				GMV.guildMusicInfo[guildId].songsQueue.append(auxList)
				embedVar = discord.Embed(title=f" All songs removed from the queue  ❌", color=0xe08a00)
				await ctx.send(embed=embedVar)
		else:
			removedString = ""
			if " " in index:
				if index[-1] == " ":
					index = index[:-1]
				indexes = index.split(" ")
				for i in indexes:
					if not str(i).isnumeric():
						embedVar = discord.Embed(title=f"Invalid parameter!", color=0xe08a00)
						await ctx.send(embed=embedVar)
						return

				if len(indexes) > len(GMV.guildMusicInfo[guildId].songsQueue) - 1:
					embedVar = discord.Embed(title=f"Too many indexes!", color=0xe08a00)
					await ctx.send(embed=embedVar)
					return
				else:
					indexes = [int(x) for x in indexes]
					if max(indexes) > len(GMV.guildMusicInfo[guildId].songsQueue) - 1:
						embedVar = discord.Embed(title=f"Invalid index!", color=0xe08a00)
						await ctx.send(embed=embedVar)
						return
					if not self.auxMethods.checkRepeatedNumbers(indexes):
						embedVar = discord.Embed(title=f"Invalid combination of indexes!", color=0xe08a00)
						await ctx.send(embed=embedVar)
						return
					indexes = sorted(indexes, reverse=False)
					for i in indexes:
						if i > len(GMV.guildMusicInfo[guildId].songsQueue) - 1:
							embedVar = discord.Embed(title=f"Invalid song index!", color=0xe08a00)
							await ctx.send(embed=embedVar)
							return
					for i in indexes:
						musicName = GMV.guildMusicInfo[guildId].songsQueue[int(i)].title
						removedString += musicName + "\n"
					count = 0
					for i in indexes:
						GMV.guildMusicInfo[guildId].songsQueue.pop(i - count)
						count += 1
					print(removedString)
					embedVar = discord.Embed(title=f"Songs removed from the queue  ❌ ", description=removedString,
											 color=0xe08a00)
					await ctx.send(embed=embedVar)
					return

			if int(index) < 0 or int(index) > len(GMV.guildMusicInfo[guildId].songsQueue) - 1:
				embedVar = discord.Embed(title=f"Invalid song index!", color=0xe08a00)
				await ctx.send(embed=embedVar)
				return


			else:
				if not str(index).isnumeric():
					embedVar = discord.Embed(title=f"Invalid parameter!", color=0xe08a00)
					await ctx.send(embed=embedVar)
					return

				if int(index) == 0:
					embedVar = discord.Embed(title=f"Can't remove the song currently playing!", color=0xe08a00)
					await ctx.send(embed=embedVar)
					return

				removedMusic = GMV.guildMusicInfo[guildId].songsQueue[int(index)].title
				GMV.guildMusicInfo[guildId].songsQueue.pop(int(index))
				embedVar = discord.Embed(title=f" Song removed from the queue  ❌", description=removedMusic,
										 color=0xe08a00)
				await ctx.send(embed=embedVar)

	@commands.command()
	async def reorder(self, ctx, *, order):
		guildId = int(ctx.message.guild.id)
		self.auxMethods.generateLogString(str(datetime.datetime.now()),
										  str(ctx.message.author),
										  str(guildId),
										  str(ctx.message.guild),
										  str(guildId),
										  str(ctx.message.content))

		newOrder = order.split(" ")
		for i in newOrder:
			if not str(i).isnumeric():
				embedVar = discord.Embed(title=f"Invalid parameter!", color=0xe08a00)
				await ctx.send(embed=embedVar)
				return
		newOrder = [int(x) for x in newOrder]
		if len(GMV.guildMusicInfo[guildId].songsQueue) <= 2:
			embedVar = discord.Embed(title="Not enough songs to reorder!", color=0xe08a00)
			await ctx.send(embed=embedVar)
			return
		if max(newOrder) > len(GMV.guildMusicInfo[guildId].songsQueue) - 1:
			embedVar = discord.Embed(title=f"Invalid index!", color=0xe08a00)
			await ctx.send(embed=embedVar)
			return
		if not self.auxMethods.checkRepeatedNumbers(newOrder):
			embedVar = discord.Embed(title=f"Invalid combination of indexes!", color=0xe08a00)
			await ctx.send(embed=embedVar)
			return
		if len(newOrder) != len(GMV.guildMusicInfo[guildId].songsQueue) - 1 and len(newOrder) != 2:
			embedVar = discord.Embed(title="Invalid number of songs to reorder!", color=0xe08a00)
			await ctx.send(embed=embedVar)
			return
		for i in newOrder:
			if i == 0:
				embedVar = discord.Embed(title="You cant reorder the song that is currently playing!", color=0xe08a00)
				await ctx.send(embed=embedVar)
				return

		newOrder = [0] + newOrder
		auxQueue = []
		auxQueueTitle = []

		if len(newOrder) == 3:
			varAux = GMV.guildMusicInfo[guildId].songsQueue[newOrder[1]]
			GMV.guildMusicInfo[guildId].songsQueue[newOrder[1]] = \
				GMV.guildMusicInfo[guildId].songsQueue[newOrder[2]]
			GMV.guildMusicInfo[guildId].songsQueue[newOrder[2]] = varAux
		else:
			for i in range(0, len(GMV.guildMusicInfo[guildId].songsQueue)):
				auxQueue.append(GMV.guildMusicInfo[guildId].songsQueue[newOrder[i]])
			GMV.guildMusicInfo[guildId].songsQueue = auxQueue[:]

		auxVector = ""
		i = 0

		embedVar = discord.Embed(title=f"Reordered  🔀", description="", color=0xe08a00)
		await ctx.send(embed=embedVar)

	def playMusic(self, vc, url, id):
		id = int(id)
		urlArray = url.split("?t=")
		if len(urlArray) > 1:
			timestamp = self.auxMethods.convertToTime(int(urlArray[1]))
			timeInSecs = int(urlArray[1])
		else:
			timestamp = "0:0:0"
			timeInSecs = 0
		FFMPEG_OPTIONS = {
			'before_options': '-reconnect 1 -reconnect_streamed 1 ' '-reconnect_delay_max 5 ' f'-ss {timestamp}',
			'options': '-vn'}

		with youtube_dl.YoutubeDL(Constants.YDL_OPTIONS_VIDEO) as ydl:
			try:
				info = ydl.extract_info(url, download=False)
				url2 = info['url']
				try:
					response = requests.get(
						url2,
						timeout=0.1)
					while int(response.status_code) == 403:
						time.sleep(0.1)
						response = requests.get(
							url2,
							timeout=0.1)
						info = ydl.extract_info(url, download=False)
						url2 = info['url']
				except:
					pass

				infoMusic = [vc, id]
				source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
				vc.play(source, after=lambda e: self.checkForQueue(infoMusic))
				isStream = self.auxMethods.checkIsStream(url2)
				if not isStream:
					duration = int(info['duration'])
					timeToEnd = int(time.time()) + duration
					timeLeft = duration - timeInSecs
				else:
					duration = None
					timeToEnd = None
					timeLeft = None

				GMV.setMusicVariables(id,
									  True,
									  self.auxMethods.checkIsStream(url2),
									  duration,
									  GMV.guildMusicInfo[id].isLoopActive,
									  timeLeft,
									  False,
									  timeToEnd,
									  int(time.time()))

				del info
			except:
				pass

	def checkForQueue(self, infoMusic):
		guildId = infoMusic[1]
		vc = infoMusic[0]
		GMV.guildMusicInfo[guildId].currentSongTimeLeft = 0
		if not GMV.guildMusicInfo[guildId].isLoopActive:
			if len(GMV.guildMusicInfo[guildId].songsQueue) == 0:
				return
			GMV.guildMusicInfo[guildId].songsQueue.pop(0)
		if len(GMV.guildMusicInfo[guildId].songsQueue) > 0:
			nextSongToPlay = GMV.guildMusicInfo[guildId].songsQueue[0].reference

			if "youtube.com/watch?v=" in nextSongToPlay or "youtu.be/" in nextSongToPlay:
				GMV.guildMusicInfo[guildId].isPlaying = False
				self.playMusic(vc, nextSongToPlay, guildId)
			else:
				html = urllib.request.urlopen(
					"https://www.youtube.com/results?search_query=" + nextSongToPlay)
				videos_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
				url = "https://www.youtube.com/watch?v=" + videos_ids[0]
				self.playMusic(vc, url, guildId)
			return
		else:
			GMV.guildMusicInfo[guildId].isPlaying = False
			return


def setup(client):
	client.add_cog(music())
