from Constants import PlatformType
import math
from PIL import ImageFont
from DBAccess import DBAccess
import GlobalMusicVariables as GMV
import time
import urllib
import Constants
import yt_dlp as youtube_dl
import unidecode
import re
from pytube import Playlist
from APIs import SpotifyAPI
import requests
import random

class AuxMethods:

	def __init__(self):
		self.dbAccess = DBAccess()
		self.Spotify = SpotifyAPI.SpotifyAPI()

	def generateLogString(self, dateTimeStr, author, authorId, guild, guildId, commandMessage):
		description = dateTimeStr + " - " + author + " with id: " + authorId + " in the server " + guild + " with id: " + guildId + " sent the command: " + commandMessage + "\n"
		self.writeLogs(description, int(guildId))

	def writeLogs(self, description, guildId):
		logFile = open("_logs.txt", "a")
		logFile.write(description)
		guildLogFile = open(f"logs/{guildId}.txt", "a")
		guildLogFile.write(description)
		return

	def checkIsStream(self, url2):
		return True if "manifest.googlevideo.com" in url2 else False

	# https://www.youtube.com/watch?v=73V0sYxyOCw&list=RD73V0sYxyOCw
	# https://youtu.be/73V0sYxyOCw?list=RD73V0sYxyOCw

	def checkPlatformType(self, url):
		if "youtu.be/" in url:
			url = self.getLongUrlYoutube(url)
		if "youtube.com/watch?v=" in url and not "&list=" in url and not "?list=" in url:
			return PlatformType.YOUTUBE
		elif "https://open.spotify.com/track/" in url:
			return PlatformType.SPOTIFY_TRACK
		elif "https://open.spotify.com/playlist/" in url:
			return PlatformType.SPOTIFY_PLAYLIST
		elif "https://open.spotify.com/album/" in url:
			return PlatformType.SPOTIFY_ALBUM
		elif "youtube.com/watch?v=" in url and ("&list=" in url or "?list=" in url) and self.getLinkIdLengthYoutube(url) == 34:
			return PlatformType.YOUTUBE_PLAYLIST
		elif "youtube.com/watch?v=" in url and ("&list=" in url or "?list=" in url):
			return PlatformType.YOUTUBE_MIX
		else:
			return PlatformType.YOUTUBE_NO_LINK

	def getLongUrlYoutube(self, url):
		site = requests.get(url)
		final = site.url.replace("&feature=youtu.be", "")
		return final

	'''def getLongUrlHardCode(self, url):
		if "www.youtu.be" in url:
			url.replace("www.youtu.be", "www.youtube.com")
			id = url.split("www.youtu.be/")[1]
		else:
			url.replace("youtu.be", "www.youtube.com")
			id = url.split("youtu.be/")[1]

		newUrl = f"https://www.youtube.com/watch?v={id}"

		return  newUrl'''



	# https://www.youtube.com/watch?v=73V0sYxyOCw
	# https://youtu.be/73V0sYxyOCw

	def getLinkIdLengthYoutube(self, url):
		if "&list=" in url:
			arrayString = url.split("&list=")
		else:
			arrayString = url.split("?list=")
		arrayString2 = arrayString[1]
		if "&index=" in url or "&start_radio" in url:
			if "&index=" in arrayString2:
				final = arrayString2.split("&index=")
			else:
				final = arrayString2.split("&start_radio")
			id = final[0]
		else:
			if "&list=" in url:
				final = url.split("&list=")
			else:
				final = url.split("?list=")
			id = final[1]
		return len(id)

	def convertToTime(self, seconds):
		timeLeftStr = ""
		timeLeft = seconds
		if timeLeft < 60:
			if timeLeft < 10:
				timeLeftStr = "0:0" + str(timeLeft)
			else:
				timeLeftStr = "0:" + str(timeLeft)
		if 3600 > timeLeft >= 60:
			seconds, minuts = math.modf(timeLeft / 60)
			minuts = str(int(minuts))
			seconds = int(seconds * 60)
			if seconds < 10:
				seconds = "0" + str(seconds)
			else:
				seconds = str(seconds)
			timeLeftStr = minuts + ":" + seconds
		if timeLeft >= 3600:
			minuts, hours = math.modf(timeLeft / 60 / 60)
			minuts = int(minuts * 60)
			hours = str(int(hours))
			if minuts < 10:
				minuts = "0" + str(minuts)
			else:
				minuts = str(minuts)
			timeLeftStr = hours + ":" + minuts + " h"
		return timeLeftStr

	def get_pil_text_size(self ,text, font_size, font_name):
		font = ImageFont.truetype(font_name, font_size)
		size = font.getsize(text)
		return size

	def writeOnDB(self, guildId, userId, musicName, musicLink):
		musicCount = self.dbAccess.selectCountOfAMusic(musicName, userId, guildId)
		if musicCount is None:
			musicCount = 0
		if musicCount > 0:
			id = self.dbAccess.selectIdOfCertainLine(musicName, userId, guildId)
			self.dbAccess.updateLineMusicCount(musicCount + 1, id)
		else:
			self.dbAccess.insertNewLine(userId, musicName, guildId, musicLink)



	def checkRepeatedNumbers(self, list):
		sortedList = sorted(list, reverse=False)
		lastValue = None
		for i in sortedList:
			if i == lastValue:
				return False
			lastValue = i
		return True


	def getLinkFromMessage(self, message, index):
		lines = message.split("\n")
		linesFinal = []
		for line in lines:
			linesFinal.append("")
			for i in range(len(line), 0, -1):
				if line[i - 1] == "(":
					linesFinal[lines.index(line)] = linesFinal[lines.index(line)][2:]
					linesFinal[lines.index(line)] = self.reverseString(linesFinal[lines.index(line)])
					break
				else:
					linesFinal[lines.index(line)] += line[i - 1]
		return linesFinal[index]

	def reverseString(self, string):
		stringAux = string
		string = ""

		for i in range(len(stringAux), 0, -1):
			string += stringAux[i - 1]
		return string

	def generateProgressBarString(self, guildId):
		duration = GMV.guildMusicInfo[guildId].durationOfCurrentSong
		timeLeft = GMV.guildMusicInfo[guildId].endOfTheSongTime - int(time.time())
		currentTime = duration - timeLeft
		durationStr = self.convertToTime(duration)
		currentTimeStr = self.convertToTime(currentTime)
		myStr = f"᲼**` " + currentTimeStr + " `**᲼"
		percentage = int(currentTime) / duration
		myStr += "`"
		for i in range(45):
			if i / 45 < percentage:
				myStr += "█"
			else:
				myStr += "᲼"
		myStr += "`"
		myStr += "᲼**` " + durationStr + " `**᲼"
		if GMV.guildMusicInfo[guildId].songsQueue[0].type == Constants.QueuePositionType.SONG:
			songName = GMV.guildMusicInfo[guildId].songsQueue[0].title
		else:
			keys_list = list(GMV.guildMusicInfo[guildId].playlistsQueue)
			songName = GMV.guildMusicInfo[guildId].playlistsQueue[keys_list[0]][0].title
		return myStr, songName


	def startPlayYoutubeSong(self, guildId, url, voiceClient, instance):
		with youtube_dl.YoutubeDL(Constants.YDL_OPTIONS_INFO) as ydl:
			info = ydl.extract_info(url, download=False)
			musicName = info['title']
		GMV.guildMusicInfo[guildId].songsQueue.append(GMV.SongInfo(url, musicName, Constants.QueuePositionType.SONG))
		if not GMV.guildMusicInfo[guildId].isPlaying:
			GMV.resetMusicVariables(guildId, False)
			instance.playMusic(voiceClient, url, guildId)
			return False, url, musicName
		else:
			return True, url, musicName

	def startPlayYoutubeSongNoUrl(self, guildId, string, voiceClient, instance):
		newString = string.replace(" ", "+")
		newString = newString.replace("&", "and")
		newUrl = unidecode.unidecode(newString)
		html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + newUrl)
		videos_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
		i = 0
		url = "https://www.youtube.com/watch?v=" + videos_ids[i]
		while "list" in url:
			i += 1
			url = "https://www.youtube.com/watch?v=" + videos_ids[i]
		with youtube_dl.YoutubeDL(Constants.YDL_OPTIONS_INFO) as ydl:
			info = ydl.extract_info(url, download=False)
			musicName = info['title']
		GMV.guildMusicInfo[guildId].songsQueue.append(GMV.SongInfo(url, musicName, Constants.QueuePositionType.SONG))
		if not GMV.guildMusicInfo[guildId].isPlaying:
			GMV.resetMusicVariables(guildId, False)
			instance.playMusic(voiceClient, url, guildId)
			return False, url, musicName
		else:
			return True, url, musicName

	def startPlaySpotifyTrack(self, guildId, url, voiceClient, instance):
		trackId = self.Spotify.extract_track_id(url, "track")
		songName, artist = self.Spotify.getTrackNameAndArtist(trackId)
		SongNameOriginal = f"{songName} - {artist}"
		songName = songName.replace(" ", "+")
		songName = songName.replace("&", "and")
		artist = artist.replace(" ", "+")
		artist = artist.replace("&", "and")
		youtubeSearchString = artist + "+" + songName + "+" + "song"
		youtubeSearchString = unidecode.unidecode(youtubeSearchString)
		html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + youtubeSearchString)
		videos_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

		url = "https://www.youtube.com/watch?v=" + videos_ids[0]

		GMV.guildMusicInfo[guildId].songsQueue.append(GMV.SongInfo(url, SongNameOriginal, Constants.QueuePositionType.SONG))

		if not GMV.guildMusicInfo[guildId].isPlaying:
			GMV.resetMusicVariables(guildId, False)
			instance.playMusic(voiceClient, url, guildId)
			return False, url, SongNameOriginal
		else:
			return True, url, SongNameOriginal

	def startPlaySpotifyPlaylist(self, guildId, url, voiceClient, instance, isShuffled: bool):
		isQueueEmpty = len(GMV.guildMusicInfo[guildId].songsQueue) == 0
		listId = self.Spotify.extract_track_id(url, "playlist")
		songsList = self.Spotify.getPlayListSongs(listId, "playlists")
		if isShuffled:
			random.shuffle(songsList)
		GMV.addToQueueAllPlaylistSongs(songsList, guildId)
		if not GMV.guildMusicInfo[guildId].isPlaying and isQueueEmpty:
			youtubeSearchString = GMV.guildMusicInfo[guildId].songsQueue[0].reference
			html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + youtubeSearchString)
			videos_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
			url = "https://www.youtube.com/watch?v=" + videos_ids[0]
			GMV.resetMusicVariables(guildId, False)
			instance.playMusic(voiceClient, url, guildId)
			return False
		else:
			return True


	def startPlaySpotifyAlbum(self, guildId, url, voiceClient, instance):
		isQueueEmpty = len(GMV.linksQueue[guildId]) == 0
		listId = self.Spotify.extract_track_id(url, "album")
		songsList = self.Spotify.getPlayListSongs(listId, "albums")
		GMV.addToQueueAllPlaylistSongs(songsList, guildId)
		if not GMV.guildMusicInfo[guildId].isPlaying and isQueueEmpty:
			youtubeSearchString = GMV.guildMusicInfo[guildId].songsQueue[0].reference
			html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + youtubeSearchString)
			videos_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
			url = "https://www.youtube.com/watch?v=" + videos_ids[0]
			GMV.resetMusicVariables(guildId, False)
			instance.playMusic(voiceClient, url, guildId)

			return False
		else:
			return True


	def startPlayYoutubePlaylist(self, url, guildId, voiceClient, instance):
		play_list = Playlist(url)
		title = "Youtube playlist"
		isQueueEmpty = len(GMV.guildMusicInfo[guildId].songsQueue) == 0
		GMV.addToQueueAllYoutubePlaylistSongs(play_list, guildId, playlistName=title)
		if not GMV.guildMusicInfo[guildId].isPlaying and isQueueEmpty:
			GMV.resetMusicVariables(guildId, False)
			instance.playMusic(voiceClient, url, guildId)
			return False
		else:
			return True

	def startPlayYoutubeMix(self, url, guildId, voiceClient, instance):
		isQueueEmpty = len(GMV.linksQueue[guildId]) == 0
		with youtube_dl.YoutubeDL(Constants.YDL_OPTIONS_MIX) as ydl:
			info = ydl.extract_info(url, download=False)
			firstUrl = info['entries'][0]['url']
		GMV.addToQueueAllYoutubeMixSongs(info, guildId)

		if not GMV.guildMusicInfo[guildId].isPlaying and isQueueEmpty:
			GMV.resetMusicVariables(guildId)
			instance.playMusic(voiceClient, firstUrl, guildId)
			return False
		else:
			return True







