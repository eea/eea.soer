from Products.CMFCore.utils import getToolByName
import urllib2

def setup_folder_structure(context):
    vocab = getToolByName(context, 'portal_vocabularies')
    european_countries = vocab['eea.soer.vocab.european_countries']
    for country_code in european_countries.keys():
        if hasattr(context, country_code):
            continue
        mapurl = u'http://map.eea.europa.eu/getmap.asp?Fullextent=1&imagetype=3&size=W600&PredefShade=GreenRed&Q=%s:2'
        print 'Creating folder with id %s and title %s' % (country_code, european_countries[country_code].title)
        folder = context[context.invokeFactory('SOERCountry', id=country_code)]
        folder.setTitle(european_countries[country_code].title)
        mapurl = mapurl % country_code
        image = urllib2.urlopen(mapurl)
        image_data = image.read()
        if image_data:
            mapimage = folder[folder.invokeFactory('Image', id='%s_map.png' % country_code,
                                              image=image_data)]
            mapimage.unmarkCreationFlag()
            mapimage.setTitle('Map of %s' % european_countries[country_code].title)
            mapimage.setDescription('Map of %s from %s' % (european_countries[country_code].title, mapurl))
        folder.unmarkCreationFlag()
        folder.reindexObject()
