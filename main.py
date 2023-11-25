import os
import time
from dotenv import load_dotenv
from game_stalker import GameStalker

# Paths and dirs
path_reports_dir = os.path.join(os.getcwd(), 'reports')
path_profile_reports_dir = os.path.join(path_reports_dir, 'profiles')
path_daily_reports_dir = os.path.join(path_reports_dir, 'daily')
path_profiles = os.path.join(os.getcwd(), 'profiles.csv')
path_env = os.path.join(os.getcwd(), '.env')
os.makedirs(path_profile_reports_dir, exist_ok=True)
os.makedirs(path_daily_reports_dir, exist_ok=True)

# Env
loaded_env = load_dotenv(path_env)
if loaded_env is False:
    raise Exception('Failed to load .env')

if __name__ == '__main__':
    game_stalker = GameStalker(
        os.getenv('DISCORD_URL'),
        minutes_between_reports=24*60,
        path_profiles=path_profiles,
        path_reports_dir=path_reports_dir,
        path_profile_reports_dir=path_profile_reports_dir,
        path_daily_reports_dir=path_daily_reports_dir
    )

    while True:
        game_stalker.stalk_and_report()
        print('Sleeping...')
        time.sleep(60)