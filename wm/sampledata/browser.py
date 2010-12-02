from Products.Five.browser import BrowserView
from zope.component import getUtilitiesFor, getUtility
from wm.sampledata.interfaces import ISampleDataPlugin
from Products.statusmessages.interfaces import IStatusMessage
from zope.component.interfaces import ComponentLookupError


class SampleDataView(BrowserView):

    def listPlugins(self):
        plugins = []
        for name, util in getUtilitiesFor(ISampleDataPlugin):
            plugins.append(dict(name=name,
                                title = util.title,
                                description=util.description))

        return plugins
    
    def runPlugin(self,plugin):
        try:
            plugin = getUtility(ISampleDataPlugin,name=plugin)
            plugin.generate(self.context)
            IStatusMessage(self.request).addStatusMessage(u"successfully ran %s" % plugin.title , 'info')
        except ComponentLookupError:
            IStatusMessage(self.request).addStatusMessage(u"could not find plugin %s" % plugin , 'error')
        except Exception, e:
            IStatusMessage(self.request).addStatusMessage(u"error running %s: %s" % (plugin.title, str(e)) , 'error')
        finally:
            #return to listing
            self.request.response.redirect(self.context.absolute_url() + '/'  + self.__name__)

        
        
