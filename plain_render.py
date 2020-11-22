"""
HTML renderer for mistletoe.
"""

import re
import sys
from itertools import chain
from urllib.parse import quote
from mistletoe.block_token import HTMLBlock
from mistletoe.span_token import HTMLSpan
from mistletoe.base_renderer import BaseRenderer
if sys.version_info < (3, 4):
    from mistletoe import _html as html
else:
    import html


class Plain_Renderer(BaseRenderer):
    """
    HTML renderer class.
    See mistletoe.base_renderer module for more info.
    """
    def __init__(self, *extras):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
        """
        self._suppress_ptag_stack = [False]
        super().__init__(*chain((HTMLBlock, HTMLSpan), extras))
        # html.entities.html5 includes entitydefs not ending with ';',
        # CommonMark seems to hate them, so...
        self._stdlib_charref = html._charref
        _charref = re.compile(r'&(#[0-9]+;'
                              r'|#[xX][0-9a-fA-F]+;'
                              r'|[^\t\n\f <&#;]{1,32};)')
        html._charref = _charref

    def __exit__(self, *args):
        super().__exit__(*args)
        html._charref = self._stdlib_charref

    def render_to_plain(self, token):
        if hasattr(token, 'children'):
            inner = [self.render_to_plain(child) for child in token.children]
            return ''.join(inner)
        return self.escape_html(token.content)

    def render_strong(self, token):
        return self.render_inner(token)

    def render_emphasis(self, token):
        template = '<em>{}</em>'
        return template.format(self.render_inner(token))

    def render_inline_code(self, token):
        return self.render_inner(token)

    def render_strikethrough(self, token):
        return self.render_inner(token)

    def render_link(self, token):
        return self.render_inner(token)

    def render_auto_link(self, token):
        return self.render_inner(token)

    def render_escape_sequence(self, token):
        return self.render_inner(token)

    def render_raw_text(self, token):
        return self.escape_html(token.content)

    @staticmethod
    def render_html_span(token):
        return token.content

    def render_heading(self, token):
        return self.render_inner(token)

    def render_quote(self, token):
        return self.render_inner(token)

    def render_paragraph(self, token):
        return self.render_inner(token)

    def render_block_code(self, token):
        return self.render_inner(token)

    def render_list(self, token):
        return self.render_inner(token)

    def render_list_item(self, token):
        return self.render_inner(token)

    @staticmethod
    def render_thematic_break(token):
        return '<hr />'

    @staticmethod
    def render_line_break(token):
        return '\n' if token.soft else '<br />\n'

    @staticmethod
    def render_html_block(token):
        return token.content

    def render_document(self, token):
        self.footnotes.update(token.footnotes)
        inner = '\n'.join([self.render(child) for child in token.children])
        return '{}\n'.format(inner) if inner else ''

    @staticmethod
    def escape_html(raw):
        return html.escape(html.unescape(raw)).replace('&#x27;', "'")

    @staticmethod
    def escape_url(raw):
        """
        Escape urls to prevent code injection craziness. (Hopefully.)
        """
        return html.escape(quote(html.unescape(raw), safe='/#:()*?=%@+,&'))