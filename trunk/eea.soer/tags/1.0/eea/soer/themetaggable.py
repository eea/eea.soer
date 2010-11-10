from zope.component import queryAdapter
from eea.themecentre.interfaces import IThemeTagging

eeaThemes = { u'air pollution' : [u'air'],
              u'climate change' : [u'climate'],
              u'land' : [u'landuse',u'soil', u'waste'],
              u'freshwater' : [u'water'],
              u'waste' : [u'waste'] }

def reportUpdated(obj, event):
    topic = obj.getTopic()
    if topic:
        taggable = queryAdapter(obj, interface=IThemeTagging)
        if taggable is not None:
            eeaTheme = eeaThemes.get(topic, None)
            if eeaTheme is not None:
                taggable.tags = eeaTheme
            
