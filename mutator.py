import re

from lxml import html


TM = '™'
PLUS = '&plus;'
PATTERN = "(?<!\w)\w{6}(?=[^\w]|$)(?iu)"


class Mutator:
    res = None
    
    def _modify_content(self):
        if 'text/html' in self.response.headers['Content-Type']:
            root = self._replace_host(self.response.text)
            text = self._add_tm(root)
            return bytes(text, encoding='utf-8')

        return self.response.content

    def _replace_host(self, text):
        root = html.fromstring(text)
        root.rewrite_links(self._replace)
        return root

    def _replace(self, link):
        return link.replace(self.site, self.localhost)

    def _add_tm(self, root):
        tags = ("div", "span", "i", "a", "b", "strong", "li", "h1", "h2", "h3",
                "h4", "h5", "h6", "p", "q", "s", "strike", "blockquote", "br",)

        for item in root.iter(tags):
            item.text = self._add(item.text)
            item.tail = self._add(item.tail)

        return html.tostring(root, encoding='unicode',
                             doctype='<!DOCTYPE html>')

    def _sub(self, str):
        return re.sub(PATTERN, self._repl, str)

    def _repl(self, match):
        return match.group() + TM

    def _add(self, text):
        if text is not None:
            text = self._sub(text)
            return text.replace(PLUS, '+')