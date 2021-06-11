# -*- coding: utf-8 -*-
from plone.portlet.static.static import Assignment as StaticAssignment
from zope.interface import implementer

from wm.sampledata.interfaces import ISampleDataPlugin
from wm.sampledata.utils import addPortlet
from wm.sampledata.utils import createImage
from wm.sampledata.utils import deleteItems
from wm.sampledata.utils import doWorkflowTransitions
from wm.sampledata.utils import eventAndReindex
from wm.sampledata.utils import getFileContent
from wm.sampledata.utils import getRandomImage
from wm.sampledata.utils import IPSUM_PARAGRAPH


@implementer(ISampleDataPlugin)
class DemoContent(object):

    title = "Demo Content"

    description = """Creates a document with an image and assigns a portlet
that displays contact information."""

    def generate(self, context):
        pageId = 'sample'

        # delete sample document if it exists
        deleteItems(context, pageId)

        context.invokeFactory('Document', id=pageId, title="Sample Document")
        page = context[pageId]

        # download image from lorempixel.com - force colour images from
        # category nature
        imageId = 'sampleImage'
        deleteItems(context, imageId)
        createImage(context, imageId, +
                    getRandomImage(category='nature', gray=False),
                    title="Random Image",
                    description="Downloaded from lorempixel.com")

        text = '<img class="image-right" src="%s/@@images/image/mini" />' % (
            imageId) + IPSUM_PARAGRAPH

        # mimetype makes tiny recognize the text as HTML
        page.setText(text, mimetype='text/html')

        # publish and reindex (needed to make it show up in the navigation) the
        # page
        doWorkflowTransitions(page)
        eventAndReindex(page)

        import wm.sampledata.example as myModule
        portlet = StaticAssignment(
            "Contact", getFileContent(myModule, 'portlet.html'))
        addPortlet(page, 'plone.leftcolumn', portlet)
