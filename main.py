import discord
import os 
from dotenv import load_dotenv 
from discord.ext import tasks
from discord import Option
import requests
import datetime
import time

def main_func():
  intents = discord.Intents.default()
  intents.message_content = True
  client = discord.Bot()
  
  global num
  num = 0
  global cur_map_time
  cur_map_time = 0
  global next_map
  next_map = '-'
  global main_color
  main_color = 0xff1500
  global map_urls 
  map_urls = {
    'Kings Canyon': 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/5/51/Kings_Canyon_MU4.png',
    'World\'s Edge': 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/f/f3/World%27s_Edge_MU3_REV1.png',
    'Olympus': 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/5/55/Olympus_MU2_REV1.png',
    'Storm Point': 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/5/56/Storm_Point_MU1.png',
    'Broken Moon': 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/5/55/Broken_Moon.png',
    'Party Crasher': 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/6/6a/Party_Crasher.png',
    'Phase runner': 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/8/89/Phase_Runner.png',
    'Overflow': 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/e/ea/Overflow.png',
    'Encore': 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/3/32/Encore.png',
    'Habitat': 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/a/ae/Habitat_4.png',
    'Drop Off': 'https://static.wikia.nocookie.net/apexlegends_gamepedia_en/images/5/59/Drop-Off.png'
  }

  def get_map_rotation_info():
    res = requests.get('https://api.mozambiquehe.re/maprotation?auth='+os.getenv('APEX_API_KEY'))
    if res.status_code == 200:
      json_data = res.json()
      if 'Error' in json_data:
        return False
      time.sleep(1)
      return json_data
    else:
      print(f"Request failed with status code: {res.status_code}")
      time.sleep(1)
      return False
  
  def get_map_rotation_info_v2():
    res = requests.get('https://api.mozambiquehe.re/maprotation?auth='+os.getenv('APEX_API_KEY')+'&version=v2')
    if res.status_code == 200:
      json_data = res.json()
      if 'Error' in json_data:
        return False
      time.sleep(1)
      return json_data
    else:
      print(f"Request failed with status code: {res.status_code}")
      time.sleep(1)
      return False

  def format_time(time_str):
    time = datetime.datetime.strptime(time_str, '%H:%M:%S')
    if time.hour > 0:
      if time.minute > 0:
        return f'{time.hour}h {time.minute}m'
      else:
        return f'{time.hour} horas' if time.hour > 1 else f'1 hora'
    else:
      return f'{time.minute} minutos' if time.minute > 1 else f'1 minuto'

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
  
  def search_for(data, target_string):
    if isinstance(data, dict):
      for key, value in data.items():
        if isinstance(value, str) and target_string in value:
          return True
        elif search_for(value, target_string):
          return True
    elif isinstance(data, list):
      for item in data:
        if isinstance(item, str) and target_string in item:
          return True
        elif search_for(item, target_string):
          return True
    return False

  async def get_map_rotation_embed(game_mode):
    match game_mode:
      case 'battle_royale':
        mode = 'Quick Play'
      case 'ranked':
       mode = 'Ranked'
      case 'arenas':
        mode = 'Arenas'
      case 'arenasRanked':
        mode = 'Arenas (ranked)'
    embed = discord.Embed(title=f"Rotación de mapa - `{mode}`", type="rich", color=main_color, timestamp=datetime.datetime.now())

    try:
      data = get_map_rotation_info_v2()
      
      data = data[game_mode]

      if data:
        if search_for(data['current'], 'No_Map_Data'):
          embed.add_field(name='Unknown Map Data! :<', value='')
        else:
          embed.add_field(name='Mapa actual', value=data['current']['map'])
          embed.add_field(name='Tiempo restante', value=format_time(data['current']['remainingTimer']))

        embed.add_field(name='', value='', inline=False)

        if search_for(data['next'], 'No_Map_Data'):
          embed.add_field(name='Unknown Map Data! :<', value='')
        else:
          embed.set_image(url=map_urls[data['next']['map']])
          embed.add_field(name='Siguiente mapa', value=data['next']['map'])
          embed.add_field(name='Duración', value=format_minutes(data['next']['DurationInMinutes']))
      else:
        raise ValueError("No data available.")
    except Exception as e:
      print('Error:', e)
      embed.add_field(name='Error :c', value='Intentalo de nuevo!')
    embed.set_footer(text='Apex Info Bot by barelyfalse')
    return embed

  class MapRotationEmbedView(discord.ui.View):
    def __init__(self, game_mode, iid):
      super().__init__(timeout=None)
      self.game_mode = game_mode
      self.id = f"rot_update_{iid}"

    @discord.ui.button(label="Actualizar", custom_id='rot', style=discord.ButtonStyle.primary, emoji="🔄")
    async def update_embed_button(self, button, interaction):
      button.custom_id = self.id
      new_embed = await get_map_rotation_embed(self.game_mode)
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
      
  @client.command(description='Shows map rotation')
  async def apexrot(ctx, mode: Option(str, "Enter mode", choices=["qp", "ranked", "arenas", "arenasranked"])):
    match mode:
      case 'qp':
        m = 'battle_royale'
      case 'ranked':
        m = mode
      case 'arenas':
        m = mode
      case 'arenasranked':
        m = 'arenasRanked'
      case _: 
        m = 'battle_royale'
    embed = await get_map_rotation_embed(m)

    view = MapRotationEmbedView(m, m)
    await ctx.respond(embed=embed, view=view)
    client.add_view(view)
    
  @client.command(description="Shows qp cat")
  async def apexcat(ctx):
    data = get_map_rotation_info()
    mapInfo = f"{data['next']['map']}%20in%20{data['current']['remainingMins']}%20minutes"
    await ctx.respond(f"https://cataas.com/cat/says/{mapInfo}")
  
  client.run(os.getenv('DC_API_KEY'))

if __name__ == '__main__':
  load_dotenv()
  
  main_func()