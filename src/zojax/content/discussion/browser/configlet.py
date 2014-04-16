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
"""

$Id$
"""

from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.proxy import removeAllProxies
from zope.traversing.browser import absoluteURL

from zope.app.security.interfaces import IAuthentication
#from zojax.batching.batch import Batch
from zojax.catalog.utils import getRequest
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.wizard.step import WizardStep

from ..catalog import getCatalog
#from ..configlet import logger
from ..interfaces import _


class NotApprovedCommentsView(WizardStep):

    title = _(u'Not Approved Comments')
    label = _(u'Here you can manage not approved comments')

    def update(self):
        super(NotApprovedCommentsView, self).update()

        request = self.request
        context = removeAllProxies(self.context)

        if context is None:
            return

        ids = getUtility(IIntIds)
        oids = request.get('form.checkbox.id', ())

        if 'form.button.remove' in request:
            if not oids:
                IStatusMessage(request).add(
                    _('You have not selected any comment.'), 'warning')
            else:
                for oid in oids:
                    try:
                        comment = ids.getObject(int(oid))
                        del comment.__parent__[comment.__name__]
                    except KeyError:
                        pass

                IStatusMessage(request).add(_('Selected comments have been removed.'))

        elif 'form.button.approve' in request:
            if not oids:
                IStatusMessage(request).add(
                    _('You have not selected any comment.'), 'warning')
            else:
                for oid in oids:
                    comment = ids.getObject(int(oid))
                    comment.approved = True
                    notify(ObjectModifiedEvent(comment))

                IStatusMessage(request).add(_('Selected comments have been approved.'))

        catalog = getCatalog()
        self.results = catalog.search(approved=(False,))

        # TODO: return all unapproved comments with Batch help
        #self.batch = Batch(results, size=20, context=context, request=request)

    def getInfo(self, comment):

        author = ''
        author_url = ''

        if getattr(comment, 'authorName'):
            author = comment.authorName

        elif comment.author is not None:
            try:
                author = getUtility(IAuthentication).getPrincipal(comment.author)
            except:
                author = None

            profile = IPersonalProfile(author, None)
            if profile is not None:
                author = profile.title

                if profile.space is not None:
                    author_url = absoluteURL(profile.space, getRequest())

        oid = getUtility(IIntIds).getId(comment)

        return dict(author=author, author_url=author_url, oid=oid)


class ApprovedCommentsView(NotApprovedCommentsView):

    title = _(u'Approved Comments')
    label = _(u'Here you can manage already approved comments')

    def update(self):
        super(ApprovedCommentsView, self).update()

        request = self.request
        context = removeAllProxies(self.context)

        if context is None:
            return

        ids = getUtility(IIntIds)
        oids = request.get('form.checkbox.id', ())

        if 'form.button.remove' in request:
            if not oids:
                IStatusMessage(request).add(
                    _('You have not selected any comment.'), 'warning')
            else:
                for oid in oids:
                    try:
                        comment = ids.getObject(int(oid))
                        del comment.__parent__[comment.__name__]
                    except KeyError:
                        pass

                IStatusMessage(request).add(_('Selected comments have been removed.'))

        elif 'form.button.reject' in request:
            if not oids:
                IStatusMessage(request).add(
                    _('You have not selected any comment.'), 'warning')
            else:
                for oid in oids:
                    comment = ids.getObject(int(oid))
                    comment.approved = False
                    notify(ObjectModifiedEvent(comment))

                IStatusMessage(request).add(_('Selected comments have been rejected.'))

        catalog = getCatalog()
        self.results = catalog.search(approved=(True,))

        # TODO: return all approved comments with Batch help
        #self.batch = Batch(results, size=20, context=context, request=request)


