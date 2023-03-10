# Sample Python code for a Discord bot that runs a simple 'Battle Royale' trivia game.
#
# Here's how it works::
# 1. Imports the required libraries, including:
#        - Discord.py - Discord Bot API Python wrapper.
#        - asyncio - For handling asynchronous events.
#
# 2. There's a Player() class and a Game() class.
#     - They are used to keep track of the players, questions, and scores.
#
# 3. The Game class has two methods: start() and play().
#    - The start() method initializes the game and waits for the specified timeout (30s) before calling play().
#    - The play() method runs a loop for a specified number of rounds, each round picking a random question and waiting for the players to answer. 
#        - If a player answers correctly, their score is updated.
#        - If a player answers incorrectly, they are eliminated from the game.
#
# 4. The code defines two Discord bot commands: start_game() and stop_game().
#     - start_game() checks if the bot is connected to a voice channel and starts a new Game object to run the trivia game.
#     - stop_game() is not defined / implemented yet.
#
# 5. client.run() is called to start the Discord bot using the provided Bot token.

from discord.ext import commands
import asyncio
import random
import discord
import os

BOT_TOKEN = os.getenv('DISCORD_AUTH_KEY') # 
intents = discord.Intents.all() # https://discordpy.readthedocs.io/en/latest/intents.html?highlight=intents
client = commands.Bot(command_prefix='!', intents=intents)

class Player:
    def __init__(self, member):
        self.member = member
        self.score = 0

    def correct_answer(self):
        self.score += 1

class Game:
    def __init__(self, ctx):
        self.ctx = ctx
        self.questions = [] # questions
        self.players = []
        self.current_question = None
        self.round = 0
        self.max_rounds = 10
        self.timeout = 30.0

    async def start(self):
        await self.initialize()
        await asyncio.sleep(self.timeout)
        await self.play()

    async def initialize(self):
        await self.ctx.send("Initializing game, please wait...")
        self.players = [Player(member) for member in self.ctx.voice_client.channel.members if not member.bot]
        await self.ctx.send(f"Game starting with {len(self.players)} players! You have {self.timeout} seconds to answer each question.")

    async def play(self):
        for self.round in range(1, self.max_rounds+1):
            await self.ctx.send(f"Round {self.round}!")
            self.current_question = random.choice(self.questions)
            correct_index = random.randint(0, len(self.current_question['answers'])-1)
            correct_answer = self.current_question['answers'][correct_index]
            answers = [f"{i+1}. {answer}" for i, answer in enumerate(self.current_question['answers'])]
            embed = discord.Embed(title=self.current_question['question'], description='\n'.join(answers), color=discord.Color.green())
            message = await self.ctx.send(embed=embed)

            def check(m):
                return m.author in [player.member for player in self.players] and m.channel == self.ctx.channel

            try:
                answer = await client.wait_for('message', timeout=self.timeout, check=check)
            except asyncio.TimeoutError:
                await self.ctx.send("Time's up!")
                break

            if answer.content.isdigit() and 1 <= int(answer.content) <= len(self.current_question['answers']):
                selected_index = int(answer.content) - 1
                if self.current_question['answers'][selected_index] == correct_answer:
                    await self.ctx.send(f"{answer.author.mention} got it right!")
                    for player in self.players:
                        if player.member == answer.author:
                            player.correct_answer()
                else:
                    await self.ctx.send(f"{answer.author.mention} got it wrong and is eliminated!")
                    self.players = [player for player in self.players if player.member != answer.author]
                    if len(self.players) == 1:
                        break
            else:
                await self.ctx.send(f"Invalid answer from {answer.author.mention}!")
                continue

        await self.ctx.send("Game over!")
        if self.players:
            winner = max(self.players, key=lambda player: player.score)
            await self.ctx.send(f"The winner is {winner.member.mention} with {winner.score} points!")
        else:
            await self.ctx.send("No players left!")

@client.command()
async def start_game(ctx):
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    game = Game(ctx)
    await game.start()

@client.command()
async def start_game(ctx):
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    game = Game(ctx)
    await game.start()

client.run(BOT_TOKEN)
