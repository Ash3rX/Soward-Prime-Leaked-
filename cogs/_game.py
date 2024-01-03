

import discord
import asyncio
import random
from discord.ext import commands
from games import  wumpus, twenty
#from Discord_Games import aki_buttons
from prince.bot import Bot
from prince.message import wait_for_msg
from prince.ui import BasicView
from config import MAIN_COLOR
from prince1.Tools import *

class TruthAndDareView(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=60)
        self.value = None

    @discord.ui.button(label="Dare", custom_id='dare', style=discord.ButtonStyle.danger)
    async def dare(self, button, interaction):
        self.value = 'dare'
        self.stop()

    @discord.ui.button(label="Truth", custom_id='truth', style=discord.ButtonStyle.green)
    async def truth(self, button, interaction):
        self.value = 'truth'
        self.stop()


class games3(commands.Cog, description="Play some fun games with me!"):
    def __init__(self, client: Bot):
        self.client = client

    @commands.command(aliases=['aki'], help="Play akinator!")
    @ignore_check()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.user)
    async def akinator(self, ctx):
        await aki_buttons.BetaAkinator().start(ctx, color=MAIN_COLOR)

    @commands.cooldown(1, 30, commands.BucketType.user)
    @ignore_check()
    @commands.command(name='2048', help="Play 2048 game.")
    async def twenty(self, ctx):
        await twenty.play(ctx, self.client)

    

    @commands.cooldown(1, 5, commands.BucketType.user)
    @ignore_check()
    @commands.command(name='wumpus', help="Play Wumpus game")
    async def _wumpus(self, ctx):
        await wumpus.play(self.client, ctx)

 

    
  
   
  
   
       
         
                
      
         

    
          
            
           
               
            

      
         
   
          
   
          
        
        
          
       
          
         
             
           
               

    @commands.command(aliases=['tnd', 'dare', 'truth', 'tod'], help="Play truth and dare!")
    
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def truthordare(self, ctx: commands.Context):
        view = TruthAndDareView(ctx)
        main_msg = await ctx.reply("Pick what u want to do?", view=view)
        await view.wait()
        if not view.value:
            return await main_msg.edit(content="Command cancelled or timed out!", view=None)
        if view.value == 'truth':
            truth_is_always_painful = random.choice([
                "When was the last time you lied?",
                "When was the last time you cried?",
                "What's your biggest fear?",
                "What's your biggest fantasy?",
                "Do you have any fetishes?",
                "What's something you're glad your mum doesn't know about you?",
                "Have you ever cheated on someone?",
                "What's the worst thing you've ever done?",
                "What's a secret you've never told anyone?",
                "Do you have a hidden talent?",
                "Who was your first celebrity crush?",
                "What are your thoughts on polyamory?",
                "What's the worst intimate experience you've ever had?",
                "Have you ever cheated in an exam?",
                "What's the most drunk you've ever been?",
                "Have you ever broken the law?",
                "What's the most embarrassing thing you've ever done?",
                "What's your biggest insecurity?",
                "What's the biggest mistake you've ever made?",
                "What's the most disgusting thing you've ever done?",
                "Who would you like to kiss in this room?",
                "What's the worst thing anyone's ever done to you?",
                "Have you ever had a run in with the law?",
                "What's your worst habit?",
                "What's the worst thing you've ever said to anyone?",
                "Have you ever peed in the shower?",
                "What's the strangest dream you've had?",
                "Have you ever been caught doing something you shouldn't have?",
                "What's the worst date you've been on?",
                "What's your biggest regret?",
                "What's the biggest misconception about you?",
                "Where's the weirdest place you've had sex?",
                "Why did your last relationship break down?",
                "Have you ever lied to get out of a bad date?",
                "What's the most trouble you've been in?"
            ])
            await main_msg.edit(content=f"```\n{truth_is_always_painful}\n```", view=None)
            msg_check = await wait_for_msg(ctx, 60, main_msg)
            if msg_check == 'pain':
                return
            else:
                await main_msg.edit(content="Oh, is that so? 😏 I didn't know that. **Shame! Shame!**", view=None)
        elif view.value == 'dare':
            dare_is_more_and_always_painful = random.choice([
                "Show the most embarrassing photo on your phone",
                "Show the last five people you texted and what the messages said",
                "Let the rest of the group DM someone from your Instagram account",
                "Eat a raw piece of garlic",
                "Do 100 squats",
                "Keep three ice cubes in your mouth until they melt",
                "Say something dirty to the person on your left",
                "Give a foot massage to the person on your right",
                "Put 10 different available liquids into a cup and drink it",
                "Yell out the first word that comes to your mind",
                "Give a lap dance to someone of your choice",
                "Remove four items of clothing",
                "Like the first 15 posts on your Facebook newsfeed",
                "Eat a spoonful of mustard",
                "Keep your eyes closed until it's your go again",
                "Send a sext to the last person in your phonebook",
                "Show off your orgasm face",
                "Seductively eat a banana",
                "Empty out your wallet/purse and show everyone what's inside",
                "Do your best sexy crawl",
                "Pretend to be the person to your right for 10 minutes",
                "Eat a snack without using your hands",
                "Say two honest things about everyone else in the group",
                "Twerk for a minute",
                "Try and make the group laugh as quickly as possible",
                "Try to put your whole fist in your mouth",
                "Tell everyone an embarrassing story about yourself",
                "Try to lick your elbow",
                "Post the oldest selfie on your phone on Instagram Stories",
                "Tell the saddest story you know",
                "Howl like a wolf for two minutes",
                "Dance without music for two minutes",
                "Pole dance with an imaginary pole",
                "Let someone else tickle you and try not to laugh",
                "Put as many snacks into your mouth at once as you can"
            ])
            await main_msg.edit(content=f"```\n{dare_is_more_and_always_painful}\n```", view=None)
            msg_check = await wait_for_msg(ctx, 60, main_msg)
            if msg_check == 'pain':
                return
            else:
                await main_msg.edit(content="Oh, seems like u have some guts. Well done.", view=None)


async def setup(client):
    await client.add_cog(games3(client))
