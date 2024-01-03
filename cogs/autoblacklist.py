import discord
from prince.bot import Bot
from discord.ext import commands
from prince1.Tools import add_user_to_blacklist

#class blacklist(commands.Cog):
#  def __init__(self, client):
    #self.client = client

class AutoBlacklist(commands.Cog):
    def __init__(self, client):
      self.client = client
      self.spam_cd_mapping = commands.CooldownMapping.from_cooldown(3, 4, commands.BucketType.member)
      self.spam_command_mapping = commands.CooldownMapping.from_cooldown(3, 4, commands.BucketType.member)

      print("Cog Loaded: AutoBlacklist")

    @commands.Cog.listener()
    async def on_message(self, message):
      bucket = self.spam_cd_mapping.get_bucket(message)
      soward = '<@1004248513435152484>'
      retry = bucket.update_rate_limit()

      if retry:
        if message.content == soward or message.content == "<@!1004248513435152484>":
          add_user_to_blacklist(message.author.id)
          await message.channel.send(embed=discord.Embed(title="**Successfully Blacklisted {} For Spam Mentioning Me**".format(message.author.mention)), color=0x2f3136)


    @commands.Cog.listener()
    async def on_command(self, ctx):
      bucket = self.spam_command_mapping.get_bucket(ctx.message)
      retry = bucket.update_rate_limit()
      if retry:
        add_user_to_blacklist(ctx.author.id)
        await ctx.reply("**Successfully Blacklisted {} For Spamming My Commands**".format(ctx.author.mention))

async def setup(client):
  await client.add_cog(AutoBlacklist(client))        