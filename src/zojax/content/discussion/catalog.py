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
from zope import interface, event, component
from zope.app.catalog import catalog
from zope.component import getUtility
from zope.proxy import removeAllProxies
from zope.app.component.hooks import getSite
from zope.app.intid.interfaces import \
    IIntIds, IIntIdAddedEvent, IIntIdRemovedEvent
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from zc.catalog.catalogindex import SetIndex, ValueIndex

from zojax.catalog.interfaces import ISortable
from zojax.catalog.result import ResultSet, ReverseResultSet
from zojax.catalog.index import DateTimeValueIndex
from zojax.catalog.utils import getAccessList, getRequest, listAllowedRoles

from interfaces import IComment, ICommentsCatalog


class CommentsCatalog(catalog.Catalog):
    interface.implements(ICommentsCatalog)

    def index_doc(self, docid, texts):
        if not IComment.providedBy(texts):
            return

        for index in self.values():
            index.index_doc(docid, texts)

    def updateIndex(self, index):
        for uid, obj in self._visitSublocations():
            if IComment.providedBy(obj):
                index.index_doc(uid, obj)

    def updateIndexes(self):
        for uid, obj in self._visitSublocations():
            if IComment.providedBy(obj):
                for index in self.values():
                    index.index_doc(uid, obj)

    def search(self, content=None,
               contexts=(), sort_on='date', sort_order='reverse'):
        ids = getUtility(IIntIds)

        query = {}

        # comments for content
        if content:
            query['content'] = {'any_of':(ids.getId(removeAllProxies(content)),)}

        # context
        if contexts:
            c = []
            for context in contexts:
                id = ids.queryId(removeAllProxies(context))
                if id is not None:
                    c.append(id)

            query['contexts'] = {'any_of': c}

        # security
        users = listAllowedRoles(getRequest().principal, getSite())
        if 'zope.Anonymous' not in users:
            users.append('zope.Anonymous')

        query['access'] = {'any_of': users}

        # apply searh terms
        results = self.apply(query)
        if results is None:
            results = IFBTree()

        # sort result by index
        if sort_on and sort_on in self:
            sortable = ISortable(self[sort_on], None)
            if sortable is not None:
                results = sortable.sort(results)

        if sort_order == 'reverse':
            return ReverseResultSet(results, ids)
        else:
            return ResultSet(results, ids)


def getCatalog():
    sm = getSite().getSiteManager()

    if 'commentsCatalog' in sm:
        return sm['commentsCatalog']

    else:
        catalog = CommentsCatalog()
        event.notify(ObjectCreatedEvent(catalog))
        removeAllProxies(sm)['commentsCatalog'] = catalog

        return sm['commentsCatalog']


@component.adapter(IComment, IIntIdAddedEvent)
def commentAdded(comment, ev):
    comment = removeAllProxies(comment)
    catalog = removeAllProxies(getCatalog())
    catalog.index_doc(getUtility(IIntIds).getId(comment), comment)


@component.adapter(IComment, IIntIdRemovedEvent)
def commentRemoved(comment, ev):
    comment = removeAllProxies(comment)
    catalog = removeAllProxies(getCatalog())
    catalog.unindex_doc(getUtility(IIntIds).getId(comment))


@component.adapter(ICommentsCatalog, IObjectAddedEvent)
def handleCatalogAdded(catalog, ev):
    if 'author' not in catalog:
        catalog['author'] = ValueIndex('author')
    if 'access' not in catalog:
        catalog['access'] = SetIndex('value', IndexableSecurityInformation)
    if 'date' not in catalog:
        catalog['date'] = DateTimeValueIndex('date', resolution=4)
    if 'content' not in catalog:
        catalog['content'] = ValueIndex('value', IndexableContent)
    if 'contexts' not in catalog:
        catalog['contexts'] = SetIndex('value', IndexableContexts)


class IndexableSecurityInformation(object):

    def __init__(self, comment, default=None):
        self.value = getAccessList(
            removeAllProxies(comment.content), 'zope.View')


class IndexableContent(object):

    def __init__(self, comment, default=None):
        self.value = getUtility(IIntIds).getId(
            removeAllProxies(comment.content))


class IndexableContexts(object):

    def __init__(self, comment, default=None):
        values = []
        ids = getUtility(IIntIds)

        context = removeAllProxies(comment.content)
        while context is not None:
            values.append(ids.queryId(context))

            context = removeAllProxies(
                getattr(context, '__parent__', None))

        self.value = values
