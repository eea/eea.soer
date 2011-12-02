""" EEA SOER package
"""
from Products.Archetypes.atapi import listTypes, process_types
from Products.CMFCore import utils as cmfutils
from eea.soer.config import ADD_CONTENT_PERMISSION, PROJECTNAME

def initialize(context):
    """ Initialize
    """

    # Initialize portal content
    all_content_types, all_constructors, all_ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = all_content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = all_constructors,
        fti                = all_ftis,
        ).initialize(context)

    #TODO: plone4, investigate below code
    ## Give it some extra permissions to control them on a per class limit
    #for i in range(0, len(all_content_types)):
        #context.registerClass(meta_type   = all_ftis[i]['meta_type'],
                              #constructors= (all_constructors[i],),
                              #permission  = ADD_CONTENT_PERMISSION)
