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

import re
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

import requests
import click
from lxml import html


TM = '™'
PLUS = '&plus;'

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

PATTERN = "(?<!\w)\w{6}(?=[^\w]|$)(?iu)"


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._get_response_from_site()
        self._send_response_to_client()

    def _get_response_from_site(self):
        self.res = requests.get(self.site + self.path, headers=REQUEST_HEADERS)

    def _send_response_to_client(self):
        self.send_response(self.res.status_code)

        [self.send_header(key, value) for key, value in self.res.headers.items()
         if key in RESPONSE_HEADERS]
        self.end_headers()

        out = self._modify_content()

        self.wfile.write(out)

    def _modify_content(self):
        if 'text/html' in self.res.headers['Content-Type']:
            self._replace_host()
            self._add_tm()
            return self.content

        return self.res.content

    def _replace_host(self):
        self.root = html.document_fromstring(self.res.text)
        self.root.rewrite_links(self._replace)

    def _replace(self, link):
        return link.replace(self.site, self.localhost)

    def _add_tm(self):
        tags = ("div", "span", "i", "a", "b", "strong", "li", "h1", "h2", "h3",
                "h4", "h5", "h6", "p", "q", "s", "strike", "blockquote", "br",)

        for item in self.root.iter(tags):
            item.text = self._add(item.text)
            item.tail = self._add(item.tail)

        self.content = html.tostring(self.root)

    def _sub(self, str):
        return re.sub(PATTERN, self._repl, str)

    def _repl(self, match):
        return match.group() + TM

    def _add(self, text):
        if text is not None:
            text = self._sub(text)
            return text.replace(PLUS, '+')


@click.command()
@click.option('--host', default='localhost', help='хост прокси-сервера')
@click.option('--port', default=8034, help='порт прокси-сервера')
@click.option('--site', default='https://habrahabr.ru',
              help='проксируемый сайт')
def run(host, port, site):
    localhost = 'http://{}:{}'.format(host, port)

    # monkey patching!
    RequestHandler.site = site
    RequestHandler.localhost = localhost

    webbrowser.open(localhost)

    server = HTTPServer((host, port), RequestHandler)
    server.serve_forever()

if __name__ == '__main__':
    run()
