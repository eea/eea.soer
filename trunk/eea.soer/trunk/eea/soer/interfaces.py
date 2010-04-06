from zope.interface import Interface

class IArchetype2Surf(Interface):


    def save():
        """ create and save a SuRF Resource.
            return the resource. """
