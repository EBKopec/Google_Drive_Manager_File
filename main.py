#########################################################################
# Created By  : Everton Barbosa Kopec
# Created Date: 27/03/2022
# version ='1.0'
# Made for Python 3.5 and Google Drive API v3.
# Instructions:
# Create a service account and adds it in Creds local folder.
# Download_Files é usado para armazenar os arquivos na opção `d` opção `a`.
# Usage:
# [a] Listar Pastas no Google Drive
# [b] Listar Arquivos no Google Drive
# [c] Upload Arquivo para o Google Drive - Se o arquivo já existe, um update do arquivo será feito.
#                                          Você pode inserir o arquivo apenas se ele estiver no diretório
#                                          local ou o diretório completo com o nome do arquivo.
# [d] Download Arquivo para o diretório local de preferência
#   [a] Todos Arquivos - Download de todos os arquivos para a pasta Download_Files
#   [b] Insira o nome do arquivo para Download - Você pode inserir no diretório local ou
#                                                indicar um diretório com o nome do arquivo
#   [q] Voltar ao Menu principal
# [e] Download Pasta de alguma pasta desejada do Google Drive para um diretório local
# [f] Apagar Arquivo do Google Drive - Só é possível os arquivos que a Service Account tiver permissão para exclusão.
# [q] Quit - Fechar Menu
##########################################################################

import json
import os

import magic
import googleapiclient
from google.oauth2.service_account import Credentials
from googleapiclient import errors
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

from instructions import instructions

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive.photos.readonly',
          'https://www.googleapis.com/auth/drive.appdata',
          'https://www.googleapis.com/auth/drive.readonly',
          'https://www.googleapis.com/auth/drive.metadata']


def auth():
    service_account_info = json.load(open('Creds/service_account.json'))
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    return creds


def retrieve_all_files(service):
    """Retrieve a list of File resources.

      Args:
        service: Drive API service instance.
      Returns:
        List of File resources.
      """
    result = []
    page_token = None
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
            items = service.files().list(supportsAllDrives=True, includeItemsFromAllDrives=True,
                                         orderBy='createdTime, folder', **param).execute()
            result.extend(items['files'])
            page_token = items.get('nextPageToken')
            if not page_token:
                break
        except errors.HttpError as error:
            print('An error occurred: %s' % error)
            break
    return result


def download(service, file_io_base, file_id, mime_type, file_name):
    request = None
    fh = file_io_base
    while mime_type not in "application/vnd.google-apps.folder":
        if 'video' or 'image' in mime_type:
            request = service.files().get_media(fileId=file_id)
        else:
            request = service.files().export_media(fileId=file_id, mimeType=mime_type)
        downloader = MediaIoBaseDownload(fh, request)
        while True:
            status, done = downloader.next_chunk()
            print("Download file %s - %d%%." % (file_name, int(status.progress() * 100)))
            if done:
                return
            print('Download complete')


def upload_file(service, folder, file):
    all_files = retrieve_all_files(service)
    folder_id = None
    file_id = None
    folder_name = folder.lower()
    file_name = file.lower()
    folders = folders_list(all_files)
    mime = magic.Magic(mime=True)
    mime_file = mime.from_file('{0}'.format(file_name))

    for key, value in folders.items():
        if folder_name == key.lower():
            folder_id = value

    if folder_id is None:
        print("Pasta {0} não existe!".format(folder_name))
        return

    name = file_name.split("/")[-1]
    print(name)
    file_metadata = {
        'name': name,
        'parents': [folder_id],
    }
    media = MediaFileUpload('{0}'.format(file_name), mimetype=mime_file, resumable=True)

    for items in all_files:
        if items['mimeType'] != "application/vnd.google-apps.folder":
            if str(items['name']).lower() == file_name:
                file_id = items['id']
                file = service.files().update(fileId=file_id, media_body=media).execute()
                print("Arquivo atualizado e uploado realizado com sucesso, ID:{0} - Nome: {1} - Pasta: {2}".
                      format(file.get("id"), file_name, folder_name))
                return

    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print("Arquivo criado e upload realizado com sucesso, ID:{0} - Nome: {1} - Pasta: {2}".format(file.get("id"),
                                                                                                  file_name,
                                                                                                  folder_name))


