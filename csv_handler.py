import os
import csv

class CsvHandler:
    def __init__(self, path, columns):
        self.path = path
        self.columns = columns
        self.create_if_not_exists()
        print(f"- Initialized csv handler: {self.path}")

    def read(self):
        with open(self.path, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
        return data

    def write(self, data: list):
        with open(self.path, 'w') as f:
            f.write(','.join(self.columns) + '\n')

    def append(self, data: list, show_output=False):
        if show_output:
            print(f"- Appending data: {data}")
        with open(self.path, 'a') as f:
            f.write(','.join(data) + '\n')

    def sort_by_column(self, column, show_output=False):
        if show_output:
            print(f"- Sorting by column: {column}")
        data = self.read()
        header = data[0]
        data = data[1:]
        data.sort(key=lambda x: x[column])
        data.insert(0, header)
        if show_output:
            print(f"- Sorted data: {data}")
        with open(self.path, 'w') as f:
            f.write('\n'.join([','.join(row) for row in data]))
            f.write('\n')

    def check_if_exists(self):
        return os.path.exists(self.path)

    def create_if_not_exists(self):
        if not self.check_if_exists():
            print(f"- Creating {self.path}")
            with open(self.path, 'w') as f:
                f.write(','.join(self.columns) + '\n')

    def write_to_cell(self, row, column, value, show_output=False):
        if show_output:
            print(f"- Writing '{value}' to cell: {row}, {column}")
        data = self.read()
        data[row][column] = value
        with open(self.path, 'w') as f:
            f.write('\n'.join([','.join(row) for row in data]))
            f.write('\n')

    def get_cell(self, row, column):
        data = self.read()
        return data[row][column]

    def get_cell_locations_with_value(self, value, unique=False, show_output=False):
        data = self.read()
        locations = []
        for row in range(len(data)):
            for column in range(len(data[row])):
                if data[row][column] == value:
                    locations.append((row, column))
        if len(locations) > 1 and unique:
            raise Exception(f"Value {value} is not unique")
        if show_output:
            print(f"Locations: {locations}")
        return locations

    def column_has_value(self, column, value, show_output=False):
        has_value = False
        data = self.read()
        for row in range(len(data)):
            if data[row][column] == value:
                has_value = True
                break
        if show_output:
            print(f"Value '{value}' in column '{column}': {has_value}")
        return has_value