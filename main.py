import nextcord as discord
from nextcord.ext import commands
from nextcord import Interaction
import datetime
import music
import OtherCommands
import Constants
import Tasks

from AuxMethods import AuxMethods

cogs = [music, OtherCommands, Tasks]
intents = discord.Intents().all()
client = commands.Bot(command_prefix = '>', intents = intents)



for i in range(len(cogs)):
	cogs[i].setup(client)

client.remove_command("help")


@client.event
async def on_guild_join(guild):
	channels = guild.text_channels
	for channel in channels:
		if channel and channel.permissions_for(guild.me).send_messages:
			embed=discord.Embed(title="**Thanks For Adding Me!**", description=f"""
			Thanks for adding me to **{guild.name}**!
			You can use the `>help` command to get started!
			""", color=0xe08a00)
			await channel.send(embed=embed)
			return
		else:
			continue
	return


@client.slash_command(name="mainteste", guild_ids=Constants.TEST_SERVERS_IDS)
async def main():
	pass


@client.slash_command(name="teste", description="teste", guild_ids=Constants.TEST_SERVERS_IDS)
async def music(interaction: Interaction, argteste: str):
	await interaction.response.send_message(argteste)


@client.command()
async def clear_dm(ctx):
	if ctx.message.author.id != Constants.ADMIN_ID:
		await ctx.send("`You do not have permission to execute this command`")
		return

	messages_to_remove = 1000
	async for message in client.get_user(Constants.ADMIN_ID).history(limit=messages_to_remove):
		if message.author.id == client.user.id:
			await message.delete()

@client.command()
async def setupadmin(ctx, member: discord.Member):
	return

@client.command(aliases=['vc'])
async def connectedVoiceClients(ctx):
	if ctx.message.author.id != Constants.ADMIN_ID:
		await ctx.send("`You do not have permission to execute this command`")
		return

	voiceClientsString = ""
	for vc in client.voice_clients:
		voiceClientsString += "**" + vc.guild.name + "**\n";
	embedVar = discord.Embed(title=f"Connected to **{len(client.voice_clients)}** voice clients", description=voiceClientsString, color=0xe08a00)
	await ctx.message.author.send(embed=embedVar)


@client.command(aliases=['||logs||'])
async def logs(ctx, isGlobal = "local"):
	await ctx.message.delete()
	if ctx.message.author.id != Constants.ADMIN_ID:
		await ctx.send("`You do not have permission to execute this command`")
		return
	resultFileName = ""
	if isGlobal == "local":
		logFileContent = open(f'logs/{ctx.message.guild.id}.txt', 'rb')
		#messageContent = "```" + logFileContent + "```"
		resultFileName = f"{ctx.message.guild.id}.txt"
	if isGlobal == "global":
		logFileContent = open('_logs.txt', 'rb')
		#messageContent = "```" + logFileContent + "```"
		resultFileName = "_logs.txt"
	await ctx.message.author.send("Logs: ", file=discord.File(logFileContent, resultFileName))
	embedVar = discord.Embed(title="I sent you a DM!",
							 color=0xe08a00)
	await ctx.send(embed=embedVar)


@client.command(aliases=['h'])
async def help(ctx):
	auxMethods = AuxMethods()
	auxMethods.generateLogString(str(datetime.datetime.now()),
								 str(ctx.message.author),
								 str(ctx.message.author.id),
								 str(ctx.message.guild),
								 str(ctx.message.guild.id),
								 str(ctx.message.content))

	embedVar = discord.Embed(title="Available commands", description="__**Music**__\n\n"
										   "**>play**(p) - Play a song if you provide a link or string corresponding to the song name.\n"
										   "**>playrandom**(pr) - Play spotify playlist in random order.\n"
										   "**>queue**(q) - Show the songs in the queue.\n"
										   "**>skip**(s) - Skip to the next music, or if you give adictional information skip to the song in the queue position you provided ex: >skip 3 , skips to the song in the position 3.\n"
										   "**>loop**(l) - Loops through the current song.\n"
										   "**>pause** - Pause the current song.\n"
										   "**>resume** - Continues playing the current song.\n"
										   "**>time**(t) - Shows the time left to the end of the current song.\n"
										   "**>lyrics**(lyr) - Shows the lyrics of the current song, or if addictional information is given, shows the lyrics of the song provided.\n"
										   "**>tomp3** - Sends you a DM with the audio file of the video provided.\n"
										   "**>remove**(r) - Removes the songs with index the user provided ex: >remove 2 3 , removes the songs in the index 2 and 3, >remove all , removes all songs in the queue.\n"
										   "**>reorder** - Reorders the songs in queue ex: >reorder 2 4 , switch position of the songs 2 and 4.\n"
										   "**>top** - Shows the top 5 songs of the user ex: >top , shows top 5 songs of the user, ex: >top cur @user , shows top 5 of the user mentioned.\n"
										   "**>servertop** - Shows the top 10 songs of the server.\n"
										   "**>disconnect**(disc, dc) - Disconnects the bot from the channel.\n"
										   "**>help**(h) - Shows this message.\n\n"
										   "**Additionaly, you can add a reaction to the >top and >servertop commands output to play the corresponding song, and add a reaction to the >queue command output to skip to the next song in the queue.**",
							 color=0xe08a00)

	#this footer just says that the bot was made by me and has the url for my profile picture, this can be customized at your will
	#embedVar.set_footer(text="Bot made by Peixe Graúdo", icon_url="https://media.discordapp.net/attachments/760582402845704255/915006775957262346/Peixe_Graudo.jpg")
	await ctx.send(embed=embedVar)

'''@client.event
async def on_disconnect():
	print("entrou")'''



@client.event
async def on_ready():
	print("bot ready")
	await client.change_presence(activity=discord.Game(name=">sal grosso!"))




@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound):
		await ctx.send("Invalid command!")

client.run(Constants.TEST_BOT_TOKEN)
