
from os.path import join, expanduser

def print_out(platform_config, msg):
    for plat_conf in platform_config:
            platform = plat_conf['platform']
            if platform == 'slack':
                _to_slack(plat_conf, msg)
            elif platform == 'txt':
                _to_txt(plat_conf, msg)
            elif platform == 'google sheet':
                _to_google_sheet(plat_conf, msg)

def _to_slack(platform_config, msg):
    import requests, json
    data = {'text': msg}
    web_hook_url = platform_config['web_hook_url']
    requests.post(web_hook_url, data=json.dumps(data))

def _to_txt(platform_config, msg):
    with open(platform_config['filePath'], 'a') as f:
        f.write(msg+'\n') 

def _to_google_sheet(platform_config, msg):
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from httplib2 import Http
    from oauth2client import file, client, tools
    # setting authentication and get the service
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = join('./', 'Kai_utils', 'seld-1540200324155-22f83fb910f2.json')
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    
    # spread sheet 
    SPREADSHEET_ID = platform_config['sheet ID']
    response = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    AllSheetsTitle = [sheet['properties']['title'] for sheet in response['sheets']]
    
    if platform_config['sheet name'] not in AllSheetsTitle:
        # creat new spreadsheet
        sheet_request = {
            "requests":[
                {
                    "addSheet":{
                        "properties": {
                            "title": platform_config['sheet name']
                        }
                    }
                }
            ]
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body=sheet_request).execute()
        
        assert(type(msg)==type(list()))
        # write to sheet
        value_range = {
            "values":msg
        }
        try:
            service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range=platform_config['sheet name'],
            valueInputOption="RAW", body=value_range
            ).execute()
        except expression as identifier:
            print(identifier)
        
    else:
        assert(type(msg)==type(list()))
        # write to sheet
        value_range = {
            "values":msg
        }

        try:
            service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range=platform_config['sheet name'],
            valueInputOption="RAW", body=value_range
            ).execute()
        except expression as identifier:
            print(identifier)

    
        
    
    
    
    
    
                
            
            
            
        