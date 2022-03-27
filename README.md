
Created By  : Everton Barbosa Kopec<br />
Created Date: 27/03/2022<br />
version ='1.0'<br />
Made for Python 3.5 and Google Drive API v3.<br />
Instructions:<br />
Create a service account and adds it in Creds local folder.<br />
Download_Files é usado para armazenar os arquivos na opção `d` opção `a`.<br />
Usage:<br />
```
[a] Listar Pastas no Google Drive
[b] Listar Arquivos no Google Drive
[c] Upload Arquivo para o Google Drive - Se o arquivo já existe, um update do arquivo será feito.
                                         Você pode inserir o arquivo apenas se ele estiver no diretório
                                         local ou o diretório completo com o nome do arquivo.
[d] Download Arquivo para o diretório local de preferência
  [a] Todos Arquivos - Download de todos os arquivos para a pasta Download_Files
  [b] Insira o nome do arquivo para Download - Você pode inserir no diretório local ou
                                               indicar um diretório com o nome do arquivo
  [q] Voltar ao Menu principal
[e] Download Pasta de alguma pasta desejada do Google Drive para um diretório local
[f] Apagar Arquivo do Google Drive - Só é possível os arquivos que a Service Account tiver permissão para exclusão.
[q] Quit - Fechar Menu
```
