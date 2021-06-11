# -*- coding: utf-8 -*-
from plone import api
from plone.app.textfield import RichTextValue
from plone.portlet.static.static import Assignment as StaticAssignment
from wm.sampledata.interfaces import ISampleDataPlugin
from wm.sampledata.utils import addPortlet
from wm.sampledata.utils import createImage
from wm.sampledata.utils import deleteItems
from wm.sampledata.utils import doWorkflowTransitions
from wm.sampledata.utils import eventAndReindex
from wm.sampledata.utils import getFileContent
from wm.sampledata.utils import getRandomImage
from wm.sampledata.utils import IPSUM_PARAGRAPH
from zope.interface import implementer


@implementer(ISampleDataPlugin)
class DemoContent(object):

    title = "Demo Content"

    description = """Creates a document with an image and assigns a portlet
that displays contact information."""

    def generate(self, context):
        pageId = "sample"

        # delete sample document if it exists
        deleteItems(context, pageId)
        site = api.portal.get()
        page = api.content.create(site, "Document", pageId, title="Sample Document")

        # download image from lorempixel.com - force colour images from
        # category nature
        imageId = "sampleImage"
        deleteItems(context, imageId)
        createImage(
            context,
            imageId,
            getRandomImage(category="nature", gray=False),
            title="Random Image",
            description="Downloaded from lorempixel.com",
        )

        text = (
            f"""<img class="image-right" src="{imageId}/@@images/image/mini" />
        <p>And now to something completely different:</p>
        """
            + IPSUM_PARAGRAPH
        )

        # mimetype makes tiny recognize the text as HTML
        page.text = RichTextValue(text, "text/html", "text/html")

        # publish and reindex (needed to make it show up in the navigation) the
        # page
        doWorkflowTransitions(page)
        eventAndReindex(page)

        import wm.sampledata.example as myModule

        portlet = StaticAssignment("Contact", getFileContent(myModule, "portlet.html"))
        addPortlet(page, "plone.leftcolumn", portlet)

        return "successfully ran democontent plugin"
