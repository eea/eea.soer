""" Transform
"""
from Products.PortalTransforms.interfaces import itransform
from DocumentTemplate.DT_Util import html_quote
from DocumentTemplate.DT_Var import newline_to_br
import re
from htmlentitydefs import name2codepoint
from Products.kupu.plone.config import UID_PATTERN
from zope.interface import implements
from Products.PortalTransforms.interfaces import ITransform

name2codepoint = name2codepoint.copy()
name2codepoint['apos'] = ord("'")

# IMAGE_PATTERN matches an image tag on its own, or an image tag
# enclosed in a simple <p> or <div>. In the latter case we strip out
# the enclosing tag since we are going to insert our own.
PATIMG = '\\<img[^>]+class\s*=[^=>]*captioned[^>]+\\>'
PATA = '(?:(?P<atag0>\\<a[^>]*\\>)'+PATIMG+'\\</a\\>)' + '|' + PATIMG
PAT0 = '(?P<pat0>'+PATA+')'
PAT1 = '<(?:p|div)[^>]*>'+PAT0 + '</(?:p|div)>' + '|' + PAT0.replace('0>','1>')
IMAGE_PATTERN = re.compile(PAT1, re.IGNORECASE)

# Regex to match stupid IE attributes. In IE generated HTML an
# attribute may not be enclosed by quotes if it doesn't contain
# certain punctuation.
ATTR_VALUE = '=(?:"?)(?P<%s>(?<=")[^"]*|[^ \/>]*)'
ATTR_CLASS = ATTR_VALUE % 'class'
ATTR_WIDTH = ATTR_VALUE % 'width'
ATTR_HEIGHT = ATTR_VALUE % 'height'
ATTR_ALT = ATTR_VALUE % 'alt'

ATTR_PATTERN = re.compile('''
    (?P<tag>\<
     ( class%s
     | src\s*=\s*"resolveuid/(?P<src>([^/"#? ]*))
     | width%s
     | alt%s
     | height%s
     | .
     )*\>
    )''' % (ATTR_CLASS, ATTR_WIDTH, ATTR_ALT, ATTR_HEIGHT),
         re.VERBOSE | re.IGNORECASE | re.DOTALL)
SRC_TAIL = re.compile(r'/([^" \/>]+)')

CLASS_PATTERN = re.compile('\s*class\s*=\s*("[^"]*captioned[^"]*"|[^" \/>]+)')
ALT_PATTERN = re.compile('\\balt\s*=\s*("[^"]*"|[^" \/>]+)')
END_TAG_PATTERN = re.compile('(<img[^>]*?)( */?>)')
IMAGE_TEMPLATE = '''\
<dl class="%(class)s" style="width:%(width)spx;">
 <dt style="width:%(width)spx;">
  %(tag)s
 </dt>
 <dd class="image-caption">
  %(caption)s
 </dd>
</dl>
<h2> Fjantit</h2>
'''

