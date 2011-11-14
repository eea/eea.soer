from eea.facetednavigation.subtypes.descriptors import FacetedNavigableDescriptor
from eea.faceted.inheritance.subtypes.descriptors import FacetedHeritorDescriptor

class FolderFacetedNavigableDescriptor(FacetedNavigableDescriptor):
    """ Folder descriptor
    """
    for_portal_type = 'SOERCountry'

class FolderFacetedHeritorDescriptor(FacetedHeritorDescriptor):
    """ Folder descriptor
    """
    for_portal_type = 'SOERCountry'
