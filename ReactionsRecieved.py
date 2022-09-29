import nextcord as discord
from nextcord.ext import commands


class ReactionsRecieved(commands.Cog):
    def __int__(self):
        pass

    '''@commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        emoji = payload.emoji
        member = payload.member
        url = ""
        channel = self.client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        messageEmbeds = message.embeds
        embedTitle = messageEmbeds[0].title
        #reaction = get(message.reactions, emoji=payload.emoji.name)'''