import base64
import json
import os
import socket
import sys

import utils

printCommand = '''
Digite o o comando:
list    ||    put    ||   get  ||  exit
'''

printNomeArquivo = '''
Digite o nome do arquivo:
'''


def main():
    ip = '127.0.0.1'
    port = 50000

    socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketClient.connect((ip, port))
    socketFile = socketClient.makefile('rw')

    while True:
        operacao = input(printCommand).lower()

        if operacao == 'exit':
            print(json.dumps({
                'command': 'exit',
            }), file=socketFile, flush=True)
            sys.exit()

        elif operacao == 'list':
            print(json.dumps({
                'command': 'list',
            }), file=socketFile, flush=True)

            retorno = json.loads(socketFile.readline())
            print(retorno['files'])

        elif operacao == 'put':
            fileName = input(printNomeArquivo)
            fullFileName = os.path.join('arquivosClient', fileName)

            print(json.dumps({
                'command': 'put',
                'file': fileName,
                'hash': utils.calc_hash(fullFileName),
            }), file=socketFile, flush=True)

            with open(fullFileName, 'rb') as f:
                while True:
                    chunk = f.read(1024 * 1024)
                    if len(chunk) == 0:
                        print(json.dumps({'chunk': None}), file=socketFile, flush=True)
                        break
                    print(json.dumps({'chunk': base64.b64encode(chunk).decode('utf-8')}), file=socketFile, flush=True)

            retorno = json.loads(socketFile.readline())
            print(retorno)

        elif operacao == 'get':
            fileName = input(printNomeArquivo)
            fullFileName = os.path.join('arquivosClient', fileName)

            print(json.dumps({
                'command': 'get',
                'file': fileName,
            }), file=socketFile, flush=True)

            retorno = json.loads(socketFile.readline())

            with open(fullFileName, 'wb') as f:
                while True:
                    chunk = json.loads(socketFile.readline())
                    if chunk['chunk'] is None:
                        break
                    f.write(base64.b64decode(chunk['chunk']))

            foi = retorno['hash'] == utils.calc_hash(fullFileName)
            if not foi:
                os.unlink(fullFileName)

            print({
                'file': retorno['file'],
                'operation': 'get',
                'status': 'success' if foi else 'fail'})


if __name__ == '__main__':
    main()
