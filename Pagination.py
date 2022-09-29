import GlobalMusicVariables as GMV
import nextcord as discord
from AuxMethods import AuxMethods
import Constants

class Pagination:
    def __init__(self, message, messageTitle, guildId):
        self.auxMethods = AuxMethods()
        self.guildId = guildId
        self.message = message
        self.messageTitle = messageTitle
        self.isPlaylistEmbed = self.checkIfIsPlaylistEmbed()
        self.pages = self.createPagesFromArray()


    def createPagesFromArray(self):
        pages = []
        i = 0
        j = 0
        pageNumber = 1
        indexString = "**"
        songsString = ""
        changed = False

        totalPages, d = divmod((len(GMV.guildMusicInfo[self.guildId].songsQueue)) / 10, 1)
        auxArray = GMV.guildMusicInfo[self.guildId].songsQueue.copy()
        songIndex = 0

        for info in auxArray:
            songName = info.title
            while self.auxMethods.get_pil_text_size(songName, 12, "arial.ttf")[0] > 290:
                changed = True
                songName = songName[:-1]
            if changed:
                songName += "..."
                changed = False
            if i == 0 and songIndex == 0:
                indexString += "Playing now" + "\n"
                if info.type == Constants.QueuePositionType.PLAYLIST:
                    songsString += "**(Playlist)**"
                if "youtube.com/watch?v=" in info.reference:
                    songsString += "᲼" + "[" + songName + "]" + "(" + info.reference + ")" + "\n"
                else:
                    songsString += "᲼" + songName + "\n"

                j -= 1
            elif i == 0 and songIndex > 0:
                indexString += str(i) + "\n"
                if info.type == Constants.QueuePositionType.PLAYLIST:
                    songsString += "**(Playlist)**"
                if "youtube.com/watch?v=" in info.reference:
                    songsString += " " + "[" + songName + "]" + "(" + info.reference + ")" + "\n"
                else:
                    songsString += "᲼" + songName + "\n"
                j -= 1
            else:
                if j == 9:

                    indexString += "**"
                    if self.isPlaylistEmbed:
                        embedVar = discord.Embed(title=self.messageTitle, description="", color=0xe08a00)
                        embedVar.add_field(name="Song index", value=indexString, inline=True)
                    else:
                        embedVar = discord.Embed(title=f"Next songs", description="", color=0xe08a00)
                        embedVar.add_field(name="Queue position", value=indexString, inline=True)
                    embedVar.add_field(name="Song", value=songsString, inline=True)
                    embedVar.set_footer(text="page "+str(pageNumber)+" of " + str(int(totalPages) + 1))
                    pages.append(embedVar)
                    pageNumber += 1
                    indexString = "**"
                    songsString = ""

                    indexString += str(i) + "\n"
                    if "youtube.com/watch?v=" in info.reference:
                        songsString += "᲼" + "[" + songName + "]" + "(" + info.reference + ")" + "\n"
                    else:
                        songsString += "᲼" + songName + "\n"
                    j = 0
                    i += 1
                    continue
                indexString += str(i) + "\n"
                if "youtube.com/watch?v=" in info.reference:
                    songsString += "᲼" + "[" + songName + "]" + "(" + info.reference + ")" + "\n"
                else:
                    songsString += "᲼" + songName + "\n"
            i += 1
            j += 1
        indexString += "**"
        if songsString != "":
            if self.isPlaylistEmbed:
                embedVar = discord.Embed(title=self.messageTitle, description="", color=0xe08a00)
                embedVar.add_field(name="Song index", value=indexString, inline=True)
            else:
                embedVar = discord.Embed(title=f"Next songs", description="", color=0xe08a00)
                embedVar.add_field(name="Queue position", value=indexString, inline=True)

            embedVar.add_field(name="᲼Song", value=songsString, inline=True)
            embedVar.set_footer(text="page " + str(pageNumber) + " of " + str(int(totalPages) + 1))
            pages.append(embedVar)
        return pages
    
    def page(self, index):
        curPage = self.getIndexFromMessage()
        return self.pages[curPage - 1 + index]


    def checkIfIsPlaylistEmbed(self):
        return False if "Next songs" in self.messageTitle else True

    def getIndexFromMessage(self):
        return int(self.message.split(" ")[1])


