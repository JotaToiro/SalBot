import base64
import requests
import datetime
import Constants

class SpotifyAPI:

	client_creds = f'{Constants.SPOTIFY_CLIENT_ID}:{Constants.SPOTIFY_CLIENT_SECRET}'
	client_creds_b64 = base64.b64encode(client_creds.encode())

	token_url = "https://accounts.spotify.com/api/token"
	method = "POST"
	token_data = {
		"grant_type": "client_credentials"
	}
	token_headers = {
		"Authorization": f"Basic {client_creds_b64.decode()}"
	}

	access_token = ""


	def __init__(self):
		self.expires = datetime.datetime.now()
		pass

	def extract_track_id(self, url, linkType):
		if "?si=" in url:
			array = url.split("?si=")
			link = array[0]
		else:
			link = url
		trackId = link.split(f"/{linkType}/")[1]
		return trackId



	def setNewSpotifyToken(self):

		r = requests.post(self.token_url, data=self.token_data, headers=self.token_headers)
		token_response_data = r.json()
		self.accessToken = token_response_data['access_token']
		self.track_Request_Header = {
			"Authorization": f"Bearer {self.accessToken}"
		}
		while not r.status_code in range(200, 299):
			r = requests.post(self.token_url, data=self.token_data, headers=self.token_headers)
			token_response_data = r.json()
			self.accessToken = token_response_data['access_token']
			self.track_Request_Header = {
				"Authorization": f"Bearer {self.accessToken}"
			}
		expires_in = token_response_data['expires_in']
		now = datetime.datetime.now()
		self.expires = now + datetime.timedelta(seconds=expires_in)


	def getTrackNameAndArtist(self, trackId):
		endPoint = f"https://api.spotify.com/v1/tracks/{trackId}"

		if self.didExpired():
			self.setNewSpotifyToken()

		r = requests.get(endPoint, headers=self.track_Request_Header)
		while not r.status_code in range(200, 299):
			r = requests.get(endPoint, headers=self.track_Request_Header)
		song_data = r.json()


		return song_data['name'], song_data['artists'][0]['name']

	def getPlayListSongs(self, trackId, playlistType):
		if self.didExpired():
			self.setNewSpotifyToken()
		list = []
		offset = 0
		while True:
			endpoint = f"https://api.spotify.com/v1/{playlistType}/{trackId}/tracks?offset={offset}"
			r = requests.get(endpoint, headers=self.track_Request_Header)
			while not r.status_code in range(200, 299):
				r = requests.get(endpoint, headers=self.track_Request_Header)
			playlist_data = r.json()
			if len(playlist_data['items']) == 0:
				break
			else:
				if playlistType == "playlists":
					for i in range(len(playlist_data['items'])):
						var = tuple([playlist_data['items'][i]['track']['name'], playlist_data['items'][i]['track']['artists'][0]['name']])
						list.append(var)

				elif playlistType == "albums":
					for i in range(len(playlist_data['items'])):
						var = tuple(
							[playlist_data['items'][i]['name'], playlist_data['items'][i]['artists'][0]['name']])
						list.append(var)
				offset += Constants.DEFAULT_OFFSET_JUMP

		return list

	def getNameOfPlaylist(self, id, playlistType):
		endPoint = f"https://api.spotify.com/v1/{playlistType}/{id}"
		r = requests.get(endPoint, headers=self.track_Request_Header)
		while not r.status_code in range(200, 299):
			r = requests.get(endPoint, headers=self.track_Request_Header)

		data = r.json()
		return data['name']

	def didExpired(self):
		return self.expires <= datetime.datetime.now()