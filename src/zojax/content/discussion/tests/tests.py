##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" zojax.principal.profile tests

$Id$
"""
import os, unittest, doctest

from mock import Mock

from zope import interface, component, event
from zope.app.testing import functional
from zope.app.component.hooks import setSite
from zope.app.rotterdam import Rotterdam
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectCreatedEvent
from zojax.ownership.interfaces import IOwnership
from zojax.content.space.interfaces import ISpace
from zojax.layoutform.interfaces import ILayoutFormLayer
from zojax.activity.interfaces import IActivityAware
from zojax.content.type.interfaces import IItem
from zojax.content.type.item import PersistentItem
from zojax.catalog.catalog import Catalog, ICatalog
from zojax.personal.space.manager import PersonalSpaceManager, IPersonalSpaceManager

from zojax.widget.captcha.validator import CaptchaValidator


zojaxContentDiscussionLayer = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'zojaxContentDiscussionLayer', allow_teardown=True)


class IContent(IItem):
    """ content """


class Content(PersistentItem):
    interface.implements(IContent, IActivityAware)

CaptchaValidator.validate = Mock(return_value=True)

def FunctionalDocFileSuite(*paths, **kw):
    layer = zojaxContentDiscussionLayer

    globs = kw.setdefault('globs', {})
    globs['http'] = functional.HTTPCaller()
    globs['getRootFolder'] = functional.getRootFolder
    globs['sync'] = functional.sync

    kw['package'] = doctest._normalize_module(kw.get('package'))

    kwsetUp = kw.get('setUp')
    def setUp(test):
        functional.FunctionalTestSetup().setUp()

        root = functional.getRootFolder()
        setSite(root)
        sm = root.getSiteManager()

        # IIntIds
        root['ids'] = IntIds()
        sm.registerUtility(root['ids'], IIntIds)
        root['ids'].register(root)

        # catalog
        root['catalog'] = Catalog()
        sm.registerUtility(root['catalog'], ICatalog)

        # personal space manager
        root['people'] = PersonalSpaceManager()
        sm.registerUtility(root['people'], IPersonalSpaceManager)

        # default content
        content = Content()
        event.notify(ObjectCreatedEvent(content))
        IOwnership(content).ownerId = 'zope.user'
        root['content'] = content

    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')
    def tearDown(test):
        setSite(None)
        functional.FunctionalTestSetup().tearDown()

    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        #old = doctest.set_unittest_reportflags(0)
        #doctest.set_unittest_reportflags(old)
        kw['optionflags'] = (doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)

    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = layer
    return suite


class IDefaultSkin(ILayoutFormLayer, Rotterdam):
    """ skin """


def test_suite():
    return unittest.TestSuite((
            FunctionalDocFileSuite("testbrowser.txt"),
            FunctionalDocFileSuite("twitter.txt"),
            FunctionalDocFileSuite("facebook.txt"),
            ))
