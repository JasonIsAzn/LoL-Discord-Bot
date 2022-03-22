import requests
import os
import datetime
import time
import dateutil.relativedelta
from PIL import Image
import json
from replit import db
from bs4 import BeautifulSoup



API_KEY = os.getenv('league_apikey')
url = 'https://ddragon.leagueoflegends.com/api/versions.json'
request = requests.get(url).text
soup = BeautifulSoup(request, features='lxml').text
version = soup.split(',')[0][2:-1]

def process_timer(num, functionName):
    '''
    IN: INT NUMBER, STRING FUNCTION Name
    OUT: NONE
    DESC: PRINTION FUNCTION PROCESS TIME IN SECONDS
    '''
    if num >= 0.05:
        print(str(round((num), 2)) + 's', functionName)
def summonerinfo(name):
    '''
    IN: STRING SUMMONER NAME
    OUT TUPLE OF SUMMONER DATA
    DESC: SUMMMONER ID, ACCOUNT ID, PUUID, SUMMONER NAME, PROFILE ID, LEVEL, REVISION DATE
    '''
    start = time.process_time()
    url = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + name + '?api_key=' + API_KEY
    request = requests.get(url)
    if request.status_code != 200:
        print('STATUS CODE: ' + str(request.status_code))
        return False, 'Error: Invalid Summoner Name'
    summoner_id = request.json()['id']
    account_id = request.json()['accountId']
    puuid = request.json()['puuid']
    summoner_name = request.json()['name']
    profile_id = request.json()['profileIconId']
    level = request.json()['summonerLevel']
    epoch_time = request.json()['revisionDate']
    human_time = datetime.datetime.fromtimestamp(
        epoch_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
    process_timer(time.process_time() - start, 'summonerinfo()')
    return summoner_id, account_id, puuid, summoner_name, profile_id, level, human_time
def IdToName(Id):
    '''
    IN: STRING CHAMPION ID
    OUT: TUPLE OF CHAMPION INFO
    DESC: CHAMPIONID, NAME, ROLE, TITLE
    '''
    global version
    start = time.process_time()
    url = 'http://ddragon.leagueoflegends.com/cdn/' + version + '/data/en_US/champion.json'
    request = requests.get(url)
    file = open('championIdToName.txt', 'r')
    outdated = False
    if file.readline().strip() == version:
        pass
    else:
        outdated = True
    if outdated:
        file = open('championIdToName.txt', 'w')
        file.write(version + '\n')
        string_format = '{}, {}, {}, {}\n'
        for i in request.json()['data']:
            name = request.json()['data'][i]['name']
            title = request.json()['data'][i]['title']
            role = request.json()['data'][i]['tags']
            championId = request.json()['data'][i]['key']
            file.write(string_format.format(championId, name, role, title))
        file.close()
    file = open('championIdToName.txt', 'r')
    for item in file:
        champion_info = item.split(', ')
        if champion_info[0] == Id:
            process_timer(time.process_time() - start, 'IdToName()')
            return champion_info
def all_mastery(name):
    time.sleep(5)
    '''
    IN: STRING SUMMONER NAME
    OUT: DICTIONARY OF MASTERY CHAMPIONS
    ETC: LEVEL, POINTS, CHEST, CHAMPION NAME
    '''
    start = time.process_time()
    summonerID = summonerinfo(name)[0]
    if 'all_masteryData' not in db:
        db['all_masteryData'] = {}
    all_masteryData = db['all_masteryData']
    exist = False
    for item in all_masteryData:
        if item == name:
            exist = True
    if exist:
        mastery_list = all_masteryData[name]
    else:
        if summonerID == False:
            return False, 'Error: Invalid Summoner Name'
        url = 'https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/' + summonerID + '?api_key=' + API_KEY
        time.sleep(5)
        request = requests.get(url)
        mastery_list = []
        if request.json()[0]['championLevel'] >= 5:
            for item in request.json():
                if item['championLevel'] >= 5:
                    mastery_list.append([item['championLevel'], item['championPoints'],item['chestGranted'],IdToName(str(item['championId']))[1], item['tokensEarned']])
                else:
                    break
        else:
            for index, item in enumerate(request.json()):
                if index + 1 <= 3:
                    mastery_list.append([item['championLevel'], item['championPoints'],item['chestGranted'],IdToName(str(item['championId']))[1], item['tokensEarned']])
        if len(mastery_list) < 10:
            for item in request.json():
                if item['championLevel'] <= 4 and len(mastery_list) < 10:
                    if [item['championLevel'], item['championPoints'],item['chestGranted'], IdToName(str(item['championId']))[1],item['tokensEarned']] not in mastery_list:
                        mastery_list.append([item['championLevel'], item['championPoints'],item['chestGranted'],IdToName(str(item['championId']))[1],item['tokensEarned']])
                elif len(mastery_list) > 10:
                    break
        all_masteryData[name] = mastery_list
        db['all_masteryData'] = all_masteryData
    process_timer(time.process_time() - start, 'all_mastery()')
    return mastery_list
def total_mastery(name):
    '''
    IN: STRING SUMMONER NAME
    OUT: INT MASTERY NUMBER
    '''
    start = time.process_time()
    summonerID = summonerinfo(name)[0]
    if summonerID == False:
        return False, 'Error: Invalid Summoner Name'
    url = 'https://na1.api.riotgames.com/lol/champion-mastery/v4/scores/by-summoner/' + summonerID + '?api_key=' + API_KEY
    request = requests.get(url)
    mastery = int(request.text)
    process_timer(time.process_time() - start, 'total_mastery()')
    return mastery
def rotational_champion():
    '''
    OUT: LIST OF FREE CHAMPION
    DESC: ELEMENT IN LIST ALSO CONTAINS CHAMPIONID, NAME, ROLE, TITLE
    '''
    start = time.process_time()
    url = 'https://na1.api.riotgames.com/lol/platform/v3/champion-rotations?api_key=' + API_KEY
    request = requests.get(url)
    champion_list = []
    for item in request.json()['freeChampionIds']:
        champion_list.append(IdToName(str(item)))
    process_timer(time.process_time() - start, 'rotational_champion()')
    return champion_list
def rank_info(name):
    '''
    IN: STRING SUMMONER NAME
    OUT: RANK INFO
    DESC: NEED TO LOOK AT MORE (FLEX) DATA. TIER, RANK, LP, WINS, LOSSES, WINRATE, LEAGUENAME
    '''
    start = time.process_time()
    summonerID = summonerinfo(name)[0]
    if summonerID == False:
        return False, 'Error: Invalid Summoner Name'
    url = 'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/' + summonerID + '?api_key=' + API_KEY
    request = requests.get(url)
    if request.json() == []:
        process_timer(time.process_time() - start, 'rank_info()')
        return 'Unranked'
    elif request.json()[0]['queueType'] == 'RANKED_SOLO_5x5':
        tier = request.json()[0]['tier']
        rank = request.json()[0]['rank']
        name = request.json()[0]['summonerName']
        leaguePoints = request.json()[0]['leaguePoints']
        wins = request.json()[0]['wins']
        losses = request.json()[0]['losses']
        winrate = wins / (wins + losses)
        leagueName = request.json()[0]['leagueId']
        process_timer(time.process_time() - start, 'rank_info()')
        return tier, rank, leaguePoints, wins, losses, winrate, leagueName
    else:
        process_timer(time.process_time() - start, 'rank_info()')
        return 'Unranked'
def gameIdToType(id):
    '''
    IN: INT GAME ID
    OUT: STRING GAME TYPE
    '''
    start = time.process_time()
    file = open('queues.json', 'r')
    data = json.load(file)
    file.close()
    for item in data:
        if item['queueId'] == id:
            description = item['description']
            break
    process_timer(time.process_time() - start, 'gameIdToType()')
    return description
def match_More_Info(name, matchId):
    '''
    IN: INT MATCH ID, STRING SUMMONER NAME
    OUT INFO ABOUT MATCH
    DESC: KDA, TOTAL KILLS, SCORE, CS, PARTICIPANTS LIST, ITEMS ID, CHAMPIONS LIST
    '''
    start = time.process_time()
    if 'match_infoData' not in db:
        db['match_infoData'] = {}
    match_infoData = db['match_infoData']
    exist = False
    for item in match_infoData:
        if item == name + str(matchId):
            exist = True
    if exist:
        info = match_infoData[name + str(matchId)]
    else:
        summonerName = summonerinfo(name)[3]
        url = 'https://na1.api.riotgames.com/lol/match/v4/matches/' + str(matchId) + '?api_key=' + API_KEY
        request = requests.get(url)
        participants = []
        for item in request.json()['participantIdentities']:
            if item['player']['summonerName'] == summonerName:
                participantId = item['participantId']
            participants.append(item['player']['summonerName'])
        total_kills = 0
        for index, item in enumerate(request.json()['participants']):
            if index + 1 == participantId:
                score = item['stats']['win']
                kill = item['stats']['kills']
                death = item['stats']['deaths']
                assist = item['stats']['assists']
                kda = '{}/{}/{}'.format(kill, death, assist)
                cs_score = item['stats']['totalMinionsKilled'] + item['stats'][
                    'neutralMinionsKilled']
                items = [item['stats']['item0'], item['stats']['item1'],item['stats']['item2'], item['stats']['item3'],item['stats']['item4'], item['stats']['item5']]
            if participantId <= 5 and index <= 4:
                total_kills += item['stats']['kills']
            elif participantId >= 6 and index >= 5:
                total_kills += item['stats']['kills']
        info = kda, total_kills, score, cs_score, participants, items
        match_infoData[name + str(matchId)] = info
        db['match_infoData'] = match_infoData
    process_timer(time.process_time() - start, 'match_More_Info()')
    return info
def match_history(name, number, game_type='total'):
    '''
    IN: STRING SUMMONER NAME, STRING NUMBER, OPTIONAL STRING GAME TYPE
    OUT LIST OF LIST OF MATCH HISTORY DATA
    DESC: GAMEID, QUEUE, TIMESTAMP, CHAMPION, LANE, LANE2
    '''
    start = time.process_time()
    if 'match_historyData' not in db:
        db['match_historyData'] = {}
    match_historyData = db['match_historyData']
    exist = False
    for item in match_historyData:
        if item == name + number + game_type:
            exist = True
    if exist:
        match_history = match_historyData[name + number + game_type]
    else:
        accountID = summonerinfo(name)[1]
        if accountID == False:
            return False, 'Error: Invalid Summoner Name'
        if game_type == 'total':
            url = 'https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + accountID + '?endIndex=' + number + '&api_key=' + API_KEY
        elif game_type == 'ranked':
            url = 'https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + accountID + '?queue=420&endIndex=' + number + '&api_key=' + API_KEY
        elif game_type == 'normals':
            url = 'https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + accountID + '?queue=400&endIndex=' + number + '&api_key=' + API_KEY
        elif game_type == 'normals/ranked':
            url = 'https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + accountID + '?queue=420&queue=400&endIndex=' + number + '&api_key=' + API_KEY
        else:
            return False, 'Invalid Game Type'
        request = requests.get(url)
        match_history = []
        for item in request.json()['matches']:
            gameId = item['gameId']
            champion = IdToName(str(item['champion']))[1]
            lane = item['lane']
            lane2 = item['role']
            queue = gameIdToType(item['queue'])
            timestamp = datetime.datetime.fromtimestamp(item['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            match_history.append([gameId, queue, timestamp, champion, lane, lane2])
        match_historyData[name + number + game_type] = match_history
        db['match_historyData'] = match_historyData
    process_timer(time.process_time() - start, 'match_history()')
    return match_history
def live_match(name):
    '''
    IN: STRING SUMMONER NAME
    OUT: LIST OF SUMMONER INFO AND GAME LENGTH
    DESC: SUMMONERS, GAME LENGTH, GAMETYPE
    '''
    start = time.process_time()
    summonerID = summonerinfo(name)[0]
    if summonerID == False:
        return False, 'Error: Invalid Summoner Name'
    url = 'https://na1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/' + summonerID + '?api_key=' + API_KEY
    request = requests.get(url)
    if request.status_code != 200:
        return False, 'Error: Summoner Not In Game'
    current_time = datetime.datetime.fromtimestamp(time.time())
    start_time = datetime.datetime.fromtimestamp(
        request.json()['gameStartTime'] / 1000)
    rd = dateutil.relativedelta.relativedelta(current_time, start_time)
    game_length = '{:0>2d}:{:0>2d}:{:0>2d}'.format(rd.hours, rd.minutes, rd.seconds)
    gameType = gameIdToType(request.json()['gameQueueConfigId'])
    summoners = []
    for item in request.json()['participants']:
        summonerName = item['summonerName']
        profileIcon = item['profileIconId']
        champion = IdToName(str(item['championId']))
        summoners.append([summonerName, profileIcon, champion])
    process_timer(time.process_time() - start, 'live_match()')
    return summoners, game_length, gameType
def most_played_role(name):
    '''
    IN: STRING SUMMONER NAME
    OUT LIST WITH ELEMENT OF 1 OR 2
    DESC: ELEMENT CONTAIN PRIMARY AND/OR SECONDARY ROLE
    '''
    start = time.process_time()
    matches_data = match_history(name, '20', 'normals/ranked')
    roles = []
    for index, item in enumerate(matches_data):
        if matches_data[index][4] == 'NONE':
            pass
        elif matches_data[index][5] == 'DUO_SUPPORT':
            roles.append('Support')
        elif matches_data[index][5] == 'DUO_CARRY':
            roles.append('AD Carry')
        else:
            roles.append(matches_data[index][4])
    if len(set(roles)) == 1:
        process_timer(time.process_time() - start, 'most_played_role()')
        return [roles[0].capitalize()]
    else:
        roles_set = list(set(roles))
        role_count = []
        for i in roles_set:
            matches_played = 0
            for j in roles:
                if i == j:
                    matches_played += 1
            role_count.append(matches_played)
        role_index = role_count[:]
        role_count.sort(reverse=True)
        primary = roles_set[role_index.index(role_count[0])].capitalize()
        secondary = roles_set[role_index.index(role_count[1])].capitalize()
        process_timer(time.process_time() - start, 'most_played_role()')
        return [primary, secondary]
def most_played_champion(name):
    '''
    IN: STRING SUMMONER NAME 
    OUT: LIST WITH ELEMENT OF 1 OR 2
    DESC: ELEMENT CONTAIN FIRST, SECOND, AND/OR THIRD MAIN MOST PLAYED CHAMPION
    '''
    start = time.process_time()
    matches_data = match_history(name, '20', 'normals/ranked')
    champions = []
    for index, item in enumerate(matches_data):
        champions.append(matches_data[index][3])
    if len(set(champions)) == 1:
        process_timer(time.process_time() - start, 'most_played_champion()')
        return [champions[0]]
    else:
        champions_set = list(set(champions))
        champion_count = []
        for i in champions_set:
            matches_played = 0
            for j in champions:
                if i == j:
                    matches_played += 1
            champion_count.append(matches_played)
        champion_index = champion_count[:]
        champion_count.sort(reverse=True)
        first = champions_set[champion_index.index(champion_count[0])]
        second = champions_set[champion_index.index(champion_count[1])]
        try:
            third = champions_set[champion_index.index(champion_count[2])]
            process_timer(time.process_time() - start,
                          'most_played_champion()')
            return list(set([first, second, third]))
        except IndexError:
            pass
        process_timer(time.process_time() - start, 'most_played_champion()')
        return list(set([first, second]))
def edit_image(url, imageName, width):
    '''
    IN: STRING URL OF IMAGE, STRING FILE NAME, INT WIDTH SIZE
    OUT: CREATE IMAGES FILE
    '''
    global version
    start = time.process_time()
    image = requests.get(url)
    file = open(imageName, 'wb')
    file.write(image.content)
    file.close()
    basewidth = width
    img = Image.open(imageName)
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    img.save(imageName)
    process_timer(time.process_time() - start, 'edit_image()')
def concat_h2(im1, im2):
    start = time.process_time()
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    process_timer(time.process_time() - start, 'concat_h2()')
    return dst
def concat_h3(im1, im2, im3):
    '''
    IN: THREE IMAGE VARIBLES 
    CREATE IMAGE FILE 
    DESC: CONCATENTATION OF THREE IMAGES THAT ARE THE SAME SIZE HORIZONTALLY
    '''
    start = time.process_time()
    dst = Image.new('RGB', (im1.width + im2.width + im3.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    dst.paste(im3, (im1.width + im2.width, 0))
    process_timer(time.process_time() - start, 'concat_h3()')
    return dst
def concat_v(im1, im2):
    '''
    IN: TWO IMAGE VARIBLES 
    CREATE IMAGE FILE 
    DESC: CONCATENTATION OF TWO IMAGES VERTICALLY
    '''
    global version
    start = time.process_time()
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    process_timer(time.process_time() - start, 'concat_v()')
    return dst
def make_image_item(summonerName, gameId, items):
    '''
    IN: STRING SUMMONER NAME, INT GAMEID, LIST OF ITEMS ID
    CREATES IMAGE FILE
    DESC: COMBINE SIX IMAGES TOGETHER 
    '''
    start = time.process_time()
    url = 'http://ddragon.leagueoflegends.com/cdn/' + version + '/img/item/'
    for index, item in enumerate(items):
        if item == 0:
            Image.new('RGB', (40, 40)).save('item' + str(index) + '.png')
        else:
            edit_image(url + str(item) + '.png', 'item' + str(index) + '.png',
                       40)
    item0 = Image.open('item0.png')
    item1 = Image.open('item1.png')
    item2 = Image.open('item2.png')
    item3 = Image.open('item3.png')
    item4 = Image.open('item4.png')
    item5 = Image.open('item5.png')
    concat_h3(item0, item1, item2).save('row1.png')
    concat_h3(item3, item4, item5).save('row2.png')
    row1 = Image.open('row1.png')
    row2 = Image.open('row2.png')
    concat_v(row1, row2).save('item_image.png')
    for index in range(0, 6):
        os.remove('item' + str(index) + '.png')
    os.remove('row1.png')
    os.remove('row2.png')
    process_timer(time.process_time() - start, 'make_item_image()')
def make_image_profile(summonerName):
    '''
    IN: STRING SUMMONER NAME
    CREATE IMAGE PROFILE FILE
    '''
    global version
    start = time.process_time()
    imageId = summonerinfo(summonerName)[4]
    edit_image(
        'http://ddragon.leagueoflegends.com/cdn/' + version + '/img/profileicon/' +
        str(imageId) + '.png', 'ProfileIcon.png', 100)
    process_timer(time.process_time() - start, 'make_image_profile')
def league_Name(leagueId):
    '''
    IN STRING LEAGUE ID
    OUT LEAGUENAME 
    '''
    url = 'https://na1.api.riotgames.com/lol/league/v4/leagues/' + leagueId + '?api_key=' + API_KEY
    request = requests.get(url)
    leagueName = request.json()['name']
    return leagueName
def check_API():
    '''
    CHECK API BY USING A BASE URL 
    PRINTS STATUS CODE
    403 - OUTDATE API
    200 - WORKING
    '''
    url = 'https://na1.api.riotgames.com/lol/status/v3/shard-data?api_key=' + API_KEY
    request = requests.get(url)
    status = request.status_code
    print('Status Code:', status)
def save_Data(key, index):
  if 'saved_data' not in db:
      db['saved_data'] = [[],[],[]]
  saved_Data = db['saved_data']
  if key not in saved_Data[index]:
    saved_Data[index].append(key)
  db['saved_data'] = saved_Data
### Main Functions ###
def profile_command(summonerName, image=True):
    global version
    #general data used
    start = time.process_time()
    summoner_info = summonerinfo(summonerName)
    if not summoner_info[0]:
        return summoner_info
    if 'profileData' not in db:
        db['profileData'] = {}
    profileData = db['profileData']
    exist = False
    for item in profileData:
        if item == summonerName:
            exist = True
    if exist:
        message = profileData[summonerName]
    else:
        top_mastery = all_mastery(summonerName)[0:3]
        ranked = rank_info(summonerName)
        top_champions = most_played_champion(summonerName)
        #specific data used
        name = summoner_info[3]
        level = summoner_info[5]
        role = most_played_role(summonerName)
        primary_role = role[0]
        second_role = False
        try:
            second_role = role[1]
        except IndexError:
            pass
        ##formatting message
        #General Summoner Information
        message = '```'
        info_format = '\nSummoner: {}\nLevel: {}\nPrimary Role: {}'
        message += info_format.format(name, level, primary_role)
        if second_role:
            message += '\nSecondary Role: ' + second_role + '\n'
        message += '```'
        #Summoner Ranked Information
        if ranked != 'Unranked':
            message += '```'
            leagueId = ranked[6]
            leagueName = league_Name(leagueId)
            rank = ranked[0].capitalize() + ' ' + ranked[1] + '  ' + leagueName
            rank1 = str(ranked[3]) + 'W ' + str(ranked[4]) + 'L ' + str(
                ranked[2]) + ' LP'
            winratio = round(ranked[5] * 100)
            ranked_format = '\nRank:\n{}\n{}\n{}% WinRatio\n'
            message += ranked_format.format(rank, rank1, winratio)
            message += '```'
        #Summoner Champion Information
        message += '```'
        table_format1 = '{:<15}{:<15}\n'
        table_format2 = '{:<15}\n'
        message += table_format1.format('Top Mastery', 'Most Recently Played')
        message += '-' * 11 + ' ' * 4 + '-' * 24 + '\n'
        for index in range(0, 3):
            try:
                message += table_format1.format(top_mastery[index][3], top_champions[index])
            except IndexError:
                message += table_format2.format(top_mastery[index][3])
            except:
                pass
        message += '```'
        profileData[summonerName] = message
        db['profileData'] = profileData
        save_Data(summonerName, 0)
    #getting images and editting them
    if image:
        top_mastery = all_mastery(summonerName)[0:3]
        imageId = summoner_info[4]
        champion =  top_mastery[0][3].replace(' ', '')
        if champion == "Nunu&Willump":
          champion = "Nunu"
        profile_url = 'http://ddragon.leagueoflegends.com/cdn/' + version + '/img/profileicon/' + str(imageId) + '.png'
        champion_url = 'http://ddragon.leagueoflegends.com/cdn/' + version + '/img/champion/' + champion + '.png'
        edit_image(profile_url, 'ProfileIcon.png', 100)
        edit_image(champion_url, 'ChampionIcon.png', 100)
        img1 = Image.open('ProfileIcon.png')
        img2 = Image.open('ChampionIcon.png')
        concat_h2(img1, img2).save('combined.png')
    #Returning Message
    process_timer(time.process_time() - start, 'profile_command() FINAL\n')
    return message
def mastery_command(summonerName, image=True):
    start = time.process_time()
    if 'masteryData' not in db:
        db['masteryData'] = {}
    masteryData = db['masteryData']
    exist = False
    for item in masteryData:
        if item == summonerName:
            exist = True
    if exist:
        message = masteryData[summonerName]
    else:
        print("here", summonerinfo(summonerName))
        summoner_name = summonerinfo(summonerName)[3]
        totalMastery = total_mastery(summonerName)
        masteries = all_mastery(summonerName)
        format_string = '{:<5}{:<15}{:<10}{:<12}{:<5}\n'
        message = '```' + summoner_name + ' Total Mastery: ' + str(
            totalMastery) + '\n'
        message += '-' * len(message) + '\n'
        message += format_string.format('Lvl', 'Champion', 'Points',
                                        'Progress', 'Earned')
        for index in range(0, 4):
            for item in masteries:
                chest = 'X'
                if item[2] == True:
                    chest = 'Earned'
                if item[0] == 7 and index == 0:
                    message += format_string.format(item[0], item[3],
                                                    "{:,}".format(item[1]),
                                                    'Mastered', chest)
                elif item[0] == 6 and index == 1:
                    message += format_string.format(item[0], item[3],
                                                    "{:,}".format(item[1]),
                                                    str(item[4]) + '/3', chest)
                elif item[0] == 5 and index == 2:
                    message += format_string.format(item[0], item[3],
                                                    "{:,}".format(item[1]),
                                                    str(item[4]) + '/2', chest)
                elif item[0] <= 4 and index == 3:
                    message += format_string.format(item[0], item[3],
                                                    "{:,}".format(item[1]),
                                                    'No Tokens', chest)
        message += '```'
        masteryData[summonerName] = message
        db['masteryData'] = masteryData
        save_Data(summonerName, 1)
    if image:
      make_image_profile(summonerName)
    process_timer(time.process_time() - start, 'mastery_command() FINAL\n')
    return message
def history_command(summonerName, gameType, index, image=True):
    start = time.process_time()
    if 'historyData' not in db:
        db['historyData'] = {}
    historyData = db['historyData']
    exist = False
    for item in historyData:
        if item == summonerName + '/' +gameType + '/' + str(index):
            exist = True
    matchHistory = match_history(summonerName, '3', gameType)[index]
    matchId = matchHistory[0]
    matchInfo = match_More_Info(summonerName, matchId)
    items = matchInfo[5]
    if exist:
        message = historyData[summonerName + '/' +gameType + '/' + str(index)]
    else:
        queue = matchHistory[1]
        match_date = matchHistory[2][5:10]
        champion = matchHistory[3]
        kda = matchInfo[0]
        total_kills = matchInfo[1]
        kill_participation = str(
            round(int(kda.split('/')[0]) + int(kda.split('/')[2]) * 100 / total_kills)) + '%'
        if matchInfo[2]:
            score = 'Victory'
        else:
            score = 'Defeat'
        cs_score = str(matchInfo[3])
        string_format = '{:<25}{:<20}\n'
        message = '```\n'
        message += string_format.format(queue, champion)
        message += string_format.format(score, 'KDA: ' + kda)
        message += string_format.format(' ', 'P/Kill: ' + kill_participation)
        message += string_format.format(match_date, 'CS: ' + cs_score)
        message += '```Items:'
        historyData[summonerName + '/' + gameType + '/' + str(index)] = message
        db['historyData'] = historyData
        save_Data(summonerName + '/' +gameType + '/' + str(index), 2)
    if image:
      make_image_item(summonerName, matchId, items)
    process_timer(time.process_time() - start, 'history_command() FINAL\n')
    return message
def load_Data():
    if 'saved_data' not in db:
      db['saved_data'] = [[],[],[]]
    else:
      saved_Data = db['saved_data']
      profileData = db['profileData']
      masteryData = db['masteryData']
      for item in saved_Data[0]:
        profile_command(item, image=False)
        time.sleep(5)
      for item in saved_Data[1]:
        mastery_command(item, image=False)
        time.sleep(5)
      #for item in saved_Data[2]:
      #  try:
      #    inputs = item.split('/')
      #    history_command(inputs[0],inputs[1],int(inputs[2]), image=False)
      #    time.sleep(3)
      #  except:
      #    continue
    print('Loading Previous Data')
def update():
    '''
    RESET DATABASE
    '''
    db['profileData'] = {}
    db['historyData'] = {}
    db['masteryData'] = {}
    db['all_masteryData'] = {}
    db['match_historyData'] = {}
    load_Data()