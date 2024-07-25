#!/usr/bin/env python3

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import django
import sys
from django.conf import settings
from django.test import RequestFactory
import datetime

# change this during setup
# sys.path.append(r'C:\Users\labAdmin\Documents\KauffmanLabProject')
sys.path.append(r'C:\Users\labAdmin\Documents\KauffmanLabProject')

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KauffmanLabProject.settings')
django.setup()

from KauffmanLabApp import views

SCOPES = ['https://www.googleapis.com/auth/drive.file']
# SERVICE_ACCOUNT_FILE = os.path.join('/Users/jatinchhabria/Documents/KauffmanLab/KauffmanLabProject/KauffmanLabApp/media', 'creds/kauffman-lab-data-backup-67a554acfbc0.json')
SERVICE_ACCOUNT_FILE = r'C:\Users\labAdmin\Documents\KauffmanLabProject\KauffmanLabApp\media\creds\kauffman-lab-data-backup-67a554acfbc0.json'

def upload_to_google_drive(file_path, file_name, parent_folder_id=None):
    print('in upload_to_google_drive')
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
                        'name': file_name,
                        'parents': [parent_folder_id] if parent_folder_id else []
                     }
    media = MediaFileUpload(file_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'File ID: {file.get("id")}')

if __name__ == "__main__":
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/dummy-url')

    file_path = views.export_excel_csv(request=request, selections=None, action='export_excel_for_bakcup')
    if file_path:
        now = datetime.datetime.now()
        timestamp = f"{str(now.year)[-2:]}{now.timetuple().tm_yday}_{now.strftime('%H%M%S')}"
        file_name = f'{timestamp}.samples_backup.xlsx'
        parent_folder_id = '1jQAvDbYUC6hP-pplduW1kAI9I2RwEF6C'
        upload_to_google_drive(file_path, file_name, parent_folder_id)
