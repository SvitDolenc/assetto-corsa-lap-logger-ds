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
        self.woorksheet.insert_row(["Lap","Time(ms)","Valid","User"], 1)

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


#main read args
demo = GoogleSheetDemo()


def main(argv, arc):
    demo.open_sheet(argv[2])
    name = argv[2]
    lap = argv[4]
    time = argv[6]
    invalidated = argv[8]
    user = "unknown"
    if(len(argv) > 10):
        user = argv[10]

    row_data = [lap, time, invalidated, user]
    demo.add_row(row_data)

if __name__ == '__main__':
    main(sys.argv, len(sys.argv))
