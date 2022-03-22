import discord 
from keep_alive import keep_alive
import os
import threading
from replit import db
import time
import requests
import praw
import random
from bs4 import BeautifulSoup

import HelpCommand as HC
import LeagueCommand as LC

client = discord.Client()
headers = {'user-agent': 'Mozilla/5.0 '}

### Functions ###
def hourly_update():
  LC.update()
  print('Resetting League Database')

def test():
  print('test')

### Main ###
@client.event
async def on_ready():
    start = time.process_time()
    await client.change_presence(activity=discord.Game("$help"))
    #LC.update()
    #threading.Timer(43200.0, hourly_update).start() # 12 hours
    LC.check_API()
    LC.process_timer(time.process_time() - start, '')
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    msg = message.content
    if message.author == client.user:
        return
    elif msg.startswith('$test'):
      pass
    elif msg.startswith('$help'):
        help_commands = [
            '$profile <Summoner Name>',
            '$mastery <Summoner Name>',
            '$history <Summoner Name> {Total, Normals, Ranked, Normals/Ranked}',
            '$update',
            '$live <Summoner Name>',
            '$meme list',
            '$anime <season> <year>',
            '$news list',
            '$flashcards help',
            '$mmr <Summoner Name>'
        ]
        embedMessage = HC.command(help_commands)
        await message.channel.send(embed=embedMessage)
    elif msg.startswith('$profile'):
      summonername = msg.split('$profile ', 1)[1].lower()
      #try:
      profile = LC.profile_command(summonername)
      await message.channel.send(file=discord.File('combined.png'))
      await message.channel.send(profile)
      os.remove('ProfileIcon.png')
      os.remove('combined.png')
      os.remove('ChampionIcon.png')
      #except IndexError:
      #  await message.channel.send('Invalid Summoner Name. $profile <SummonerName>')
      #except:
      #  await message.channel.send('Server Side Error. (Update API key?)\n<@382201591429595137>')
    elif msg.startswith('$mastery'):
      try:
        summonername = msg.split('$mastery ', 1)[1].lower()
        masterys = LC.mastery_command(summonername)
        await message.channel.send(file=discord.File('ProfileIcon.png'))
        await message.channel.send(masterys)
        os.remove('ProfileIcon.png')
      except IndexError:
        await message.channel.send('Invalid Summoner Name. $mastery <SummonerName>')
      except:
        await message.channel.send('Server Side Error. (Update API key?)\n<@382201591429595137>')
    elif msg.startswith('$history'):
      try:
        summonername = msg.split('$history ', 1)[1].split(' ')[0].lower()
        if len(msg.split('$history ', 1)[1].split(' ')) == 1:
          gameType = 'total'
        else:
          gameType = msg.split('$history ', 1)[1].split(' ')[1].lower()
        for num in range(0,3):
            matches = LC.history_command(summonername, gameType, num)
            await message.channel.send(matches)
            await message.channel.send(file=discord.File('item_image.png'))
            os.remove('item_image.png')
      except KeyError:
        await message.channel.send('Invalid Input. $history <SummonerName>')
      except:
        await message.channel.send('Server Side Error. (Update API key?)\n<@382201591429595137>')
    elif msg.startswith('$update'):
      await message.channel.send('Updating League Data. This may take awhile')
      LC.update()
      await message.channel.send('League Data is now Updated')
    elif msg.startswith('$live'):
        user = msg.split('$live ', 1)[1]
        user_opgg = 'https://na.op.gg/summoner/spectator/userName=' + user
        html_text = requests.get(user_opgg, headers=headers).text
        soup = BeautifulSoup(html_text, features='lxml')
        try:
            summoners = soup.find_all('td', class_="SummonerName Cell")
            ranks = soup.find_all('td', class_="CurrentSeasonTierRank Cell")
            bluetier = soup.find_all(
                'th', class_="HeaderCell MMR")[0].text.strip()
            redtier = soup.find_all(
                'th', class_="HeaderCell MMR")[1].text.strip()
            champions = soup.find_all('td', class_='ChampionImage Cell')
            game_info = soup.find(
                'div', class_='Title').text.split('\n')[0].split('\t')
            map_type = game_info[-1]
            game_type = game_info[0]
            info = ''
            for index in range(0, 10):
                if index == 0:
                    info += game_type + ' ' * 5 + map_type + '\n'
                    info += '**Blue Team **' + bluetier + '\n```'
                string_format = "{:<20}{:<20} {:^10}\n"
                summoner_name = summoners[index].a.text
                rank = ranks[index].div.text.strip()
                champion = champions[index].a['href'].split(
                    '/')[2].capitalize()
                info += string_format.format(champion, summoner_name, rank)
                if index == 4:
                    info += "```\n**Red Team **" + redtier + '\n```'
                if index == 9:
                    info += '```'

            await message.channel.send(info)
        except:
            try:
                user_name = soup.find('div', class_="Information").span.text
                await message.channel.send(user_name + " is not in a game")
            except:
                await message.channel.send("Summoner Does Not Exist")
    elif msg.startswith('$meme'):
        try:
            reddit = praw.Reddit(
                client_id=os.getenv('client_id'),
                client_secret=os.getenv('client_secret'),
                user_agent=os.getenv('user_agent'),
                username=os.getenv('username'),
                password=os.getenv('password'))
            meme_type = msg.split('$meme ', 1)[1]
            meme_subs = [
                'animemes', 'memes', 'wholesomememes', 'dankmemes', 'deepfried'
            ]
            if meme_type in meme_subs:
                extension = ''
                while extension not in ['jpg', 'png']:
                    number = random.randint(0, 50)
                    if meme_type == 'animemes':
                        subred = reddit.subreddit("Animemes").hot(limit=50)
                    elif meme_type == 'memes':
                        subred = reddit.subreddit("memes").hot(limit=50)
                    elif meme_type == 'wholesomememes':
                        subred = reddit.subreddit("wholesomememes").hot(
                            limit=50)
                    elif meme_type == 'dankmemes':
                        subred = reddit.subreddit("dankmemes").hot(limit=50)
                    elif meme_type == 'deepfried':
                        subred = reddit.subreddit("DeepFriedMemes").hot(
                            limit=50)
                    extension = ''
                    for i, j in enumerate(subred):
                        if i == number:
                            meme_url = j.url
                            meme_title = str(j.title)
                            meme_author = str(j.author)
                            break
                    extension = meme_url.split('.')[-1]
                image = requests.get(meme_url)
                file = open('meme.' + extension, 'wb')
                file.write(image.content)
                file.close()
                await message.channel.send('"' + meme_title + '"   -u/' +
                                           meme_author)
                await message.channel.send(
                    file=discord.File('meme.' + extension))
                os.remove('meme.' + extension)
            else:
                await message.channel.send(
                    'Try Typing: \n```$meme animemes\n$meme memes\n$meme wholesomememes\n$meme dankmemes\n$meme deepfried```'
                )
        except:
            await message.channel.send('Invalid Input. Try $meme list')
    elif msg.startswith('$anime'):
        try:
            year = msg.split(' ')[2]
            season = msg.split(' ')[1]
            anime_url = 'https://myanimelist.net/anime/season/' + year + '/' + season
            html_text = requests.get(anime_url, headers=headers).text
            soup = BeautifulSoup(html_text, features='lxml')
            animelist = soup.find_all(
                'div', class_='seasonal-anime js-seasonal-anime')[0:10]

            months = []
            years = []
            for anime in animelist:
                data = anime.find(
                    'div', class_='info').span.text.split('\n')[1].replace(
                        ' ', '').split(',')
                months.append(data[0][0:3])
                years.append(data[1])
            initial_months = set(months)
            initial_years = set(years)
            current_month = years[0]
            current_year = months[0]
            for i in initial_months:
                if months.count(i) > months.count(current_month):
                    current_month = i
            for j in initial_years:
                if years.count(j) > years.count(current_year):
                    current_year = j

            if current_month in ['Oct', 'Nov', 'Dec']:
                current_season = 'Fall'
            elif current_month in ['Jan', 'Feb', 'Mar']:
                current_season = 'Winter'
            elif current_month in ['Apr', 'May', 'Jun']:
                current_season = 'Spring'
            elif current_month in ['Jul', 'Aug', 'Sep']:
                current_season = 'Summer'
            if current_season.lower() == season.lower() and current_year.lower(
            ) == year.lower():
                list_message = ''
                for index, anime in enumerate(animelist):
                    string_format = '{:<10} {:<5}\n'
                    title = anime.find('h2', class_='h2_anime_title').a.text
                    score = anime.find('span', title='Score').text.strip()
                    if index == 0:
                        list_message += string_format.format('Score', 'Title')
                        list_message += '-' * 60 + '\n'
                    list_message += string_format.format(score, title)
                await message.channel.send('```' + list_message + '```')
            else:
                await message.channel.send(
                    'Try Typing: $anime <seasson> <year>\nFor an season that exist.'
                )
        except:
            await message.channel.send(
                'Try Typing: $anime <seasson> <year>\nFor a season that exist.'
            )
    elif msg.startswith('$news'):
        news = msg.split('$news ', 1)[1]
        if news == 'list':
            await message.channel.send(
                'Try Typing:\n```$news league\n$news news```')
        if news[0:6] == 'league':
            url = 'https://na.leagueoflegends.com/en-us/latest-news/'
            html_text = requests.get(url, headers=headers).text
            soup = BeautifulSoup(html_text, features='lxml')
            articles = soup.find_all(
                'li', class_='style__Item-sc-3mnuh-3 ekxbJn')
            if news == 'league':
                articles_message = ''
                format_string = '{:<3} {:<20} {:<20}\n'
                for index, article in enumerate(articles):

                    league_article = article.find(
                        'div', 'style__InfoInner-i44rc3-7 fqltpa')
                    article_type = league_article.div.text
                    article_title = league_article.h2.text
                    if index == 0:
                        articles_message += '```'
                        articles_message += format_string.format(
                            '#', 'Category', 'Article Title')
                        articles_message += '-' * 70 + '\n'
                    articles_message += format_string.format(
                        index + 1, article_type, article_title)
                    if index + 1 == len(articles):
                        articles_message += '```'
                await message.channel.send(
                    articles_message +
                    'Type $news league <number> to get link')
            else:
                try:
                    number = news.split(' ')[1]
                    number = int(number.replace(' ', ''))
                except:
                    number = False
                if number or number == 0:
                    if number > len(articles):
                        await message.channel.send(
                            'Enter a number less than ' + str(len(articles)))
                        number = False
                    elif number <= len(articles) and int(number) > 0:
                        pass
                    else:
                        await message.channel.send(
                            "Enter a number from the list")
                        number = False
                if number:
                    for index, article in enumerate(articles):
                        url = article.a['href']
                        article_url = ''
                        if url[0] == '/':
                            article_url = 'https://na.leagueoflegends.com/' + url
                        else:
                            article_url = url
                        if index + 1 == number:
                            break
                    await message.channel.send(article_url)
        elif news[0:4] == 'news':
            url = 'https://arstechnica.com/'
            html_text = requests.get(url, headers=headers).text
            soup = BeautifulSoup(html_text, features='lxml')
            news_article = soup.find(
                'section', class_="listing listing-top with-feature")
            article1 = news_article.find_all(
                'li', class_='tease article split-feature')
            article2 = news_article.find_all('li', class_='tease article')
            if news == 'news':
                articles_message = ''
                format_string = '{:<3} {:<20}\n'
                articles_message += '```'
                articles_message += format_string.format(
                            '#', 'Article Title')
                articles_message += '-' * 70 + '\n'
                for index, article in enumerate(article1):
                    article_title = article.header.h2.a.text
                    articles_message += format_string.format(index + 1, article_title)
                for index, article in enumerate(article2):
                    article_title = article.header.h2.a.text
                    articles_message += format_string.format(
                        index + 1 + len(article1), article_title)
                    if index + 1 == len(article2):
                        articles_message += '```'
                await message.channel.send(
                    articles_message +
                    'Type: $news news <number> to get article link')
            else:
                try:
                    number = news.split(' ')[1]
                    number = int(number.replace(' ', ''))
                except:
                    number = False
                if number or number == 0:
                    if number > len(article1) + len(article2):
                        await message.channel.send(
                            'Enter a number less than ' +
                            str(len(article1) + len(article2)))
                        number = False
                    elif number <= (
                            len(article1) + len(article2)) and int(number) > 0:
                        pass
                    else:
                        await message.channel.send(
                            "Enter a number from the list")
                        number = False
                if number:
                    url = 0
                    for index, article in enumerate(article1):
                        if index + 1 == number:
                            url = article.header.h2.a['href']
                            break
                    if not url:
                        for index, article in enumerate(article2):
                            if index + 1 + len(article1) == number:
                                url = article.header.h2.a['href']
                                break
                    await message.channel.send(url)
    elif msg.startswith('$flashcards'):
        command = msg.split('$flashcards ', 1)[1]
        detail = command.split(' ')
        detail_mod = command.split('"')
        if "flashcards" not in db:
            db["flashcards"] = []
        else:
            pass

        flashcards = db["flashcards"]
        if detail[0] == 'help':
            flashcards_list = []
            await message.channel.send(
                '```$flashcards add <Flashcard Name>\n$flashcards del <index>\n$flashcards list\n$flashcards rename <Old Name> <New Name>\n$flashcards <Flashcard Name> list\n$flashcards <Flashcard Name> <add> "<front>" "<back>"\n$flashcards <Flashcard Name> <del> <index>\n$flashcards <Flashcard Name> random\n$flashcards <FLashcard Name> <Index>```'
            )
        elif detail[0] == 'add':
            exist = False
            for item in flashcards:
                if item['title'] == detail[1]:
                    exist = True
                    break
            if exist:
                await message.channel.send(detail[1] + ' already exist.')
            else:
                await message.channel.send(detail[1] + ' has been created.')
                flashcards.append(dict(title=detail[1]))
            db['flashcards'] = flashcards
        elif detail[0] == 'del':
            try:
                if int(detail[1]) > len(flashcards) or int(detail[1]) <= 0:
                    await message.channel.send(
                        'Enter an Index from the list of flashcards using $flashcards list'
                    )
                else:
                    await message.channel.send(
                        flashcards[int(detail[1]) - 1]['title'] +
                        " Flashcards has been deleted.")
                    del flashcards[int(detail[1]) - 1]
                db['flashcards'] = flashcards
            except:
                await message.channel.send(
                    'Invalid Input. Try $flashcards del <Index>')
        elif detail[0] == 'list':
            if len(flashcards) == 0:
                await message.channel.send("No Flashcards have been created")
            else:
                titlelist = ''
                format_string = '{:<7} {:<10}\n'
                for index, item in enumerate(flashcards):
                    if index == 0:
                        titlelist += '```'
                        titlelist += format_string.format('Index', 'title')
                    titlelist += format_string.format(index + 1, item['title'])

                    if index + 1 == len(flashcards):
                        titlelist += '```'
                await message.channel.send(titlelist)
        elif detail[0] == 'rename':
            try:
                name = detail[1]
                new_name = detail[2]
                for index, item in enumerate(flashcards):
                    if name == item['title']:
                        flashcard = flashcards[index]
                flashcard['title'] = new_name
                db['flashcards'] = flashcards
                await message.channel.send(name + ' has been changed to ' +
                                           new_name)
            except:
                message.channel.send(
                    'Invalid Input. Try $flashcards rename <Old Name> <New Name>'
                )
        else:
            canpass = False
            name = detail[0]
            for index, item in enumerate(flashcards):
                if name == item['title']:
                    flashcard = flashcards[index]
                    canpass = True
            if canpass:
                command = detail[1]
                if command == 'add':
                    try:
                        front = detail_mod[1]
                        back = detail_mod[3]
                        flashcard[len(flashcard)] = [front, back]
                        db["flashcards"] = flashcards
                        await message.channel.send('Card Created')
                    except:
                        await message.channel.send(
                            'Invalid Input. Try: $flashcards <Flashcard Name> add "<front>" "<back>"'
                        )
                elif command == 'del':
                    if int(detail[2]) > len(flashcard) or int(detail[2]) <= 0:
                        await message.channel.send(
                            'Enter an index assigned to the card using $flashcards <Flashcard Name> list'
                        )
                    else:
                        del flashcard[detail[2]]
                        for index, key in enumerate(flashcard):
                            if index == 0:
                                pass
                            else:
                                flashcard[index] = flashcard.pop(key)
                        db["flashcards"] = flashcards
                        await message.channel.send('Card Deleted')
                elif command == 'list':
                    string_format = '{:<7} {:<20}\n'
                    list_message = ''
                    for index, item in enumerate(flashcard):
                        if index == 0:
                            list_message += '```'
                            list_message += string_format.format(
                                'Index', 'Front Card')
                        elif index < len(flashcard):
                            front = str(flashcard[item][0])
                            list_message += string_format.format(item, front)
                        if index + 1 == len(flashcard):
                            list_message += '```'
                    await message.channel.send(list_message)
                elif command == 'random':
                    number = random.randint(1, len(flashcard) - 1)
                    random_message = 'Index: ' + str(
                        number) + '\nFront: ' + flashcard[str(
                            number)][0] + '\nBack: ||' + flashcard[str(
                                number)][1] + '||'
                    await message.channel.send(random_message)
                else:
                    try:
                        number = int(detail[1])
                        index_message = 'Index: ' + str(
                            number) + '\nFront: ' + flashcard[str(
                                number)][0] + '\nBack: ||' + flashcard[str(
                                    number)][1] + '||'
                        await message.channel.send(index_message)
                    except KeyError:
                        await message.channel.send(
                            "Enter an Index of a card using $flashcards <name> list"
                        )
                    except:
                        await message.channel.send(
                            "Invalid Input. Try $flashcards help")

            else:
                await message.channel.send(
                    'Invalid Input. Try $flashcards help')
    elif msg.startswith('$mmr'):
        try:
            user = msg.split('$mmr ', 1)[1]
            json_url = 'https://na.whatismymmr.com/api/v1/summoner?name=' + user
            r_json = requests.get(json_url)
            mmr_data = r_json.json()
            ranked_mmr = mmr_data['ranked']['avg']
            normal_mmr = mmr_data['normal']['avg']
            aram_mmr = mmr_data['ARAM']['avg']
            comment = ''
            try:
                comment1 = mmr_data['ranked']['summary'].split('<b>')
                comment2 = comment1[1].split('</span>')
                comment3 = comment1[2].split('</b>')
                comment = comment2[1] + comment3[0] + comment3[1]
            except:
                pass
            mmr_string = 'League of Legends MMR of ' + user + '\n'
            if type(ranked_mmr) == int:
                mmr_string += 'Ranked MMR: ' + str(ranked_mmr) + '\n'
            if type(normal_mmr) == int:
                mmr_string += 'Normal MMR: ' + str(normal_mmr) + '\n'
            if type(aram_mmr) == int:
                mmr_string += 'Aram MMR: ' + str(aram_mmr) + '\n'
            mmr_string += comment + '\n'
            await message.channel.send(mmr_string)
        except:
            await message.channel.send(
                'Enter a Valid Summoner Name.\n $mmr <Summoner Name>')

keep_alive()
client.run(os.getenv('TOKEN'))
