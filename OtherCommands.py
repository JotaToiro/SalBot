import nextcord as discord
from nextcord.ext import commands
import yt_dlp as youtube_dl
import os
import GlobalMusicVariables as GMV
import lyr
from Constants import QueuePositionType

class otherCommands(commands.Cog):
	@commands.command()
	async def tomp3(self, ctx, *, link=None):
		if link is None:
			embedVar = discord.Embed(title="Addictional information needed, ex: >tomp3 link", color=0xe08a00)
			await ctx.send(embed=embedVar)

		if "https://www.youtube.com/watch?v=" not in link and "youtu.be/" not in link:
			embedVar = discord.Embed(title="Invalid ulr!", color=0xe08a00)
			await ctx.send(embed=embedVar)
		try:
			await ctx.message.author.send()
		except discord.Forbidden:
			embedVar = discord.Embed(
				title="Could not send you a DM with the audio file, please turn on your DMs if you want to use this functionality.",
				color=0xe08a00)
			await ctx.send(embed=embedVar)
			return
		except discord.HTTPException:
			ydl_opts = {
				'format': 'bestaudio/best',
				'postprocessors': [{
					'key': 'FFmpegExtractAudio',
					'preferredcodec': 'mp3',
					'preferredquality': '192'
				}],
				'postprocessor_args': [
					'-ar', '16000'
				],
				'prefer_ffmpeg': True
			}

			with youtube_dl.YoutubeDL(ydl_opts) as ydl:
				embedVar = discord.Embed(title="Processing...", color=0xe08a00)
				message = await ctx.send(embed=embedVar)
				info = ydl.extract_info(link)
				fileName = f"{info['title']} [{info['id']}].mp3"
				fileName = fileName.replace("/", "_")
				fileName = fileName.replace("'\'", "_")
				try:
					await ctx.message.author.send(file=discord.File(fileName, info['title'] + ".mp3"))
					embedVar = discord.Embed(title="I sent you a DM with your audio", color=0xe08a00)
					await ctx.send(embed=embedVar)
				except:
					embedVar = discord.Embed(title="Audio file is too large!", color=0xe08a00)
					await ctx.send(embed=embedVar)
				await message.delete()
				if os.path.exists(fileName):
					os.remove(fileName)

	@commands.command(aliases=['lyr'])
	async def lyrics(self, ctx, *, songName=None):
		guildId = ctx.message.guild.id
		if songName is None:
			if GMV.guildMusicInfo[guildId].songsQueue[0].type == QueuePositionType.SONG:
				query = GMV.guildMusicInfo[guildId].songsQueue[0].title
			else:
				key = GMV.guildMusicInfo[guildId].songsQueue[0].reference
				query = GMV.guildMusicInfo[guildId].playlistsQueue[key[0]][0].title
			nameOfTheSong = query
		else:
			query = songName
			nameOfTheSong = songName
		lyrics = lyr.lyrics(query)
		embedVar = discord.Embed(title=nameOfTheSong, description=lyrics, color=0xe08a00)
		await ctx.send(embed=embedVar)

def setup(client):
	client.add_cog(otherCommands(client))