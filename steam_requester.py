import requests
import pandas as pd
from bs4 import BeautifulSoup
from print_with_color import print_with_color

class Requester:
    def __init__(self, steam_profiles: dict):
        self.steam_profiles = steam_profiles

    def get_page_content(self, url):
        print_with_color(f"Fetching page: {url}", 'white')
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Failed to fetch page. Status code: {response.status_code}")

    def get_profile_in_game_header(self, soup):
        class_to_find = "profile_in_game_header"
        print_with_color(f"Finding {class_to_find}")
        element = soup.find("div", class_=class_to_find)
        if element:
            element_text = element.text
            print_with_color(f"Found text: {element_text}", 'green')
            return element_text
        else:
            print_with_color(f"Element not found", 'red')
            return "Not playing"

    def get_profile_in_game_name(self, soup):
        class_to_find = "profile_in_game_name"
        print_with_color(f"Finding {class_to_find}")
        element = soup.find("div", class_=class_to_find)
        if element:
            element_text = element.text
            print_with_color(f"Found text: {element_text}", 'green')
            return element_text
        else:
            print_with_color(f"Element not found", 'red')
            return "No game"

    def get_report(self):
        results = []

        for profile in self.steam_profiles:
            print_with_color(f"\n* Profile: {profile} *", 'cyan')
            requester = Requester(self.steam_profiles[profile])
            page_content = requester.get_page_content(self.steam_profiles[profile])
            soup = BeautifulSoup(page_content, 'html.parser')

            profile_results = {'profile': profile}

            try:
                profile_results['game_status'] = requester.get_profile_in_game_header(soup)
                profile_results['game_name'] = requester.get_profile_in_game_name(soup)
            except Exception as e:
                print_with_color(f"Error: {e}", 'red')

            print_with_color(f"Results: {profile_results}", 'green')
            results.append(profile_results)

        df_results = pd.DataFrame(columns=['profile', 'game_status', 'game_name'])
        for profile in results:
            df_results = pd.concat([df_results, pd.DataFrame(profile, index=[0])], ignore_index=True)

        print_with_color(f"\nDataframe:", 'yellow')
        print_with_color(df_results, 'inverse')
        print()

        return df_results.reset_index()