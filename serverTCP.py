import base64
import json
import os
import socket
import sys
import threading

import utils


def run(port):
    print(f'Running server at port {port}...')
    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind(('0.0.0.0', port))
        serverSocket.listen(5)
        while True:
            print('Waiting...')
            (clientSocket, address) = serverSocket.accept()
            print(f'connect to: {clientSocket}')
            threading.Thread(
                target=mainConnection,
                kwargs={'clientSocket': clientSocket.makefile('rw')},
            ).start()

    except Exception:
        print('RUN error')


def main():
    port = 50000
    if 1 <= port <= 65535:
        run(port)
    else:
        print('Invalid port')
        sys.exit()


def mainConnection(clientSocket):
    while True:
        operacao = json.loads(clientSocket.readline())

        if operacao['command'] == 'exit':
            print('exit')
            sys.exit()

        if operacao['command'] == 'list':
            print(json.dumps({
                'files': os.listdir('arquivosServer'),
            }), file=clientSocket, flush=True)

        elif operacao['command'] == 'put':
            fullFileName = os.path.join('arquivosServer', operacao['file'])

            with open(fullFileName, 'wb') as f:
                while True:
                    chunk = json.loads(clientSocket.readline())
                    if chunk['chunk'] is None:
                        break
                    f.write(base64.b64decode(chunk['chunk']))

            foi = operacao['hash'] == utils.calc_hash(fullFileName)
            if not foi:
                os.unlink(fullFileName)

            print(json.dumps({
                'file': operacao['file'],
                'operation': operacao['command'],
                'status': 'success' if foi else 'fail',
            }), file=clientSocket, flush=True)

        elif operacao['command'] == 'get':
            fullFileName = os.path.join('arquivosServer', operacao['file'])

            print(json.dumps({
                'file': operacao['file'],
                'operation': operacao['command'],
                'hash': utils.calc_hash(fullFileName),
            }), file=clientSocket, flush=True)

            with open(fullFileName, 'rb') as f:
                while True:
                    chunk = f.read(1024 * 1024)
                    if len(chunk) == 0:
                        print(json.dumps({'chunk': None}), file=clientSocket, flush=True)
                        break
                    print(json.dumps({
                        'chunk': base64.b64encode(chunk).decode('utf-8')
                        }), file=clientSocket, flush=True)


if __name__ == '__main__':
    main()
