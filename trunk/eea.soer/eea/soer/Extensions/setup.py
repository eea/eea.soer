from eea.soer.vocab import european_country_codes


def setup_folder_structure(context):
    for i in european_country_codes:
        context.invokeFactory('Folder', id=i)
