## Script (Python) "computeBackRelatedItems"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=url,countryCode
##title=create a soer country and test the feed
##

countryCode = countryCode.lower()

if countryCode in context.objectIds():
   country = context[countryCode]
else:
   context.invokeFactory('SOERCountry', id=countryCode)
   country = context[countryCode]

country.setRdfFeed(url)

country.updateFromFeed()
return context.REQUEST.RESPONSE.redirect(country.absolute_url())