class ImageSource:
    """ Transform which adds captions to images embedded in HTML
    """
    if ITransform is not None:
        implements(ITransform)
    __implements__ = itransform
    __name__ = "image_with_source"
    inputs = ('text/x-html-safe',)
    output = "text/x-html-safe"

    def __init__(self, name=None):
        self.config_metadata = {
            'inputs' : ('list',
                        'Inputs',
                        'Input(s) MIME type. Change with care.'),
            }
        if name is not None:
            self.__name__ = name

    def name(self):
        """ Name
        """
        return self.__name__

    def __getattr__(self, attr):
        if attr == 'inputs':
            return self.config['inputs']
        if attr == 'output':
            return self.config['output']
        raise AttributeError(attr)

    def resolveuid(self, context, reference_catalog, uid):
        """ Convert a uid to an object by looking it up in the reference
            catalog.
            If not found then tries to fallback to a possible hook (e.g.
            so you could resolve uids on another system).
        """
        target = reference_catalog.lookupObject(uid)
        if target is not None:
            return target
        hook = getattr(context, 'kupu_resolveuid_hook', None)
        if hook is not None:
            target = hook(uid)
        return target

    def convert(self, data, idata, filename=None, **kwargs):
        """ Convert the data, store the result in idata and return that
        optional argument filename may give the original file name of received data
        additional arguments given to engine's convert, convertTo or __call__ are
        passed back to the transform

        The object on which the translation was invoked is available as context
        (default: None)
        """
        context = kwargs.get('context', None)
        at_tool = None
        template = context.kupu_captioned_image
        if context is not None:
            at_tool = context.archetype_tool
            rc = at_tool.reference_catalog

        if context is not None and at_tool is not None:
            def replaceImage(match):
                """ Replace image
                """
                tag = match.group('pat0') or match.group('pat1')
                attrs = ATTR_PATTERN.match(tag)
                atag = match.group('atag0') or match.group('atag1')
                src = attrs.group('src')
                subtarget = None
                m = SRC_TAIL.match(tag, attrs.end('src'))
                if m is not None:
                    srctail = m.group(1)
                else:
                    srctail = None
                if src is not None:
                    d = attrs.groupdict()
                    target = self.resolveuid(context, rc, src)
                    if target is not None:
                        d['class'] = attrs.group('class')
                        d['originalwidth'] = attrs.group('width')
                        d['originalalt'] = attrs.group('alt')
                        d['url_path'] = target.absolute_url_path()
                        d['caption'] = \
                             newline_to_br(html_quote(target.Description()))
                        d['image'] = d['fullimage'] = target
                        d['tag'] = None
                        d['isfullsize'] = True
                        d['width'] = target.width
                        if srctail:
                            if isinstance(srctail, unicode):
                                # restrictedTraverse doesn't accept unicode
                                srctail = srctail.encode('utf8')
                            try:
                                subtarget = target.restrictedTraverse(srctail)
                            except Exception:
                                subtarget = getattr(target, srctail, None)
                            if subtarget is not None:
                                d['image'] = subtarget

                            if srctail.startswith('image_'):
                                d['tag'] = \
                               target.getField('image').tag(target,
                                                            scale=srctail[6:])
                            elif subtarget:
                                d['tag'] = subtarget.tag()

                        if d['tag'] is None:
                            d['tag'] = target.tag()

                        if subtarget is not None:
                            d['isfullsize'] = subtarget.width == \
                               target.width and subtarget.height == \
                               target.height
                            d['width'] = subtarget.width

                        # Strings that may contain non-ascii characters
                        # need to be decoded to unicode
                        for key in ('caption', 'tag'):
                            if isinstance(d[key], str):
                                d[key] = d[key].decode('utf8')

                        # Must preserve original link, don't overwrite with
                        # a link to the image
                        if atag is not None:
                            d['isfullsize'] = True
                            d['tag'] = "%s%s</a>" % (atag, d['tag'])

                        result = template(**d)
                        if isinstance(result, str):
                            result = result.decode('utf8')

                        return result

                return match.group(0) # No change

            if isinstance(data, str):
                data = data.decode('utf8')
            html = IMAGE_PATTERN.sub(replaceImage, data)

            # Replace urls that use UIDs with human friendly urls.
            def replaceUids(match):
                """ Replace Uids
                """
                tag = match.group('tag')
                uid = match.group('uid')
                target = self.resolveuid(context, rc, uid)
                if target is not None:
                    try:
                        url = target.getRemoteUrl()
                    except AttributeError:
                        url = target.absolute_url_path()
                    return tag + url
                return match.group(0)

            html = UID_PATTERN.sub(replaceUids, html)
            if isinstance(html, unicode):
                html = html.encode('utf8') # Indexing requires a string result.
            idata.setData(html)
            return idata

        # No context to use for replacements, so don't bother trying.
        idata.setData(data)
        return idata

def register():
    """ Register
    """
    return ImageSource()
