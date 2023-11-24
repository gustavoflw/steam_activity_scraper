import os
import time
import numpy as np
from datetime import timedelta
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from csv_handler import CsvHandler
from discord_handler import DiscordHandler
from steam_requester import Requester
from print_with_color import print_with_color

path_reports_dir = os.path.join(os.getcwd(), 'reports')
path_profiles = os.path.join(os.getcwd(), 'profiles.csv')
path_env = os.path.join(os.getcwd(), '.env')

loaded_env = load_dotenv(path_env)
if loaded_env is False:
    raise Exception('Failed to load .env')

discord_url = os.getenv('DISCORD_URL')

def get_report(steam_profiles: dict):
    results = []

    for profile in steam_profiles:
        print_with_color(f"\n--> Profile: {profile}", 'cyan')
        requester = Requester(steam_profiles[profile])
        page_content = requester.get_page_content()
        soup = BeautifulSoup(page_content, 'html.parser')

        profile_results = {'profile': profile}

        try:
            
            profile_results['game_status'] = requester.get_profile_in_game_header(soup)
            profile_results['game_name'] = requester.get_profile_in_game_name(soup)
        except Exception as e:
            print_with_color(f"Error: {e}", 'red')

        print_with_color(f"Results: {profile_results} ***", 'green')
        results.append(profile_results)

    df_results = pd.DataFrame(columns=['profile', 'game_status', 'game_name'])
    for profile in results:
        df_results = pd.concat([df_results, pd.DataFrame(profile, index=[0])], ignore_index=True)

    print_with_color(f"\nDataframe:\n{df_results}\n", 'yellow')

    return df_results.reset_index()

def stalk_and_report():
    csv_profiles = pd.read_csv(path_profiles)
    steam_profiles = {}
    for index, row in csv_profiles.iterrows():
        if int(row['allowed_to_track']) == 1:
            steam_profiles[row['name']] = row['url']

    df_results = get_report(steam_profiles)

    date = time.strftime("%d/%m/%Y")
    hour = time.strftime("%H:%M:%S")

    log_results = []
    for index, row in df_results.iterrows():
        
        if not os.path.exists(path_reports_dir):
            os.mkdir(path_reports_dir)
        path_report = os.path.join(path_reports_dir, f"report_{row['profile']}.csv")
        csv_handler = CsvHandler(path_report)
        csv_handler.create_if_not_exists()
        content_to_append = [date, hour, row['game_status'], row['game_name']]
        print_with_color(f"Appending to {path_report}: {content_to_append}", 'yellow')
        csv_handler.append(content_to_append)

        df = pd.read_csv(path_report, parse_dates=[['date', 'hour']], dayfirst=True)
        print(df)
        today = pd.Timestamp.now().floor('D')
        in_game_df = df[df['game_status'] == 'Currently In-Game']
        in_game_df['date_hour'] = pd.to_datetime(in_game_df['date_hour'])
        in_game_df = in_game_df[in_game_df['date_hour'].dt.floor('D') == today]
        in_game_df['duration'] = in_game_df['date_hour'].diff()
        in_game_df = in_game_df.iloc[1:]
        max_time_between_reports = timedelta(hours=2)
        in_game_df['duration'] = in_game_df['duration'].apply(lambda x: x / 2 if x > max_time_between_reports else x)
        total_game_hours = in_game_df['duration'].sum()
        total_seconds = np.timedelta64(total_game_hours, 's').astype('timedelta64[s]').astype(str)
        total_seconds = int(total_seconds.split(' ')[0])
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        formatted_duration = f'{hours:02}:{minutes:02}:{seconds:02}'
        print(f'Total game hours played today: {formatted_duration}')

        profile_log = [
            f"# profile: {row['profile']}",
            f"- game status: {row['game_status']}",
            f"- game name: {row['game_name']}",
            f"- hours played today: {formatted_duration}"
        ]
        profile_log = '\n'.join(profile_log)
        log_results.append(profile_log)


    log_results = '\n'.join(log_results)
    log_datetime = f"{date} - {hour}"
    log_header = f'**STEAM STALKER REPORT ({log_datetime})**'

    log = [
        log_header,
        '```md\n',
        log_results,
        '```']
    log = ''.join(log)
    print_with_color(log, 'purple')
    DiscordHandler(discord_url).send_message(log)

if __name__ == '__main__':
    while True:
        stalk_and_report()
        print('Sleeping...')
        time.sleep(60)