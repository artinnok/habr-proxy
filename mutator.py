import re

from lxml import html


TM = '™'
PLUS = '&plus;'
PATTERN = '(?<!\w)\w{6}(?=[^\w]|$)(?iu)'


class Mutator:
    def __init__(self, proxy_host, site):
        self.proxy_host = proxy_host
        self.site = site
        self.response = None

    def modify_content(self, response):
        self.response = response

        if 'text/html' in self.response.headers['Content-Type']:
            root = self._replace_site_host(self.response.text)
            text = self._add_tm(root)
            return bytes(text, encoding='utf-8')

        return self.response.content

    def _replace_site_host(self, text):
        root = html.fromstring(text)
        root.rewrite_links(self._rewrite_link)
        return root

    def _rewrite_link(self, link):
        return link.replace(self.site, self.proxy_host)

    def _add_tm(self, root):
        tags = ('div', 'span', 'i', 'a', 'b', 'strong', 'li', 'h1', 'h2', 'h3',
                'h4', 'h5', 'h6', 'p', 'q', 's', 'strike', 'blockquote', 'br',)

        for item in root.iter(tags):
            item.text = self._add(item.text)
            item.tail = self._add(item.tail)

        return html.tostring(root, encoding='unicode', doctype='<!DOCTYPE html>')

    def _replace_tm(self, match):
        return match.group() + TM

    def _add(self, text):
        if text is not None:
            text = re.sub(PATTERN, self._replace_tm, text)
            return text.replace(PLUS, '+')
