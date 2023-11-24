import requests
from print_with_color import print_with_color

class Requester:
    def __init__(self, steam_profile_url):
        self.steam_profile_url = steam_profile_url

    def get_page_content(self):
        response = requests.get(self.steam_profile_url)
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
            print_with_color(f"Found text: {element_text}")
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
            print_with_color(f"Found text: {element_text}")
            return element_text
        else:
            print_with_color(f"Element not found", 'red')
            return "No game"