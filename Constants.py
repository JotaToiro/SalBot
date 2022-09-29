
"""DISCORD CONSTS"""
TEST_SERVERS_IDS = "array of test servers ids []"
ADMIN_ID = "your discord account id for administration purposes"
SAL_BOT_TOKEN = "your discord bot application token"
TEST_BOT_TOKEN = "your discord bot application token for tests"

"""SPOTIFY CONSTS"""
SPOTIFY_CLIENT_ID = "your spotify client id"
SPOTIFY_CLIENT_SECRET = "your spotify secrete"
DEFAULT_OFFSET_JUMP = 100

"""DB CONSTS"""
HOST = "your data base host"
USER = "data base user"
PASSWORD = "user password"
DATABASE = 'your data base name'

"""OTHER CONSTS"""
NUMBERS = [""] * 10
'''NUMBERS[0] = "<:1_:1010303047106318537>"
NUMBERS[1] = "<:2_:1010303048289099797>"
NUMBERS[2] = "<:3_:1010303049518031068>"
NUMBERS[3] = "<:4_:1010305635625214073>"
NUMBERS[4] = "<:5_:1010305636925456445>"
NUMBERS[5] = "<:6_:1010305638062112868>"
NUMBERS[6] = "<:7_:1010305639244906666>"
NUMBERS[7] = "<:8_:1010305640276701346>"
NUMBERS[8] = "<:9_:1010305641979588658>"
NUMBERS[9] = "<:10:1010305643166568539>"'''

NUMBERS[0] = ":one:"
NUMBERS[1] = ":two:"
NUMBERS[2] = ":three:"
NUMBERS[3] = ":four:"
NUMBERS[4] = ":five:"
NUMBERS[5] = ":six:"
NUMBERS[6] = ":seven:"
NUMBERS[7] = ":eight:"
NUMBERS[8] = ":nine:"
NUMBERS[9] = "🔟"

QUEUE_ARROW_NEXT = "⏩"

YDL_OPTIONS_INFO = {'format': 'bestaudio/best'}

YDL_OPTIONS_VIDEO = {
			'quiet': False,
			'default_search': 'ytsearch',
			'format': 'bestaudio/best',
			'youtube_include_dash_manifest': False,
			'retries': 10,
			'age_limit': 20,
			'noplaylist': True
		}

YDL_OPTIONS_MIX = {
				'extract_flat': True,
				'quiet': False,
				'default_search': 'ytsearch',
				'format': 'bestaudio/best',
				'youtube_include_dash_manifest': False,
				'retries': 10,
				'age_limit': 20,
                'noplaylist': False
			}



from enum import Enum
class PlatformType(Enum):
	YOUTUBE = 1
	YOUTUBE_NO_LINK = 2
	SPOTIFY_TRACK = 3
	SPOTIFY_PLAYLIST = 4
	SPOTIFY_ALBUM = 5
	SOUND_CLOUD = 6
	YOUTUBE_PLAYLIST = 7
	YOUTUBE_MIX = 8

class QueuePositionType(Enum):
	PLAYLIST = 1
	SONG = 2
	STREAM = 3

class MessageButtonsValues(Enum):
	SONG_1 = 0
	SONG_2 = 1
	SONG_3 = 2
	SONG_4 = 3
	SONG_5 = 4
	SONG_6 = 5
	SONG_7 = 6
	SONG_8 = 7
	SONG_9 = 8
	SONG_10 = 9
	NEXT_PAGE = 10
	PREVIOUSE_PAGE = 11
	SHUFFLE = 12
	NEXT_SONG = 13
	PLAY = 14
	PAUSE = 15
	SKIP = 16
	LOOP = 17
