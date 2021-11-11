from bs4 import BeautifulSoup
import os
import json
import requests

def get_avaliable_years(soup, num_years=3):
    options = soup.find(id="ddl_past_rosters").text.replace("  ", "").replace("\r", "").split('\n')
    options = [option for option in options if option][:num_years]
    return [year.split(" ")[0] for year in options]

def get_athlete_data(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    res = soup.find('script', type='application/ld+json')
    return json.loads(res.contents[0])

def get_profile_soup(sport, name, id):
    profile_url = 'https://gocolumbialions.com/sports/{}/roster/{}/{}'.format(sport, name.lower().replace(' ', '-'), id)
    athlete_page = requests.get(profile_url)
    return BeautifulSoup(athlete_page.content, 'html.parser')
    
def get_athlete_player_fields(soup):
    # find player field section and get field data
    player_fields = soup.find("div", class_="sidearm-roster-player-fields")
    if player_fields is None:
        return None
    return player_fields.find_all("li")

def get_athlete_active_years(current_year, soup):
    player_active_years = soup.find_all("span", class_="sidearm-roster-player-first-name")
    years = [year.text for year in player_active_years]
    return years if len(years) > 0 else [current_year]

def get_roster_data(sport, specified_year=None):
    URL = 'https://gocolumbialions.com/sports/{}/roster'.format(sport)
    page = requests.get(URL)
    
    # get page content in soup object
    soup = BeautifulSoup(page.content, 'html.parser')
    years = get_avaliable_years(soup) if not specified_year else [specified_year]
    athletes_info = []
    seen_names = {}
    
    for year in years:
        # get url of each year/season
        year_data_url = '{}/{}'.format(URL, year)
        athletes = get_athlete_data(year_data_url)

        for athlete in athletes['item']:
            # make sure we aren't repeating players
            if athlete['name'] not in seen_names:
                athlete_info = {
                    "name": athlete['name'],
                    "gender": athlete['gender'],
                    "id": int(athlete['url'].split("=")[1])
                }

                # add in player fields from their profile page
                if athlete['url']:
                    profile_soup = get_profile_soup(sport, athlete_info['name'], athlete_info['id'])
                    athlete_info["active_years"] = get_athlete_active_years(year, profile_soup)
                    player_fields = get_athlete_player_fields(profile_soup)
                    if player_fields:
                        for field in player_fields:
                            athlete_info[field.find("dt").text.lower()] = field.find("dd").text.lower()

                # add image if avaliable
                if athlete['image']:
                    athlete_info['image_url'] = athlete['image']['url']
                    
                athletes_info.append(athlete_info)
                seen_names[athlete_info['name']] = 1
                
    return athletes_info
    

def get_years(soup, num_years=3):
    #starts at 2022 -- is that ok?
    options = soup.find(id="sidearm-schedule-select-season").text.replace("  ", "").replace("\r", "").split('\n')
    options = [option for option in options if option][:num_years]
    return [year.split(" ")[0] for year in options]

def clean_text(s):
    if s==None: return(None)
    s = s.replace('\n', "").replace('\r', "").strip()
    words = s.split(" ")
    result = ""
    notFirst = False
    # remove everything after and including 'on'
    for word in words:
        if word!="on":
            if notFirst:
                result+=" "
            result+=word
            notFirst = True
        else:
            break
    return(result)

def get_games(url, year):
    # info included: Year, Opponent, Date, Home/Away, Location, Result
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    games = soup.find_all('li', class_="sidearm-schedule-game")
    games_in_year = []
    for game in games:
        game_info = {"Year": year}
        # opponent
        opp = game.find('div', class_="sidearm-schedule-game-opponent-name")
        if opp!=None:
            a = opp.find("a")
            if a!=None:
                game_info["Opponent/Event"] = clean_text(a["aria-label"])
            else:
                game_info["Opponent/Event"] = clean_text(opp.text)
        else:
            game_info["Opponent/Event"] = ""
        # date
        date = game.find('div', class_="sidearm-schedule-game-opponent-date")
        game_info["Date"] = date.find("span").text if date!=None else ""
        # home or away
        vs_at = game.find('span', class_="sidearm-schedule-game-conference-vs")
        if vs_at!=None:
            found = False
            a = vs_at.find('span', class_="sidearm-schedule-game-away")
            if a!=None:
                game_info["Home/Away"] = "Away"
                found = True
            a = vs_at.find('span', class_="sidearm-schedule-game-home")
            if a!=None:
                game_info["Home/Away"] = "Home"
                found = True
            if not found:
                game_info["Home/Away"] = ""
        else:
            game_info["Home/Away"] = ""
        # location
        location = game.find('div', class_="sidearm-schedule-game-location")
        game_info["Location"] = location.find("span").text if location!=None else ""
        # result
        result = game.find('div', class_="sidearm-schedule-game-result")
        if result!=None:   
            result_line = ""
            for line in result.find_all('span'):
                if(line.text!=None):
                    result_line += line.text
            game_info["Result"] = result_line
        else:
            game_info["Result"] = ""
        games_in_year.append(game_info)
    return games_in_year

def get_schedule_data(sport, specified_year=None):
    URL = 'https://gocolumbialions.com/sports/{}/schedule/'.format(sport)
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    years = get_years(soup) if not specified_year else [specified_year]
    all_games = []
    for year in years:
        games = get_games('https://gocolumbialions.com/sports/{}/schedule/{}'.format(sport, year), year)
        all_games+=games
    return all_games


def get_table_headers(table):
    """Given a table soup, returns all the headers"""
    headers = []
    if(table.find("thead")):
        for row in table.find("thead").find_all("tr"):
            for th in row.find_all("th"):
                headers.append(th.text.strip().split("\n")[0])
    return headers
def get_team_stats(sport, specified_year=None):
    table_captions = []
    URL = 'https://gocolumbialions.com/sports/{}/stats'.format(sport)
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    tables = soup.findAll("table")
    all_table_stats = {}
    captions = soup.findAll("caption")
    table_captions = [caption.text for caption in captions]
    for table in tables:
        table_caption = table.find("caption").text
        if table_caption in table_captions:
            table_stats = {}
            headers = get_table_headers(table)
            current_header = ""
            is_game = False
            if "Game-By-Game" or "Game By Game" in table_caption:
                is_game = True
            for table_row in table.findAll('tr'):
                columns = table_row.findAll('td')
                sub_header = ""           
                if is_game:
                    sub_header = columns[0].text.strip() if len(columns) > 0 else table_row.find("th").text.strip().split("\n")[0] 
                else:
                    sub_header = table_row.find("th").text.strip().split("\n")[0] 
                
                if len(columns) == 0:
                    current_header = sub_header
                else:
                    if current_header not in table_stats:
                        table_stats[current_header] = {}
                    table_stats[current_header][sub_header] = {}
                    if "High" in table_caption or "Low" in table_caption:
                        if columns[1].text not in table_stats:
                            table_stats[columns[1].text] = {}
                        table_stats[columns[1].text][current_header] = columns[0].text
                    else:
                        for i in range(len(columns)):
                            header_index = i if is_game else i + 1
                            if header_index >= len(headers):
                                break
                            table_stats[current_header][sub_header][headers[header_index]] = columns[i].text.strip().replace("\r\n", "")
            all_table_stats[table_caption] = table_stats
    return(all_table_stats)