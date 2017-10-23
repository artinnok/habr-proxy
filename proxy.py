"""
##### Прокси-сервер для Хабра #####

Простейший прокси-сервер, использовались библиотеки:
* requests - запросы на проксируемый сайт
* lxml - замена ссылок на полученной странице + добавление ТМ
* click - параметры командной строки


##### Параметры запуска #####

* --host - хост, на котором стартует прокси-сервер (default - localhost)
* --port - порт, на котором стартует прокси-сервер (default - 8034)
* --site - сайт, который проксируем (default - https://habrahabr.ru)


##### Пример запуска #####
>>> python proxy.py --port=8000 --site=http://docs.python-requests.org/en/master
"""

import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

import requests
import click

from mutator import Mutator


REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
    'Accept-Encoding': 'gzip, deflate, sdch, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
              'image/webp,*/*;q=0.8'
}
RESPONSE_HEADERS = ('Content-Type', 'Content-Length', 'Date',)


class RequestHandler(BaseHTTPRequestHandler):
    mutator = None

    def do_GET(self):
        self._get_response_from_site()

        try:
            self._send_response_to_client()

        except BrokenPipeError:
            print('Client terminated connection.')

    def _get_response_from_site(self):
        self.response = requests.get(self.mutator.site + self.path, headers=REQUEST_HEADERS)

    def _send_response_to_client(self):
        self.send_response(self.response.status_code)

        [self.send_header(key, value) for key, value in self.response.headers.items() if key in RESPONSE_HEADERS]
        self.end_headers()

        out = self.mutator.modify_content(self.response)

        self.wfile.write(out)


@click.command()
@click.option('--host', default='0.0.0.0', help='хост прокси-сервера')
@click.option('--port', default=8034, help='порт прокси-сервера')
@click.option('--site', default='https://habrahabr.ru', help='проксируемый сайт')
def run(host, port, site):
    proxy_host = 'http://{}:{}'.format(host, port)

    RequestHandler.mutator = Mutator(proxy_host, site)

    webbrowser.open(proxy_host)

    server = HTTPServer((host, port), RequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    run()
