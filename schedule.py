import requests
import tablib
import re
from bs4 import BeautifulSoup
from urlparse import urlparse

data = tablib.Dataset()

data.headers = ['game date', 'away', 'home', 'game time', 'espn id']

root_url = 'http://scores.espn.go.com/nhl/scoreboard?date='

month_schedule = {'jan': {'start': 20130126, 'end': 20130132},
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
    s = soup.find(id=re.compile('awayHeader')).text
    clean_text = s.split()
    away_team = ' '.join(clean_text)
    return away_team

def home(soup):
    s = soup.find(id=re.compile('homeHeader')).text
    clean_text= s.split()
    home_team = ' '.join(clean_text)
    return home_team

def game_time(soup):
    s = soup.find(id=re.compile('statusLine2Left'))
    return s.text

def espn_id(soup):
    links = soup.find(id=re.compile('gameLinks')).find_all('a')
    for link in links:
        if 'conversation' in link['href']:
            text = link['href'].split('=')
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


for month in month_schedule:
    for day in range(month_schedule.get(month).get('start'), month_schedule.get(month).get('end')):
        url = root_url + str(day)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html5lib')
        date = extract_date(soup)
        for x in games_for_day(soup):
            data.append([date, team_names.get(away(x)), team_names.get(home(x)), game_time(x), espn_id(x)])

