import requests
from print_with_color import print_with_color

class DiscordHandler:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_message(self, message):
        data = {"content": message}
        response = requests.post(self.webhook_url, json=data)
        if response.status_code == 204:
            print_with_color(f"Message sent successfully", 'green')
        else:
            print_with_color(f"Failed to send message. Status code: {response.status_code}", 'red')