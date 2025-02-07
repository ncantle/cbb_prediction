import urllib3
import pandas as pd
import string
from datetime import datetime
from bs4 import BeautifulSoup

def get_season_schools(year):
    http = urllib3.PoolManager()
    URL = f'https://www.sports-reference.com/cbb/seasons/men/{year}-school-stats.html'
    r = http.request('GET', URL)
    soup = BeautifulSoup(r.data, 'html.parser')

    filename = 'data_file.txt'
    with open(filename, 'w') as f:
        header = ','.join([item.get_text() for item in soup.select("table[id = 'basic_school_stats'] > thead > tr > th")][12:])
        print(header, file=f)
        for item in soup.select("table[id='basic_school_stats'] > tbody > tr"):
            row_data = ','.join( [ item.get_text() for item in item.select("td") ] )
            print(row_data, file=f)

    df = pd.read_csv(filename)
    cols = df.columns
    df.drop(columns = 'PF', inplace = True)
    df.columns = cols[1:]
    
    df.drop(columns = ['\xa0','\xa0.1','\xa0.2','\xa0.3','\xa0.4'], inplace = True)
    
    column_names = {
        'School':'school',
        'G':'games',
        'W':'wins',
        'L':'losses',
        'W-L%':'win_loss_percent',
        'SRS':'simple_rating_system',
        'SOS':'strength_of_schedule',
        'W.1':'conference_wins',
        'L.1':'conference_losses',
        'W.2':'home_wins',
        'L.2':'home_losses',
        'W.3':'away_wins',
        'L.3':'away_losses',
        'Tm.':'points_for',
        'Opp.':'points_against',
        'MP':'minutes_played',
        'FG':'field_goals',
        'FGA':'field_goals_attempted',
        'FG%':'field_goal_percent',
        '3P':'three_pointers',
        '3PA':'three_pointers_attempted',
        '3P%':'three_pointer_percentage',
        'FT':'free_throws',
        'FTA':'free_throws_attempted',
        'FT%':'free_throw_percentage',
        'ORB':'offensive_rebounds',
        'TRB':'total_rebounds',
        'AST':'assists',
        'STL':'steals',
        'BLK':'blocks',
        'TOV':'turnovers',
        'PF':'personal_fouls'
        }

    df.columns = df.columns.map(column_names)
    
    schools = df['school'].unique()
    school_dict = {}
    for school in schools:
        school_dict[school] = school.lower().translate(str.maketrans('','',string.punctuation)).replace(' ','-')
    
    return df, school_dict

def players_per_game(year):
    http = urllib3.PoolManager()
    URL = f'https://www.sports-reference.com/cbb/schools/abilene-christian/men/{year}.html'
    r = http.request('GET', URL)
    soup = BeautifulSoup(r.data, 'html.parser')

    filename = 'players_per_game.txt'
    with open(filename, 'w') as f:
        header = ','.join([item.get_text() for item in soup.select("table[id = 'players_per_game'] > thead > tr > th")])
        print(header, file=f)
        for item in soup.select("table[id='players_per_game'] > tbody > tr"):
            row_data = ','.join( [ item.get_text() for item in item.select("td") ] )
            print(row_data, file=f)

    df = pd.read_csv(filename)
    cols = df.columns
    df.drop(columns = 'Awards', inplace = True)
    df.columns = cols[1:]
    
    return df

def add_player_stats_to_team(team_df):
    top_ten_points = list(player_df.sort_values('PTS', ascending = False)['PTS'][0:10])
    top_ten_rebounds = list(player_df.sort_values('TRB', ascending = False)['TRB'][0:10])
    top_ten_fg_per = list(player_df.sort_values('FG%', ascending = False)['FG%'][0:10])
    
    for i in range(10):
        team_df[f'top_points_{i+1}'] = top_ten_points[i]
    for i in range(10):
        team_df[f'top_rebounds_{i+1}'] = top_ten_rebounds[i]
    for i in range(10):
        team_df[f'top_fg_per_{i+1}'] = top_ten_fg_per[i]
        
    return team_df

def get_home_team_results():
    http = urllib3.PoolManager()
    URL = f'https://www.sports-reference.com/cbb/schools/abilene-christian/men/2025-schedule.html'
    r = http.request('GET', URL)
    soup = BeautifulSoup(r.data, 'html.parser')

    filename = 'schedule.txt'
    with open(filename, 'w') as f:
        header = ','.join([item.get_text() for item in soup.select("table[id = 'schedule'] > thead > tr > th")])
        print(header, file=f)
        for item in soup.select("table[id='schedule'] > tbody > tr"):
            row_data = ','.join( [ item.get_text() for item in item.select("td") ] )
            print(row_data, file=f)

    df = pd.read_csv(filename)
    df.rename(columns = {'\xa0':'home_away',
                         '\xa0.1':'w_l',
                        'Tm':'home_team_pts',
                        'Opp':'road_team_pts',
                        'Opponent':'road_team'}, inplace = True)
    df = df.loc[(df['home_away'].isin([np.nan,'N'])) & (pd.isna(df['w_l']) == False)]
    df['home_team'] = abi_df['school'][0]
    df = df[['home_team','road_team','Conf','w_l','home_team_pts','road_team_pts']].reset_index(drop = True)
    
    return df

def get_todays_games_df():
    http = urllib3.PoolManager()
    URL = f'https://www.ncaa.com/scoreboard/basketball-men/d1/2025/02/07/all-conf'
    r = http.request('GET', URL)
    soup = BeautifulSoup(r.data, 'html.parser')

    header = ','.join([item.get_text() for item in soup.select("span[class = 'gamePod-game-team-name']")])

    today_games_df = pd.DataFrame(columns = ['today_road_team', 'today_home_team'])

    today_games_df['today_road_team'] = header.split(',')[0::2]
    today_games_df['today_home_team'] = header.split(',')[1::2]
    
    return today_games_df