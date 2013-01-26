import requests
import tablib
import re
from bs4 import BeautifulSoup
from urlparse import urlparse

data = tablib.Dataset()

data.headers = ['game date', 'away', 'home', 'game time', 'espn id']

root_url = 'http://scores.espn.go.com/nhl/scoreboard?date='

month_schedule = {'jan': {'start': 20130119, 'end': 20130132},
                  'feb': {'start': 20130201, 'end': 20130229},
                  'mar': {'start': 20130301, 'end': 20130333},
                  'apr': {'start': 20130401, 'end': 20130428}}

def games_for_day(soup):
    return soup.find_all(id=re.compile('gamebox'))

def extract_date(soup):
    html = soup.find(class_=re.compile('key-dates'))
    text = html.find('h2').text
    date = text.split()[2:]
    return ' '.join(date)

def away(soup):
    s = soup.find(id=re.compile('awayHeader')).find(class_='team-name').text
    clean_text = s.split()
    away_team = ' '.join(clean_text)
    return away_team

def home(soup):
    s = soup.find(id=re.compile('homeHeader')).find(class_='team-name').text
    clean_text= s.split()
    home_team = ' '.join(clean_text)
    return home_team

def twenty_four_hr_time(text):
    if 'TBD' in text.upper():
        return text
    else:
        time_conversion = {'PM': '12', 'ET': '3', 'AM': '00'}
        split = text.split()
        time = split[0].split(':')
        convert = int(time[0]) + int(time_conversion.get(split[1])) - int(time_conversion.get(split[2]))
        new_time = str(convert) + ":" + time[1]
        return new_time
    
def espn_id_link(soup):
    links = soup.find(id=re.compile('gameLinks')).find_all('a')
    for link in links:
        if 'conversation' in link['href']:
            text = link['href']
    return text
    
def game_time(soup):
    root = 'http://scores.espn.go.com'
    s = soup.find(id=re.compile('statusLine2Left'))
    if 'Highlights' in s.text or not s.text:
        url = root + espn_id_link(soup)
        r = requests.get(url)
        soup1 = BeautifulSoup(r.text)
        time = soup1.find(class_='game-time-location').text
        convert_time = twenty_four_hr_time(time.split(',')[0])
        # go to next page and get start time
        return convert_time
    else:
        return twenty_four_hr_time(s.text)

def espn_id(soup):
    text = espn_id_link(soup).split('=')
    espn_id = text[-1]
    return espn_id
                  
team_names = {'Devils': 'NJD', 'Blackhawks': 'CHI', 'Islanders': 'NYI', 
              'Blue Jackets': 'CBJ', 'Rangers': 'NYR', 'Red Wings': 'DET', 
              'Flyers': 'PHI', 'Predators':'NSH', 'Penguins': 'PIT',
              'Blues': 'STL', 'Bruins': 'BOS',  'Sabres': 'BUF',
              'Avalanche': 'COL', 'Canadiens': 'MTL', 'Oilers': 'EDM', 
              'Senators': 'OTT', 'Wild': 'MIN', 'Maple Leafs': 'TOR', 
              'Canucks': 'VAN', 'Hurricanes': 'CAR', 'Ducks': 'ANA', 
              'Panthers': 'FLA', 'Stars': 'DAL', 'Lightning': 'TBL', 
              'Kings': 'LAK', 'Capitals': 'WSH', 'Coyotes': 'PHX', 
              'Jets': 'WPG', 'Sharks': 'SJS', 'Flames': 'CGY'}


def make_schedule():
    # Will make nhl schedule for games to be played
    for month in month_schedule:
        for day in range(month_schedule.get(month).get('start'), month_schedule.get(month).get('end')):
            url = root_url + str(day)
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html5lib')
            for x in games_for_day(soup):
                data.append([str(day), team_names.get(away(x)), team_names.get(home(x)), game_time(x), espn_id(x)])

