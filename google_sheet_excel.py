'''
API for Goggle Sheet

'''

import asyncio
from pprint import pprint

from keys import *
import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
import time



class ExcelAPI:
    # day.month, week, hour:minutes
    time_now_data = time.strftime('%d.%m, %A, %H:%M')

    def __init__(self, CREDENTIALS_FILE:str, spreadsheet_id:str ):
        # Файл, полученный в Google Developer Console
        # https://console.cloud.google.com/apis/credentials/oauthclient/131872528200-g0c8lu5artgb46lsda1obtn3j286t8a9.apps.googleusercontent.com?project=windy-ripsaw-395415
        self.CREDENTIALS_FILE = CREDENTIALS_FILE
        # ID Google Sheets документа (можно взять из его URL)
        self.spreadsheet_id = spreadsheet_id
        # setting
        self.service = self.setting_API_excel_file()
        # data from excel
        self.values = self.read_excel_file()

    # Подключение API до service /  Настройки таблицы
    def setting_API_excel_file(self) -> googleapiclient.discovery.Resource:
        # Авторизуемся и получаем service — экземпляр доступа к API
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.CREDENTIALS_FILE,
            # Сервисы с которыми мы будем работать (spreadsheets, drive)
            ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http())
        # получаем данные из нашей обертки (sheets-GoogleSheets, version-v4, )
        service = googleapiclient.discovery.build('sheets', 'v4', http = httpAuth)
        return service

    # чтения файла
    def read_excel_file(self) -> dict:
        values = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='A1:Z100',
            majorDimension='ROWS' # COLUMNS
        ).execute()
        pprint(values)
        return values


    # Добавляем дату и время в пустом столбце
    def add_new_column_date(self) -> None:
        update_column_date = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    # chr(len(values['values'][0]) + 65) - получаем следующий столбец куда
                    #                                      надо записать дату и время
                    {"range": rf"{chr(len(self.values['values'][0]) + 65)}1",
                     "majorDimension": "ROWS",
                     "values": [[rf"{self.time_now_data}"]]},
            ]
            }
        ).execute()






# if '__main__' == __name__:
obj = ExcelAPI(CREDENTIALS_FILE, spreadsheet_id )