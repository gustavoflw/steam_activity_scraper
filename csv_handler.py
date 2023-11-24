import os

class CsvHandler:
    def __init__(self, path):
        self.path = path
        self.columns= ['date', 'hour', 'game_status', 'game_name']

    def read(self):
        with open(self.path, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
        return data

    def write(self, data: list):
        with open(self.path, 'w') as f:
            f.write(','.join(self.columns) + '\n')

    def append(self, data: list):
        with open(self.path, 'a') as f:
            f.write(','.join(data) + '\n')

    def check_if_exists(self):
        return os.path.exists(self.path)

    def create_if_not_exists(self):
        if not self.check_if_exists():
            with open(self.path, 'w') as f:
                f.write(','.join(self.columns) + '\n')