import pickle
import os
from typing import Any
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime

class Service():

    def __init__(self,client_secret_file, api_name, api_version, *scopes) -> None:
        self.client_secret_file = client_secret_file
        self.api_name = api_name
        self.api_version = api_version
        self.scopes = [scope for scope in scopes[0]]
        print(self.client_secret_file, self.api_name, self.api_version, self.scopes, sep='-')

        self.cred = None

        pickle_file = f'token_{self.api_name}_{self.api_version}.pickle'
        # print(pickle_file)

        if os.path.exists(pickle_file):
            with open(pickle_file, 'rb') as token:
                self.cred = pickle.load(token)

        if not self.cred or not self.cred.valid:
            if self.cred and self.cred.expired and self.cred.refresh_token:
                self.cred.refresh(Request())
            else:
                self.flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, self.scopes)
                self.cred = self.flow.run_local_server()

            with open(pickle_file, 'wb') as token:
                pickle.dump(self.cred, token)
        
        try:
            service = build(self.api_name, self.api_version, credentials=self.cred)
            print(self.api_name, 'service created successfully')
            self.service = service
        except Exception as e:
            print('Unable to connect.')
            print(e)
            return None
        pass




def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt