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
            raise Exception(
                print_with_color(
                    f"Failed to send message. Status code: {response.status_code}", 'red', return_as_string=True))

    def send_file(self, path, file_name=None):
        with open(path, 'rb') as f:
            if file_name is not None:
                data = {"file": (file_name, f.read())}
            response = requests.post(self.webhook_url, files=data)
            if response.status_code == 204 or response.status_code == 200:
                print_with_color(f"File sent successfully", 'green')
            else:
                raise Exception(
                    print_with_color(
                        f"Failed to send file. Status code: {response.status_code}", 'red', return_as_string=True))