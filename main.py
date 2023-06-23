import discord
import os 
from dotenv import load_dotenv 
from discord.ext import tasks
import requests
import datetime

def main_func():
  intents = discord.Intents.default()
  intents.message_content = True
  client = discord.Client(intents=intents)
  
  global num
  num = 0
  global cur_map_time
  cur_map_time = 0
  global next_map
  next_map = '-'
  global main_color
  main_color = 0xff1500

  def get_map_rotation_info():
    res = requests.get('https://api.mozambiquehe.re/maprotation?auth='+os.getenv('APEX_API_KEY'))
    if res.status_code == 200:
      json_data = res.json()
      if 'Error' in json_data:
        return False
      return json_data
    else:
      print(f"Request failed with status code: {res.status_code}")
      return False

  def format_time(time_str):
    time = datetime.datetime.strptime(time_str, '%H:%M:%S')
    if time.hour > 0:
      return f'{time.hour}h {time.minute}m'
    elif time.minute == 0:
      if time.hour > 1:
        return f'{time.hour} horas'
      elif time.hour == 0:
        return 'Ninguno, 0 :v'
      else:
        return f'1 hora'
    else:
      return f'{time.minute} minutos'

  def format_minutes(mins):
    hours = mins // 60
    mins %= 60
    if hours > 0:
      if mins > 0:
        return f'{hours}h {mins}m'
      else:
        return f'{hours} horas' if hours > 1 else f'1 hora'
    else:
      return f'{mins} minutos' if mins > 1 else '1 minuto'

  async def get_map_rotation_embed():
    data = get_map_rotation_info()
    embed = discord.Embed(title="Rotación de mapa", type="rich", color=main_color, timestamp=datetime.datetime.now())
    
    if data:
      match data['current']['map']:
        case "King's Canyon":
          mapImgUrl = 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/0/0a/Kings_Canyon_MU3_REV1.png/'
        case "World's Edge":
          mapImgUrl = 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/f/f3/World%27s_Edge_MU3_REV1.png/'
        case "Olympus":
          mapImgUrl = 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/3/3a/Olympus_MU1.png/'
        case "Storm Point":
          mapImgUrl = 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/5/56/Storm_Point_MU1.png/'
        case "Broken Moon":
          mapImgUrl = 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/5/55/Broken_Moon.png/'
        case _:
          mapImgUrl = 'https://i.imgur.com/4UB9Cun.png'

      embed.set_thumbnail(url=mapImgUrl)
      embed.set_footer(text='Apex Info Bot by barelyfalse')
      embed.add_field(name='Mapa actual', value=data['current']['map'])
      embed.add_field(name='Tiempo restante', value=format_time(data['current']['remainingTimer']))
      embed.add_field(name='', value='', inline=False)
      embed.add_field(name='Siguiente mapa', value=data['next']['map'])
      embed.add_field(name='Duración', value=format_minutes(data['next']['DurationInMinutes']))
    else:
      embed.add_field(name='Error :c', value='Intentalo de nuevo!')
    
    return embed

  class MapRotationEmebedView(discord.ui.View):
    @discord.ui.button(label="Actualizar", style=discord.ButtonStyle.primary, emoji="🔄")
    async def update_embed_button(self, button, interaction):
      new_embed = await get_map_rotation_embed()
      await interaction.response.edit_message(embed=new_embed, view=self)

  @client.event
  async def on_ready():
    print(f'We have logged in as {client.user}')
    update_activity.start()

  @tasks.loop(minutes=1)
  async def update_activity():
    global cur_map_time
    global next_map
    if cur_map_time > 0:
      print(f'{next_map} in {cur_map_time}')
      await client.change_presence(activity=discord.Game(f'{next_map} en {format_minutes(cur_map_time)}'))
      cur_map_time -= 1
    else:
      data = get_map_rotation_info()
      if data:
        match data['next']['map']:
          case "King's Canyon":
            next_map = 'KC'
          case "World's Edge":
            next_map = 'WE'
          case "Olympus":
            next_map = 'O'
          case "Storm Point":
            next_map = 'SP'
          case "Broken Moon":
            next_map = 'BM'
          case _:
            next_map = '-'
        cur_map_time = data['current']['remainingMins']
        activity = discord.Game(f'{next_map} en {format_minutes(cur_map_time)}')
        await client.change_presence(activity=activity)
        cur_map_time -= 2
      else:
        activity = discord.Game("morirse")
        await client.change_presence(activity=activity)

  @client.event
  async def on_message(message):
    if message.author == client.user:
      return

    if message.content.startswith('$hello'):
      embedVar = discord.Embed(title="Hello!", description="Desc", color=main_color)
      embedVar.add_field(name="Field1", value="hi", inline=False)
      await message.channel.send(embed=embedVar)
    
    if message.content.startswith('$apexrot'):
      embed = await get_map_rotation_embed()
      view = MapRotationEmebedView()
      await message.channel.send(embed=embed, view=view)
      
  client.run(os.getenv('DC_API_KEY'))

if __name__ == '__main__':
  load_dotenv()
  
  main_func()