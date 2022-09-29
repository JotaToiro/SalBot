import nextcord as discord
from nextcord.ext import commands, tasks
import GlobalMusicVariables as GMV
from AuxMethods import AuxMethods
from Buttons import songInteractionsPlaying
from nextcord import ButtonStyle

class Tasks(commands.Cog):
	def __init__(self):
		self.auxMethods = AuxMethods()
		self.updateTimeLeftBar.start()

	@tasks.loop(seconds=10.0)
	async def updateTimeLeftBar(self):
		for guildId in GMV.guildMusicInfo:
			if GMV.guildMusicInfo[guildId].timeLeftBar is None and len(GMV.guildMusicInfo[guildId].songsQueue) > 0:
				print("Task error")
				continue
			if len(GMV.guildMusicInfo) > 0 and not GMV.guildMusicInfo[guildId].isPaused and GMV.guildMusicInfo[guildId].isPlaying:

				if GMV.guildMusicInfo[guildId].isStream:
					songName = GMV.guildMusicInfo[guildId].songsQueue[0].title
					myStr = "ㅤㅤㅤㅤㅤㅤㅤㅤㅤ**🔴  Streaming!**"
					view = songInteractionsPlaying()
					view.children[2].disabled = True
				else:
					myStr, songName = self.auxMethods.generateProgressBarString(guildId)
					view = songInteractionsPlaying()
				if GMV.guildMusicInfo[guildId].isLoopActive:
					title = "Playing now!  <:loopicon:1006005075652640811>"
					view.children[2].style = ButtonStyle.green
				else:
					title = "Playing now!"
					view.children[2].style = ButtonStyle.gray
				embedVar = discord.Embed(title=title, color=0xe08a00)
				embedVar.add_field(name=songName, value=myStr, inline=True)
				try:
					await GMV.guildMusicInfo[guildId].timeLeftBar.edit(embed=embedVar, view=view)
				except:
					print("falied edit")

def setup(client):
	client.add_cog(Tasks())