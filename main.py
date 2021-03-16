from discord.ext import commands
import os
import asyncio
import json
import requests
import re
import discord


prefix = '.'
client = commands.Bot(command_prefix=prefix, case_insensitive=True, help_command=None)

weather_api = os.getenv("weather_key")

class cards:
  def __init__(self, value, suit):
    self.value = value
    self.suit = suit


suits = ['heart', 'diamonds', 'spades', 'clubs']
deck = [cards(value, suit) for value in range(1, 14) for suit in suits]
weather_words = ["weather", "hot", "cold"]

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))



@client.command(name="help")
async def help(ctx):
    if ctx.author == client.user:
      return

    await ctx.channel.send('Hi, you found me, I am pretty useless right now, use . to summon me and I can look up the weather for you using .weather or seach up a term on urban dictionary using .urbandict [your term]')

@client.command(name="cards")
async def on_message(ctx):
    if ctx.author == client.user:
        return

    for i in range(len(deck)):
      await ctx.channel.send("The card is '{0}'' with a suit of '{1}'".format(deck[i].value,deck[i].suit))


@client.command(name="schedule_send")
async def schedule_send(ctx):
    if ctx.author == client.user:
      return
    def check(msg):
      return msg.author == ctx.author and msg.channel == ctx.channel 

    await ctx.channel.send('What is your message?')
    try:
      msg = await client.wait_for('message', check=check, timeout=30)
    except asyncio.TimeoutError:
      await ctx.channel.send("Sorry, you didn't reply in time!")
      return

    
    await ctx.channel.send("When do you want to send it")
    try:
      msg = await client.wait_for('message', check=check, timeout=30)
    except asyncio.TimeoutError:
      await ctx.channel.send("Sorry, you didn't reply in time!")
      return


@client.command(name="ping")
async def _ping(ctx):
    if ctx.author == client.user:
        return

    await ctx.send('pong! that took {0}ms'.format(round(client.latency*1000, 0)))

@client.command(name="weather")
async def weather(ctx):
    if ctx.author == client.user:
      return

    def check(msg):
      return msg.author == ctx.author and msg.channel == ctx.channel 

    await ctx.channel.send('Interested in the weather? Where are you located right now?')
    try:
      city = await client.wait_for('message', check=check, timeout=30)
    except asyncio.TimeoutError:
      await ctx.channel.send("Sorry, you didn't reply in time!")
      return

    request_city = city.content
    weather = requests.get("https://api.openweathermap.org/data/2.5/weather?units=metric&q={0}&appid={1}".format(request_city,weather_api))
    current_weather_data = json.loads(weather.text)
    temperture = current_weather_data["main"]["temp"]
    weather_status = current_weather_data["weather"][0]["description"]
    longitude = current_weather_data["coord"]["lon"]
    latitude = current_weather_data["coord"]["lat"]
    forcast = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat={0}&lon={1}&units=metric&exclude=current,minutely,hourly,alerts&appid={2}".format(latitude,longitude,weather_api))
    future_weather_data = json.loads(forcast.text)
    today_weather = future_weather_data["daily"][0]["weather"][0]["description"]
    today_high = future_weather_data["daily"][0]["temp"]["max"]
    await ctx.channel.send("It is currently {0} degrees with {1} outside, it will  reach a high of {2} later today with {3}".format(round(temperture, 0), weather_status, round(today_high, 0), today_weather))


@client.command(name="urbandict")
async def urban_(ctx, arg):
    if ctx.author == client.user:
        return
    definition = requests.get("http://api.urbandictionary.com/v0/define?term={0}".format(arg))
    urban_def = json.loads(definition.text)
    meaning = urban_def["list"][0]["definition"]
    meaning = re.sub(r"\[|\]", "", meaning)
    example = urban_def["list"][0]["example"]
    example = re.sub(r"\[|\]", "", example)
    embedVar = discord.Embed(title=arg, color=0x00ff00)
    embedVar.add_field(name="Top definition", value=meaning, inline=False)
    embedVar.add_field(name="Examples:", value=example, inline=False)
    await ctx.channel.send(embed=embedVar)

    
client.run(os.getenv('TOKEN'))