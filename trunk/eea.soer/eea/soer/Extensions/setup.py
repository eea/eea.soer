from eea.soer.vocab import european_country_codes, european_countries


def setup_folder_structure(context):
    for i in european_country_codes:
        id = context.invokeFactory('Folder', id=i)
        folder = context[id]
        title = european_countries[i]
        folder.setTitle(title)
        folder.unmarkCreationFlag()
        folder.reindexObject()
