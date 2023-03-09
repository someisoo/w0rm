import asyncio
import random
import discord
from discord.ext import commands

TOKEN = 'token shit here'
client = commands.Bot(command_prefix='!')

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

client.run(TOKEN)