def delete_file(service, file_id):
    try:
        service.files().delete(fileId=file_id).execute()
        service.files().emptyTrash().execute()
        print("\nArquivo Apagado!\n")
    except HttpError as err:
        if str(err.resp.status) == '403':
            print("O Usuário não tem permissão suficiente para apagar este arquivo")


def folders_list(all_files):
    folders = {}
    for items in all_files:
        if items['mimeType'] == "application/vnd.google-apps.folder":
            folders[items['name']] = items['id']
    return folders


def download_file(service, file_name):
    all_files = retrieve_all_files(service)
    # Call the Drive v3 API
    if not all_files:
        print('No files found.')
    control = False
    file = file_name.lower()
    for items in all_files:
        if items['mimeType'] != 'application/vnd.google-apps.folder':
            if file != 'todos' and file == str(items['name']).lower():
                files = open('{0}'.format(file), 'wb')
                download(service, files, items['id'], items['mimeType'], files)
                control = True
                continue

            elif file != 'todos' and file != str(items['name']).lower():
                pass

            elif file == 'todos':
                files = open('Download_Files/{0}'.format(items['name']), 'wb')
                download(service, files, items['id'], items['mimeType'], items['name'])
                control = True
                pass

    if not control:
        print("Arquivo não encontrado")


def main():
    creds = auth()
    service = googleapiclient.discovery.build('drive', 'v3', credentials=creds)
    main_menu = {"a": "[a] Listar Pastas",
                 "b": "[b] Listar Arquivos",
                 "c": "[c] Upload Arquivo",
                 "d": "[d] Download Arquivo",
                 "e": "[e] Download Pasta",
                 "f": "[f] Apagar Arquivo",
                 "i": "[i] Instruções",
                 "q": "[q] quit"}
    sub_menu = {"a": "[a] Todos Arquivos",
                "b": "[b] Insira o nome do arquivo para Download",
                "q": "[q] Voltar ao Menu principal"}
    loop = True
    while loop:
        print("Google Drive - Menu\n")

        for k, v in main_menu.items():
            print(v)

        choice = input("\nEscolha a operação\n")
        all_files = retrieve_all_files(service)
        if choice == "a":
            for items in all_files:
                if items['mimeType'] == 'application/vnd.google-apps.folder':
                    print(items)

        elif choice == "b":
            for items in all_files:
                if items['mimeType'] != 'application/vnd.google-apps.folder':
                    print(items)

        elif choice == "c":
            folder = input("Insira o nome da pasta de destino:")
            file = input("Insira o caminho completo e o nome do arquivo para Upload:")
            upload_file(service, folder, file)

        elif choice == "d":
            print("\nDownload Arquivo\n")
            for k, v in sub_menu.items():
                print(v)
            sub_choice = input("\nEscolha a opção:\n")
            sub_loop = True
            while sub_loop:
                if sub_choice == "a":
                    download_file(service, "todos")
                    sub_loop = False

                elif sub_choice == "b":
                    file = input("Insira o nome do arquivo para Download:\n")
                    download_file(service, file)
                    sub_loop = False

                elif sub_choice == "q":
                    sub_loop = False

                else:
                    os.system("cls")
                    print("Opção inválida")

        elif choice == "e":
            dir_from = input("\nNome da pasta de Origem no Google Drive:\n")
            dir_to = input("Nome da pasta local de Destino:\n")
            os.system("python download.py -f {0} -d {1}".format(dir_from, dir_to))

        elif choice == "f":
            for items in all_files:
                print(items)
            file_id = input("Insira o ID do arquivo que deseja apagar:\n")
            delete_file(service, file_id)
        elif choice == "i":
            os.system("cls")
            instructions()
        elif choice == "q":
            os.system("cls")
            print("Obrigado até a próxima")
            loop = False

        else:
            os.system("cls")
            print("Opção inválida!")


if __name__ == '__main__':
    main()
