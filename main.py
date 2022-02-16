
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials	


CREDENTIALS_FILE = 'iboxing-26431174b990.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)


spreadsheet = service.spreadsheets().create(body = {}).execute()
spreadsheetId = spreadsheet['spreadsheetId'] # сохраняем идентификатор файла
print(f'https://docs.google.com/spreadsheets/d/{spreadsheetId}')


driveService = apiclient.discovery.build('drive', 'v3', http = httpAuth) # Выбираем работу с Google Drive и 3 версию API
access = driveService.permissions().create(
    fileId = spreadsheetId,
    body = {'type': 'user', 'role': 'writer', 'emailAddress': 'vovasinitsa@gmail.com'},  # Открываем доступ на редактирование
    fields = 'id'
).execute()

def main():
    pass

if __name__ == '__main__':
    main()
