import discord


'''
Input list
Returns embed message 
'''
def command(list):
  message = ''
  for command in list:
    message += command + '\n'
  embedVar = discord.Embed(title='Billy the Bot', description='The bot that can do it all.(Now Retired)', color=0xdbff29)
  embedVar.add_field(name="Commands", value=message, inline=False)
  return embedVar