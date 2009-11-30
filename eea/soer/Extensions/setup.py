from Products.CMFCore.utils import getToolByName


def setup_folder_structure(context):
    vocab = getToolByName(context, 'portal_vocabularies')
    european_countries = vocab['eea.soer.vocab.european_countries']
    for country_code in european_countries.keys():
        print 'Creating folder with id %s and title %s' % (country_code, european_countries[country_code].title)
        folder = context[context.invokeFactory('Folder', id=country_code)]
        folder.setTitle(european_countries[country_code].title)
        folder.unmarkCreationFlag()
        folder.reindexObject()
