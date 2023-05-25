#to deactivate virtual environment run 'deactivate' in terminal.
from Google import Service
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload,HttpRequest
from googleapiclient.errors import HttpError
import pandas as pd
from io import BytesIO
import os
import zipfile

class fileResponse:

    FILE_TYPES = {
        "image/jpeg":"jpeg",
        "application/vnd.google-apps.folder":"folder",
        "application/octet-stream":".DS_Store"
    }
    
    def __init__(self,id:str,name:str,mimetype:str):
        self.id = id
        self.name = name
        self.mimetype = mimetype
        self.filetype = fileResponse.FILE_TYPES[mimetype]


class Drive(Service):

    """
    A wrapper for the Google.Service object that is specific to the Google Drive API.
    """

    CLIENT_SECRET_FILE = '/Users/trevor.johnson/Documents/Ironview360/credentials.json'
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    def __init__(self, client_secret_file:str=CLIENT_SECRET_FILE, api_name:str=API_NAME, api_version:str=API_VERSION, scopes:list=SCOPES) -> None:
        super().__init__(client_secret_file,api_name,api_version,scopes)

    def create_folder(self,request_body:str):

        """Create a folder"""

        self.service.files().create(body=request_body).execute()
    
    def upload_media(self,file:str,name:str):

        """Upload media"""

        try:
            file_metadata = {
                'name':name
            }
            media = MediaFileUpload(file,resumable=True)
            print(media)
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"File ID: {file.get('id')}")

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
        
    def search(
            self,
            query:str='',
            pageSize:int=1000,
            includeItemsFromAllDrives:bool=True,
            supportsAllDrives:bool=True,
            corpora:str="user"
            ):

        #print("Request made")
        response = self.service.files().list(q=query, pageSize=pageSize, includeItemsFromAllDrives=includeItemsFromAllDrives, supportsAllDrives=supportsAllDrives, corpora=corpora, fields="nextPageToken, files(id, name, mimeType)").execute()
        #print("Response received")
        files = response.get('files')
        #print(f"files: {files}")
        nextPageToken = response.get('nextPageToken')
        #print(nextPageToken)
        #loop over multiple pages if necessary
        while nextPageToken:
            response = self.service.files().list(
                q=query,
                pageToken=nextPageToken).execute()
            files.extend(response.get('files'))
            nextPageToken = response.get('nextPageToken', None)
            #print('next page clicked')
        
        results = pd.DataFrame(files)
        #print(results)
        return results
    
    def download_file(self,id:str,name:str):
        request = self.service.files().get_media(fileId=id)
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fd=fh, request=request)
        done = False


        while not done:
            status, done = downloader.next_chunk()
            print('Download progress {0}'.format(status.progress() * 100))
        
        fh.seek(0)

        with open(os.path.join('/Users/trevor.johnson/Downloads/',name), 'wb') as f:
            f.write(fh.read())
            f.close()

    def download_zip(self,folder_id:str,folder_name:str,zip_filename:str):

        folder_query = f"'{folder_id}' in parents"
        print(folder_query)
        query_response = self.search(folder_query)
        results = query_response[['id','name']]
        print(results)
        metadata = self.service.files().get(fileId=folder_id, fields="name")
        with zipfile.ZipFile(zip_filename, "w") as zip_file:
            for id, name in results.itertuples(index=False):
                file_request = self.service.files().get_media(fileId=id)
                file_content = file_request.execute()
                zip_file.writestr(name, file_content)
            







































    
def main():
    """Create an instance of Drive service"""
    drive = Drive()

    """Create a folder"""
    body = {
        'name':'National Parks',
        'mimeType':'application/vnd.google-apps.folder',
        'parents':[]
    }
    #drive.create_folder(request_body=body)

    """Upload media"""
    file = "/Users/trevor.johnson/Downloads/google-api.jpeg"
    #drive.upload(file,"Test.jpeg")

    """Search a folder"""
    folder_id = "1e0VEiod6hBR8wPS6h-c9X9nML02obe0Ma4NCUDclb7IoRXa2rhzRNi5qB-iN2rJbYObxdmM7"
    #query = f"parents = '{folder_id}'"
    #results = drive.search(query)
    #results.to_csv('/Users/trevor.johnson/Documents/Ironview360/search_results.csv')
    """"""

    result = drive.service.files()
    print(result)


if __name__ == '__main__':
    main()



"""
drive = Service(CLIENT_SECRET_FILE,API_NAME,API_VERSION,SCOPES)
print(drive)


def upload_files(drive:Service,body:dict):
    drive.service.files().create(body=body).execute()
    pass

#A sample of creating a file
#upload_files(drive,body)
"""