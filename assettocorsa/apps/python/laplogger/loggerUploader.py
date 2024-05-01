import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint as pp
import json
import os
import glob
import time
import sys

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
            if worksheet.title == sheet_name:
                self.woorksheet = worksheet
                return
        self.woorksheet = self.sheet.add_worksheet(title=sheet_name, rows="1000", cols="10")
        self.woorksheet.insert_row(["Time(ms)","User"], 1)

    def get_row(self, row_number):
        return self.woorksheet.row_values(row_number)

    def add_row(self, row_data):
        self.woorksheet.insert_row(row_data, 2)


    #NOT IN USE
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



def process_json(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            try:
                json_data = json.loads(line)
                time = json_data['time']
                user = json_data['user']

                row_data = [time, user]
                # Process each line of JSON data here
                #print(row_data)
                demo.add_row(row_data)
                
            except json.JSONDecodeError:
                # Handle invalid JSON data if necessary
                pass
#main read args

directory = './laplogs'

while True:
    demo = GoogleSheetDemo()
    files = os.listdir(directory)
    # Iterate over each file
    for file_name in files:
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            # Process JSON data in the file
            print('Processing file:', file_name)
            demo.open_sheet(file_name)
            process_json(file_path)
            try:
                os.remove(file_path)
            except:
                print("Error while deleting file : ", file_path)
    time.sleep(10)




# Function to process JSON data line by line


# Get list of files in the directory
