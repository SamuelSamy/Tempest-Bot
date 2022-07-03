from discord.ext import commands

import service.chat_logs as functions

class ChatLogs(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener("on_raw_message_delete")
    async def message_delete(self, ctx):
        await functions.send_delete_log(self.bot, ctx)


    @commands.Cog.listener("on_raw_message_edit")
    async def message_edit(self, ctx):
        await functions.send_edit_log(self.bot, ctx)
        