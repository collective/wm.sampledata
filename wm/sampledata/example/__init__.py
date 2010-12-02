from zope.interface.declarations import implements
from wm.sampledata.interfaces import ISampleDataPlugin
from wm.sampledata.utils import addPortlet, getFileContent, IPSUM_PARAGRAPH,\
    deleteItems, eventAndReindex
from plone.portlet.static.static import Assignment as StaticAssignment
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName

class DemoContent(object):
    implements(ISampleDataPlugin)
    
    title = u"Demo Content"
    
    description = u"Creates a document and assigns a portlet that displays contact information."
    
    def generate(self, context):
        
        #delete sample document if it exists
        deleteItems(context, ['sample'])
        #create it w/o security checks
        _createObjectByType('Document', context, id='sample', title="SampleDocument",
                            text=IPSUM_PARAGRAPH)
        
        docPath=context['sample'].getPhysicalPath()
        utils = getToolByName(context, 'plone_utils')
        utils.transitionObjectsByPaths(workflow_action='publish', paths=[docPath], include_children=False,)        
        eventAndReindex(context, 'sample')
        
        
        import wm.sampledata.example as myModule
        portlet = StaticAssignment(u"Contact", getFileContent(myModule, 'portlet.html'))
                
        addPortlet(context['sample'], 'plone.leftcolumn', portlet)