import unidecode
from dataclasses import dataclass
import Constants

"""GLOBAL MUSIC VARIABLES"""
guildMusicInfo = {}

"""DATA STRUCTS"""


@dataclass
class SongInfo:
    reference: str
    title: str
    type: Constants.QueuePositionType


class GuildMusicInfo:
    def __init__(self, songsQueue: [], isStream: bool, durationOfCurrentSong: int,
                 isLoopActive: bool, currentSongTimeLeft: int, isPlaying: bool, isPaused: bool, timeLeftBar,
                 currQueueMessagePage: int, endOfTheSongTime: int, startTimeOfTheSong: int):
        self.songsQueue = songsQueue
        self.isStream = isStream
        self.durationOfCurrentSong = durationOfCurrentSong
        self.isLoopActive = isLoopActive
        self.currentSongTimeLeft = currentSongTimeLeft
        self.isPlaying = isPlaying
        self.isPaused = isPaused
        self.timeLeftBar = timeLeftBar
        self.currQueueMessagePage = currQueueMessagePage
        self.endOfTheSongTime = endOfTheSongTime
        self.startTimeOfTheSong = startTimeOfTheSong


"""GLOBAL VARIABLES METHODS"""


def resetMusicVariables(guildId, isFullReset=True):
    if isFullReset:
        guildMusicInfo[guildId] = GuildMusicInfo([], False, 0, False, 0, False, False, None, 0, 0, 0)
    else:
        guildMusicInfo[guildId].isStream = False
        guildMusicInfo[guildId].durationOfCurrentSong = 0
        guildMusicInfo[guildId].isLoopActive = False
        guildMusicInfo[guildId].currentSongTimeLeft = 0
        guildMusicInfo[guildId].isPlaying = False
        guildMusicInfo[guildId].isPaused = False
        guildMusicInfo[guildId].timeleftFar = None
        guildMusicInfo[guildId].currQueueMessagePage = 0
        guildMusicInfo[guildId].endOfTheSongTime = 0
        guildMusicInfo[guildId].startTimeOfTheSong = 0


def setMusicVariables(guildId, isPlayingArg, isStreamArg, durationOfCurrentSongArg, isLoopActiveArg,
                      currentSongTimeLeftArg, isPausedArg, endOfTheSongTimeArg, startTimeOfTheSongArg):
    guildMusicInfo[guildId].isPlaying = isPlayingArg
    guildMusicInfo[guildId].isStream = isStreamArg
    guildMusicInfo[guildId].durationOfCurrentSong = durationOfCurrentSongArg
    guildMusicInfo[guildId].isLoopActive = isLoopActiveArg
    guildMusicInfo[guildId].currentSongTimeLeft = currentSongTimeLeftArg
    guildMusicInfo[guildId].isPaused = isPausedArg
    guildMusicInfo[guildId].endOfTheSongTime = endOfTheSongTimeArg
    guildMusicInfo[guildId].startTimeOfTheSong = startTimeOfTheSongArg


def addToQueueAllPlaylistSongs(listOfSongs, guildId):
    for song in listOfSongs:
        originalName = f"{song[0]} - {song[1]}"
        artist = song[1].replace(" ", "+")
        songName = song[0].replace(" ", "+")
        songName = songName.replace("&", "and")
        artist = artist.replace("&", "and")
        youtubeSearchString = artist + "+" + songName + "+" + "song"
        youtubeSearchString = unidecode.unidecode(youtubeSearchString)
        guildMusicInfo[guildId].songsQueue.append(SongInfo(youtubeSearchString, originalName, Constants.QueuePositionType.SONG))


def addToQueueAllYoutubePlaylistSongs(listOfSongs, guildId):
    for i in range(0, len(listOfSongs)):
        guildMusicInfo[guildId].songsQueue.append(SongInfo(listOfSongs[i], listOfSongs.videos[i].title, Constants.QueuePositionType.SONG))



def addToQueueAllYoutubeMixSongs(info, guildId):
    for i in range(len(info['entries'])):
        title = info['entries'][i]['title'].replace("[", "(")
        title = title.replace("]", ")")
        guildMusicInfo[guildId].songsQueue.append(SongInfo(info['entries'][i]['url'], title, Constants.QueuePositionType.SONG))



def lookForPlaylistName(guildId, playlistName):
    playlistNameAux = playlistName
    i = 1
    while True:
        changed = False
        for playlist in guildMusicInfo[guildId].playlistsQueue:
            if playlist == playlistNameAux:
                playlistNameAux = f"{playlistName} ({i})"
                changed = True
        i += 1
        if not changed:
            break
    return playlistNameAux

def getPositionOfPlaylistInQueue(key, guildId):
    for i in range(0, len(guildMusicInfo[guildId].songsQueue)):
        if guildMusicInfo[guildId].songsQueue[i].title == key:
            print("entrou")
            return i