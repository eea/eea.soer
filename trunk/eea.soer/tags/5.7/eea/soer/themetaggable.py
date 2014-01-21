""" Theme taggable
"""
from zope.component import queryAdapter
from eea.themecentre.interfaces import IThemeTagging

eeaThemes = { u'air pollution' : 'air',
              u'climate change' : 'climate',
              u'land' : 'landuse',
              u'freshwater' : 'water',
              u'waste' : 'waste' }

def reportUpdated(obj, event):
    """ Report updated
    """
    topic = obj.getTopic()
    if topic:
        taggable = queryAdapter(obj, interface=IThemeTagging)
        if taggable is not None:
            eeaTheme = eeaThemes.get(topic, None)
            if eeaTheme is not None and eeaTheme not in taggable.tags:
                taggable.tags = [eeaTheme]
