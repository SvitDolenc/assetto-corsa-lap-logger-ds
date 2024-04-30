import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint as pp
import json
import os
import glob
import time

class GoogleSheetDemo:
    def __init__(self):
        self.scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                      "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet  = self.client.open("Python-google-sheets-demo")
        self.woorksheet = None

    def open_sheet(self, sheet_name):
        worksheet_list = self.sheet.worksheets()
        for worksheet in worksheet_list:
            print(worksheet)
            if worksheet.title == sheet_name:
                self.woorksheet = worksheet
                return
        self.woorksheet = self.sheet.add_worksheet(title=sheet_name, rows="100", cols="20")

    def get_row(self, row_number):
        return self.woorksheet.row_values(row_number)

    def add_row(self, row_data):
        self.woorksheet.insert_row(row_data, 2)
        print("The row has been added")

    def parse_and_add_rows(self, data_string):
        data_lines = data_string.split('\n')
        car = None
        track = None
        config = None
        fastest_lap = None
        for line in data_lines:
            if not line: continue  # skip empty lines
            if 'car:' in line or 'track:' in line or 'config:' in line:
                key, value = line.split(': ')
                if key == 'car':
                    car = value
                elif key == 'track':
                    track = value
                elif key == 'config':
                    config = value
                if car and track and config:
                     self.open_sheet(car + '-' + track + '-' + config)
                continue
            else:
                line = line.replace('False', 'false')
                line = line.replace('True', 'true')
                lap_data = json.loads(line.replace("'", "\""))  # Converting to valid JSON format by replacing single quotes with double quotes
                lap_time = lap_data['time']
                invalidated = lap_data['invalidated']
                lap_number = lap_data['lap']
                splits = lap_data['splits']
                row_data = [lap_time, invalidated, lap_number] + splits
                self.add_row(row_data)


# Example usage of the class
demo = GoogleSheetDemo()
#read from file


# Set the directory you want to start from
path = './logs'


while True:
    # Use glob to match all files in the directory
    for file_path in glob.glob(os.path.join(path, '*')):
        # Make sure it's a file
        if os.path.isfile(file_path):
            # Open and read the file
            with open(file_path, 'r') as file:
                content = file.read()
                print(f'Content of {file_path}:')
                demo.parse_and_add_rows(content)
                # Process content here ...

            # Delete the file after reading
            #os.remove(file_path)
            #print(f'{file_path} has been deleted.')

    time.sleep(10)
