import discord
import os 
from dotenv import load_dotenv 

def main_func():
  intents = discord.Intents.default()
  intents.message_content = True

  client = discord.Client(intents=intents)

  @client.event
  async def on_ready():
    print(f'We have logged in as {client.user}')

  @client.event
  async def on_message(message):
    if message.author == client.user:
      return

    if message.content.startswith('$hello'):
      embedVar = discord.Embed(title="Hello!", description="Desc", color=0x00ff00)
      embedVar.add_field(name="Field1", value="hi", inline=False)
      embedVar.add_field(name="Field2", value="hi2", inline=False)
      await message.channel.send(embed=embedVar)
  
  client.run(os.getenv('DC_API_KEY'))

if __name__ == '__main__':
  load_dotenv()
  
  main_func()