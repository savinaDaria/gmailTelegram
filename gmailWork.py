from __future__ import print_function

import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import base64
from bs4 import BeautifulSoup
from apiclient import errors
# If modifying these scopes, delete the file token.json.
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/documents']

def credentials_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid: # If there are no (valid) credentials available, let the user log in.
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service_gmail = build('gmail', 'v1', credentials=creds)
    service_drive = build('drive', 'v3', credentials=creds)
    service_docs = build('docs', 'v1', credentials=creds)

    user_profile = service_gmail.users().getProfile(userId='me').execute()
    user_email = user_profile['emailAddress']
    return  service_gmail,service_drive,service_docs,user_email

def CreateMessage(sender, to, subject, msgPlain):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(msgPlain, 'plain'))
    raw = base64.urlsafe_b64encode(msg.as_bytes()) #кодирует байтоподобный объект s , используя алфавит, безопасный для URL и файловой системы,
    raw = raw.decode() #возвращает объект байтов, поэтому вам нужно преобразовать вывод в строку
    body = {'raw': raw}
    return body

def SendMessage(service,sender, to, subject, msgPlain):
    message1 = CreateMessage(sender, to, subject, msgPlain)
    SendMessageInternal(service, "me", message1)

def SendMessageInternal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

def create_doc(service_drive,name_doc):
    body = {
        'mimeType': 'application/vnd.google-apps.document',
        'name': name_doc,
    }
    file = service_drive.files().create(body=body,fields='webViewLink, id').execute()
    return file,file['id']

def insert_img_file(service_docs,file_id):
    with open("photos.txt", "r") as file:
        for line in file:
            requests = [{
                'insertInlineImage': {
                    'location': {
                        'index': 1
                    },
                    'uri':
                        line
                }
            }]
            body = {'requests': requests}
            response = service_docs.documents().batchUpdate(
                documentId=file_id, body=body).execute()
            insert_inline_image_response = response.get('replies')[0].get('insertInlineImage')
            print('Inserted image with object ID: {0}'.format(
                insert_inline_image_response.get('objectId')))

def GetMessage(service, count,sender_value,senderbool):
    result = service.users().messages().list(userId='me').execute()
    messages = result.get('messages')
    mes_list=[]
    # messages is a list of dictionaries where each dictionary contains a message id.
    for msg in messages:
        # Get the message from its id
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        payload = txt['payload']
        headers = payload['headers']
        for d in headers: # Look for Subject and Sender Email in the headers
            if d['name'] == 'Subject':
                subject = d['value']
            if d['name'] == 'From':
                sender = d['value']
        if senderbool=='true' and sender_value != sender:
            continue
        # The Body of the message is in Encrypted format. So, we have to decode it.
        # Get the data and decode it with base 64 decoder.
        parts = payload['parts'][0]
        data = parts['body']['data']
        data = data.replace("-", "+").replace("_", "/")
        decoded_data =  base64.b64decode(data).decode('utf-8')
        soup = BeautifulSoup(decoded_data, 'html.parser')
        body = soup.text
        mes_body="Subject: "+ str(subject)+"\nFrom: "+str(sender)+"\nMessage: "+str(body)
        mes_list.append(mes_body)
        if len(mes_list)==int(count):
            break
    return mes_list


def main():
    to = 'dsavina21@gmail.com'
    sender = 'darianna697@gmail.com'
    subject = "subject"
    msgPlain = "Hi\nPlain Email"
    service_gmail,service_drive,service_docs,user_email=credentials_service()
    #file,file_id=create_doc(service_drive,'name_doc')
    #document = service_docs.documents().get(documentId=file_id).execute()
    #print('The title of the document is: {}'.format(document.get('title')))
    #link = file.get('webViewLink')
    #insert_img_file(service_docs,file_id)
    mess=GetMessage(service_gmail,5,"darianna697@gmail.com",True)
    #SendMessage(service, sender, to, subject,  msgPlain)
    subject = "subject"
if __name__ == '__main__':
    main()

