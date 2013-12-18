from os.path import dirname
from Globals import package_home
from Products.Archetypes.atapi import listTypes, process_types
#from Products.Archetypes.atapi import *
from Products.CMFCore import utils as cmfutils
from Products.CMFCore.DirectoryView import registerDirectory
#from eea.soer import content
from eea.soer.config import ADD_CONTENT_PERMISSION, PROJECTNAME


# Register skin
GLOBALS = globals()
ppath = cmfutils.ProductsPath
cmfutils.ProductsPath.append(dirname(package_home(GLOBALS)))
registerDirectory('skins', GLOBALS)
cmfutils.ProductsPath = ppath


def initialize(context):

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

    # Give it some extra permissions to control them on a per class limit
    for i in range(0, len(all_content_types)):
        context.registerClass(meta_type   = all_ftis[i]['meta_type'],
                              constructors= (all_constructors[i],),
                              permission  = ADD_CONTENT_PERMISSION)