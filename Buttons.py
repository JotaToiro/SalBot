from nextcord import ui
from nextcord import ButtonStyle
from nextcord import Interaction
import nextcord as discord
import GlobalMusicVariables as GMV
from Pagination import Pagination
import time
import random
from AuxMethods import AuxMethods
import Constants


class queuePages(ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.message = None
        self.auxMethods = AuxMethods()

    async def on_timeout(self):
        self.children[0].disabled = True
        self.children[1].disabled = True
        self.children[2].disabled = True

        await self.message.edit(view=self)

    @ui.button(label="🡸", style=ButtonStyle.gray)
    async def previous(self, button: ui.Button, interaction: Interaction):
        await interaction.response.defer()
        guildId = interaction.guild_id
        embedPage = Pagination(interaction.message.embeds[0].footer.text, interaction.message.embeds[0].title, guildId)
        if embedPage.getIndexFromMessage() == 1:
            return
        newEmbed = embedPage.page(-1)

        await interaction.message.edit(embed=newEmbed)

    @ui.button(label="🡺", style=ButtonStyle.gray)
    async def next(self, button: ui.Button, interaction: Interaction):
        await interaction.response.defer()
        guildId = interaction.guild_id
        embedPage = Pagination(interaction.message.embeds[0].footer.text, interaction.message.embeds[0].title, guildId)
        if embedPage.getIndexFromMessage() == len(embedPage.pages):
            return
        newEmbed = embedPage.page(1)

        await interaction.message.edit(embed=newEmbed)

    @ui.button(emoji="<:shuffleicon:1008874990248149084>", label="", style=ButtonStyle.blurple)
    async def shuffle(self, button: ui.Button, interaction=Interaction):
        await interaction.response.defer()
        guildId = interaction.guild_id

        firstSong = GMV.guildMusicInfo[guildId].songsQueue[0].reference
        random.shuffle(GMV.guildMusicInfo[guildId].songsQueue)
        self.passTheOldFirstSongToTheFirst(guildId, firstSong)
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
        embedVar = discord.Embed(title="Next songs", description="",
                                 color=0xe08a00)
        embedVar.add_field(name="Queue position", value=indexString, inline=True)
        embedVar.add_field(name="Song", value=songsString, inline=True)
        embedVar.set_footer(text="page 1 of " + str(int(totalPages) + 1))

        await self.message.edit(embed=embedVar)

    def getIndexFromMessage(self, embed):
        return int(embed.split(" ")[1])

    def passTheOldFirstSongToTheFirst(self, guildId, firstSong):
        for i in range(0, len(GMV.guildMusicInfo[guildId].songsQueue)):
            if GMV.guildMusicInfo[guildId].songsQueue[i].reference == firstSong:
                aux = GMV.guildMusicInfo[guildId].songsQueue[i]
                GMV.guildMusicInfo[guildId].songsQueue.pop(i)
                GMV.guildMusicInfo[guildId].songsQueue.insert(0, aux)
                break


class songInteractionsPlaying(ui.View):
    def __init__(self):
        super().__init__()
        self.auxMethods = AuxMethods()
        self.message = None

    async def on_timeout(self):
        '''self.children[0].disabled = True
        self.children[1].disabled = True
        self.children[2].disabled = True
        self.children[3].disabled = True
        self.children[4].disabled = True'''

        if self.message is not None:
            await self.message.edit(view=self)
        else:
            pass

    @ui.button(emoji='<:pauseicon:1006005093134516254>', label="", style=ButtonStyle.green)
    async def pause(self, button: ui.Button, interaction: Interaction):
        await interaction.response.defer()
        guildId = interaction.guild_id
        view = songInteractionsPlaying()
        if GMV.guildMusicInfo[guildId].isPaused:
            interaction.guild.voice_client.resume()
            view.children[0].emoji = "<:pauseicon:1006005093134516254>"
            GMV.guildMusicInfo[guildId].isPaused = False
            GMV.guildMusicInfo[guildId].endOfTheSongTime = int(time.time()) + GMV.guildMusicInfo[
                guildId].currentSongTimeLeft
        else:
            interaction.guild.voice_client.pause()
            view.children[0].emoji = "<:resumeicon:1006006527880073327>"
            GMV.guildMusicInfo[guildId].isPaused = True
            GMV.guildMusicInfo[guildId].currentSongTimeLeft = GMV.guildMusicInfo[guildId].endOfTheSongTime - int(
                time.time())
        message = interaction.message
        embedVar = message.embeds[0]
        await message.edit(embed=embedVar, view=view)

    @ui.button(emoji='<:skipicon:1006966592594260069>', label="", style=ButtonStyle.blurple)
    async def skip(self, button: ui.Button, interaction: Interaction):
        await interaction.response.defer()
        guildId = interaction.guild_id
        if len(GMV.guildMusicInfo[guildId].songsQueue) == 1:
            queueEmpty = True
        else:
            queueEmpty = False
        interaction.guild.voice_client.stop()
        message = interaction.message
        if GMV.guildMusicInfo[guildId].isStream:
            songName = GMV.guildMusicInfo[guildId].songsQueue[0]
            myStr = "ㅤㅤㅤㅤㅤㅤㅤㅤㅤ🔴  Streaming!"
            view = songInteractionsPlaying()
            view.children[2].disabled = True
        else:
            myStr, songName = self.auxMethods.generateProgressBarString(guildId)
            view = songInteractionsPlaying()
        if not queueEmpty:
            embedVar = discord.Embed(title="Playing now!", color=0xe08a00)
            embedVar.add_field(name=songName, value=myStr, inline=True)
            GMV.guildMusicInfo[guildId].timeLeftBar = await message.edit(embed=embedVar, view=view)
        else:
            view = None
            embedVar = discord.Embed(title="**There are no songs in queue**", color=0xe08a00)
            await message.edit(embed=embedVar, view=view)

    @ui.button(emoji="<:loopicon:1006005075652640811>", label="", style=ButtonStyle.gray)
    async def loop(self, button: ui.Button, interaction: Interaction):
        await interaction.response.defer()
        guildId = interaction.guild_id
        view = songInteractionsPlaying()
        if GMV.guildMusicInfo[guildId].isLoopActive:
            GMV.guildMusicInfo[guildId].isLoopActive = False
            view.children[2].style = ButtonStyle.gray
            title = "Playing now!"
        else:
            GMV.guildMusicInfo[guildId].isLoopActive = True
            view.children[2].style = ButtonStyle.green
            title = "Playing now!  <:loopicon:1006005075652640811>"
        message = interaction.message
        myStr, songName = self.auxMethods.generateProgressBarString(guildId)

        embedVar = discord.Embed(title=title, color=0xe08a00)
        embedVar.add_field(name=songName, value=myStr, inline=True)
        GMV.guildMusicInfo[guildId].timeLeftBar = await message.edit(embed=embedVar, view=view)

    @ui.button(emoji="◻", label="", style=ButtonStyle.red)
    async def stop(self, button: ui.Button, interaction: Interaction):
        await interaction.response.defer()
        guildId = interaction.guild_id
        GMV.titlesQueue[guildId].clear()
        GMV.guildMusicInfo[guildId].songsQueue.clear()
        interaction.guild.voice_client.stop()
        GMV.guildMusicInfo[guildId].isPlaying = False
        GMV.guildMusicInfo[guildId].timeLeftBar = None
        message = interaction.message
        view = None
        embedVar = discord.Embed(title="**There are no songs in queue**", color=0xe08a00)
        await message.edit(embed=embedVar, view=view)

    @ui.button(emoji='<:leaveicon:1006143559822491719>', label="", style=ButtonStyle.red)
    async def disconnect(self, button: ui.Button, interaction: Interaction):
        guildId = interaction.guild_id
        GMV.resetMusicVariables(guildId)
        interaction.guild.voice_client.stop()
        await interaction.guild.voice_client.disconnect()
        message = interaction.message
        view = None
        embedVar = discord.Embed(title="**There are no songs in queue**", color=0xe08a00)
        await message.edit(embed=embedVar, view=view)
