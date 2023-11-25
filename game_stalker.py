import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta

from csv_handler import CsvHandler
from discord_handler import DiscordHandler
from steam_requester import Requester
from print_with_color import print_with_color

class GameStalker:
    def __init__(self, discord_url, minutes_between_reports, path_profiles, path_reports_dir, path_profile_reports_dir, path_daily_reports_dir):
        self.__discord_url = discord_url
        self.__last_reported_datetime = None
        self.__minutes_between_reports = minutes_between_reports
        self.__path_profiles = path_profiles
        self.__path_reports_dir = path_reports_dir
        self.__path_profile_reports_dir = path_profile_reports_dir
        self.__path_daily_reports_dir = path_daily_reports_dir

    def __get_trackable_profiles(self):
        csv_profiles = pd.read_csv(self.__path_profiles)
        steam_profiles = {}
        for index, row in csv_profiles.iterrows():
            if int(row['allowed_to_track']) == 1:
                steam_profiles[row['name']] = row['url']
        print_with_color(f"Steam profiles to track:", 'purple')
        [print_with_color(f"- {profile} | {steam_profiles[profile]}", 'white') for profile in steam_profiles]
        return steam_profiles

    def __get_date_hour(self):
        date = time.strftime("%d/%m/%Y")
        hour = time.strftime("%H:%M:%S")
        print_with_color(f"Date: {date}, hour: {hour}", 'purple')
        return date, hour

    def __find_reported_dates(self, path_report, show_output=False) -> list:
        df_report = pd.read_csv(path_report, parse_dates=[['date', 'hour']], dayfirst=True)
        dates_reported = df_report['date_hour'].dt.floor('D').unique()
        dates_reported = [date.strftime("%d/%m/%Y") for date in dates_reported]
        if show_output:
            print_with_color(f"Dates reported: {dates_reported}", 'purple')
        return dates_reported

    def __convert_seconds_to_hhmmss(self, seconds, show_output=False):
        hhmmss = str(timedelta(seconds=seconds))
        if show_output:
            print(f"Converted {seconds} seconds to {hhmmss}")
        return hhmmss

    def __get_seconds_played_for_date(self, path_report, target_date, show_output=False):
        df_report = pd.read_csv(path_report, parse_dates=[['date', 'hour']], dayfirst=True)
        target_date = pd.Timestamp(target_date).floor('D')
        in_game_df = df_report[df_report['game_status'] == 'Currently In-Game'].copy()
        in_game_df['date_hour'] = pd.to_datetime(in_game_df['date_hour'])
        in_game_df = in_game_df[in_game_df['date_hour'].dt.floor('D') == target_date]
        in_game_df['duration'] = in_game_df['date_hour'].diff()
        in_game_df = in_game_df.iloc[1:]
        max_time_between_reports = timedelta(hours=2)
        in_game_df['duration'] = in_game_df['duration'].apply(lambda x: x / 2 if x > max_time_between_reports else x)
        total_game_hours = in_game_df['duration'].sum()
        total_seconds = np.timedelta64(total_game_hours, 's').astype('timedelta64[s]').astype(str)
        total_seconds = int(total_seconds.split(' ')[0])
        if show_output:
            print(f"Total seconds played in {target_date.strftime('%d/%m/%Y')}: {total_seconds}")
        return total_seconds

    def stalk_and_report(self):
        now_date, now_hour = self.__get_date_hour()
        steam_profiles = self.__get_trackable_profiles()
        requester = Requester(steam_profiles)
        df_results = requester.get_report()

        print_with_color(f"\nSaving current instant report", 'yellow')
        for index, row in df_results.iterrows():
            print_with_color(f"> Profile: {row['profile']}", 'blue')

            content_to_append = [now_date, now_hour, row['game_status'], row['game_name']]

            path_report = os.path.join(self.__path_profile_reports_dir, f"{row['profile']}.csv")
            csv_handler = CsvHandler(path_report, ['date', 'hour', 'game_status', 'game_name'])        
            csv_handler.append(content_to_append, True)
        
        print_with_color(f"\nGetting hours played today", 'yellow')
        for profile in steam_profiles:
            print_with_color(f"> profile: {profile}", 'blue')

            path_report = os.path.join(self.__path_profile_reports_dir, f"{profile}.csv")
            dates = self.__find_reported_dates(path_report)
            dates = [pd.Timestamp(date).floor('D').strftime("%d/%m/%Y") for date in dates]
            
            path_daily_reports = os.path.join(self.__path_daily_reports_dir, f"{profile}.csv")
            csv_handler = CsvHandler(path_daily_reports, ['date', 'hours_played'])

            for target_date in dates:
                print_with_color(f">> date: {target_date}", 'purple')
                seconds_played = self.__get_seconds_played_for_date(path_report, target_date)
                hours_played = self.__convert_seconds_to_hhmmss(seconds_played)
                
                date_is_present = csv_handler.column_has_value(0, target_date)
                if date_is_present:
                    row, column = csv_handler.get_cell_locations_with_value(target_date, unique=True)[0]
                    csv_handler.write_to_cell(row, 1, hours_played, True)
                else:
                    csv_handler.append([target_date, hours_played], True)
                    csv_handler.sort_by_column(0)

        print_with_color(f"\nMaking plots", 'yellow')
        for profile in steam_profiles:
            path_daily_reports = os.path.join(self.__path_daily_reports_dir, f"{profile}.csv")
            csv_handler = CsvHandler(path_daily_reports, ['date', 'hours_played'])
            df_daily_reports = pd.read_csv(path_daily_reports)
            df_daily_reports['date_unformatted'] = df_daily_reports['date']
            df_daily_reports['date'] = pd.to_datetime(df_daily_reports['date'], dayfirst=True)
            df_daily_reports = df_daily_reports.sort_values(by=['date'])
            df_daily_reports['hours_played'] = pd.to_timedelta(df_daily_reports['hours_played'])
            df_daily_reports['hours_played'] = df_daily_reports['hours_played'].dt.total_seconds() / 3600
            df_daily_reports['hours_played'] = df_daily_reports['hours_played'].astype(float)
            df_daily_reports['Hours played'] = df_daily_reports['hours_played']
            df_daily_reports.plot(x='date_unformatted', y='Hours played', kind='bar')
            plt.title(f"{profile} - Hours played per day")
            plt.xlabel('Date')
            plt.ylabel('Hours played')
            plt.ylim(0, 24)
            plt.yticks(np.arange(0, 24, 1))
            plt.grid(axis='y')
            plt.xticks(rotation=90)
            plt.tight_layout()
            plt.savefig(os.path.join(self.__path_daily_reports_dir, f"{profile}.png"))

        print_with_color(f"\nDetermining if should report", 'yellow')
        should_report = False

        if self.__last_reported_datetime is None:
            should_report = True
        else:
            self.__last_reported_datetime = pd.Timestamp(self.__last_reported_datetime)
            now_datetime = pd.Timestamp.now()
            time_difference = now_datetime - self.__last_reported_datetime
            time_difference_minutes = time_difference.total_seconds() / 60
            if time_difference_minutes >= self.__minutes_between_reports:
                should_report = True
            else:
                remaining_minutes = self.__minutes_between_reports - time_difference_minutes
                remaining_seconds = int(remaining_minutes * 60)
                print(f"remaining_seconds: {remaining_seconds}")
        if should_report:
            self.__last_reported_datetime = pd.Timestamp.now()
        print(f"last_reported_datetime: {self.__last_reported_datetime}")
        print(f"should_report: {should_report}")

        if not should_report:
            print_with_color(f"\nNot reporting yet (remaining: {remaining_minutes} min)", 'yellow')
        else:
            print_with_color(f"\nSending graphs to Discord", 'yellow')
            for profile in steam_profiles:
                print_with_color(f"> profile: {profile}", 'blue')

                path_graph = os.path.join(self.__path_daily_reports_dir, f"{profile}.png")
                file_name = f"{profile}.png"
                DiscordHandler(self.__discord_url).send_file(path_graph, file_name)