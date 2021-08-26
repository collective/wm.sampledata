# -*- coding: utf-8 -*-
from DateTime.DateTime import DateTime
from plone import api
from plone import namedfile
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletAssignmentSettings
from plone.portlets.interfaces import IPortletManager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from wm.sampledata.images import get_placeholder_image
from wm.sampledata.images import getFlickrImage
from wm.sampledata.images import getImage
from wm.sampledata.images import getRandomFlickrImage
from wm.sampledata.images import getRandomImage
from wm.sampledata.images import random_dimensions
from zExceptions import BadRequest
from zope import event
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.container.interfaces import INameChooser
from zope.lifecycleevent import ObjectCreatedEvent

import datetime
import os


# Silence flake8
assert getImage
assert getFlickrImage
assert getRandomImage
assert getRandomFlickrImage
assert get_placeholder_image


IPSUM_LINE = "Lorem ipsum mel augue antiopam te. Invidunt constituto accommodare ius cu. Et cum solum liber doming, mel eu quem modus, sea probo putant ex."  # noqa

IPSUM_PARAGRAPH = "<p>" + 10 * IPSUM_LINE + "</p>"


def getFile(module, *path):
    """return the file located in module.
    if module is None, treat path as absolut path
    path can be ['directories','and','file.txt'] or just 'file.txt'
    """
    modPath = ""
    if module:
        modPath = os.path.dirname(module.__file__)

    if type(path) == str:
        path = [path]
    filePath = os.path.join(modPath, *path)
    return open(filePath, "rb")


def getFileContent(module, *path):
    f = getFile(module, *path)
    data = safe_unicode(f.read())
    f.close()
    return data


def deleteItems(folder, *ids):
    """delete items in a folder and don't complain if they do not exist."""
    for itemId in ids:
        try:
            folder.manage_delObjects([itemId])
        except BadRequest:
            pass
        except AttributeError:
            pass


def todayPlusDays(nrDays=0, zopeDateTime=False):
    today = datetime.date.today()
    date = today + datetime.timedelta(days=nrDays)
    if zopeDateTime:
        return DateTime(date.year, date.month, date.day)
    else:
        return date


def eventAndReindex(*objects):
    """fires an ObjectCreatedEvent event and
    reindexes the object(s) after creation so it can be found in the catalog
    """
    for obj in objects:
        event.notify(ObjectCreatedEvent(obj))
        obj.reindexObject()


def addPortlet(context, columnName="plone.leftcolumn", assignment=None):
    if not assignment:
        return
    column = getUtility(IPortletManager, columnName)
    manager = getMultiAdapter((context, column), IPortletAssignmentMapping)
    chooser = INameChooser(manager)
    manager[chooser.chooseName(None, assignment)] = assignment


def removePortlet(context, portletName, columnName="plone.leftcolumn"):
    manager = getUtility(IPortletManager, columnName)
    assignmentMapping = getMultiAdapter((context, manager), IPortletAssignmentMapping)
    # throws a keyerror if the portlet does not exist
    del assignmentMapping[portletName]


def blockPortlets(
    context, columnName="plone.leftcolumn", inherited=None, group=None, contenttype=None
):
    """True will block portlets, False will show them, None will skip settings."""

    manager = getUtility(IPortletManager, name=columnName)
    assignable = getMultiAdapter((context, manager), ILocalPortletAssignmentManager)

    if group is not None:
        assignable.setBlacklistStatus(GROUP_CATEGORY, group)
    if contenttype is not None:
        assignable.setBlacklistStatus(CONTENT_TYPE_CATEGORY, contenttype)
    if inherited is not None:
        assignable.setBlacklistStatus(CONTEXT_CATEGORY, inherited)


def hidePortlet(context, portletName, columnName="plone.leftcolumn"):
    manager = getUtility(IPortletManager, columnName)
    assignmentMapping = getMultiAdapter((context, manager), IPortletAssignmentMapping)
    settings = IPortletAssignmentSettings(assignmentMapping[portletName])
    settings["visible"] = False


def hasPortlet(context, portletName, columnName="plone.leftcolumn"):
    manager = getUtility(IPortletManager, columnName)
    assignmentMapping = getMultiAdapter((context, manager), IPortletAssignmentMapping)
    return portletName in assignmentMapping


def setPortletWeight(portlet, weight):
    """if collective weightedportlets can be imported
    we do set the weight, and do not do anything otherwise
    """
    try:
        from collective.weightedportlets import ATTR
        from persistent.dict import PersistentDict

        if not hasattr(portlet, ATTR):
            setattr(portlet, ATTR, PersistentDict())
        getattr(portlet, ATTR)["weight"] = weight
    except ImportError:
        # simply don't do anything in here
        pass


def createImage(context, id, file_data, **kwargs):
    """create an image and return the object"""
    img = api.content.create(context, "Image", id, **kwargs)
    img.image = namedfile.NamedBlobImage(file_data)
    return img


def createFile(context, id, file_data, **kwargs):
    file = api.content.create(context, "File", id, **kwargs)
    file.file = namedfile.NamedBlobFile(file_data)
    return file


def excludeFromNavigation(obj, exclude=True):
    """excludes the given obj from navigation
    make sure to reindex the object afterwards to make the
    navigation portlet notice the change
    """
    # XXX needs to be revised for plone5
    # plone4 way
    # obj._md["excludeFromNav"] = exclude
    obj.exclude_from_nav = exclude


def doWorkflowTransition(obj, transition):
    """to the workflow transition on the specified object
    we don't use wft.doActionFor directly since this does not set the effective
    data
    """

    doWorkflowTransitions([obj], transition)


def doWorkflowTransitions(objects=[], transition="publish", includeChildren=False):
    """use this to publish a/some folder(s) optionally
    including their child elements
    """

    if not objects:
        return
    if type(objects) != list:
        objects = [
            objects,
        ]

    utils = getToolByName(objects[0], "plone_utils")
    for obj in objects:
        path = "/".join(obj.getPhysicalPath())
        utils.transitionObjectsByPaths(
            workflow_action=transition,
            paths=[path],
            include_children=includeChildren,
        )


# XXX needs to be revised for plone5
def constrainTypes(obj, allowed=[], notImmediate=[]):
    """sets allowed and immediately addable types for obj.

    to only allow news and images and make both immediately addable use::

       constrainTypes(portal.newsfolder, ['News Item', 'Image'])

    if images should not be immediately addable you would use::

       constrainTypes(portal.newsfolder, ['News Item', 'Image'],
                      notImmediate=['Image'])
    """

    obj.setConstrainTypesMode(1)
    obj.setLocallyAllowedTypes(allowed)

    if notImmediate:
        immediate = [type for type in allowed if type not in notImmediate]
    else:
        immediate = allowed
    obj.setImmediatelyAddableTypes(immediate)

