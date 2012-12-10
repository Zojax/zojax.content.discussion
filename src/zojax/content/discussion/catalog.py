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
from zope.lifecycleevent.interfaces import IObjectCreatedEvent, IObjectModifiedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from zc.catalog.catalogindex import SetIndex, ValueIndex

from zojax.content.type.interfaces import IContentType
from zojax.catalog.interfaces import ISortable, ICatalogIndexFactory
from zojax.catalog.result import ResultSet, ReverseResultSet
from zojax.catalog.index import DateTimeValueIndex
from zojax.catalog.utils import getAccessList, getRequest, listAllowedRoles

from interfaces import IComment, ICommentsCatalog


class CommentsCatalog(catalog.Catalog):
    interface.implements(ICommentsCatalog)

    def createIndex(self, name, factory):
        index = factory()
        event.notify(ObjectCreatedEvent(index))
        self[name] = index

        return self[name]

    def getIndex(self, indexId):
        if indexId in self:
            return self[indexId]

        return self.createIndex(
            indexId, getAdapter(self, ICatalogIndexFactory, indexId))

    def getIndexes(self):
        names = []

        for index in super(CommentsCatalog, self).values():
            names.append(removeAllProxies(index.__name__))
            yield index

        for name, indexFactory in component.getAdapters((self,), ICatalogIndexFactory):
            if name not in names:
                yield self.createIndex(name, indexFactory)

    def values(self):
        return self.getIndexes()

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
               contexts=(), sort_on='date', sort_order='reverse', types=(), approved=()):
        ids = getUtility(IIntIds)
        indexes = list(self.values())

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

        # content type
        if types:
            query['type'] = {'any_of': types}

        # security
        users = listAllowedRoles(getRequest().principal, getSite())
        if 'zope.Anonymous' not in users:
            users.append('zope.Anonymous')

        query['access'] = {'any_of': users}

        # comments approved
        if approved:
            query['approved'] = {'any_of': approved}

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


#@component.adapter(IComment, IObjectAddedEvent)
@component.adapter(IComment, IIntIdAddedEvent)
def commentAdded(comment, ev):
    comment = removeAllProxies(comment)
    catalog = removeAllProxies(getCatalog())
    catalog.index_doc(getUtility(IIntIds).getId(comment), comment)


@component.adapter(IComment, IObjectModifiedEvent)
def commentModified(comment, ev):
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
    list(catalog.getIndexes())

class Factory(object):
    component.adapts(ICommentsCatalog)
    interface.implements(ICatalogIndexFactory)

    def __init__(self, catalog):
        self.catalog = catalog


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


class AuthorIndex(Factory):
    def __call__(self):
        return ValueIndex('author')


class AccessIndex(Factory):
    def __call__(self):
        return SetIndex('value', IndexableSecurityInformation)


class DateIndex(Factory):
    def __call__(self):
        return DateTimeValueIndex('date', resolution=4)


class ContentIndex(Factory):
    def __call__(self):
        return ValueIndex('value', IndexableContent)


class ContextsIndex(Factory):
    def __call__(self):
        return SetIndex('value', IndexableContexts)

class TypeIndex(Factory):
    def __call__(self):
        return ValueIndex('value', IndexableType)

class IndexableType(object):

    def __init__(self, comment, default=None):
        try:
            self.value = IContentType(removeAllProxies(comment.content), None).name
        except AttributeError:
            self.value = default

class ApprovedIndex(Factory):
    def __call__(self):
        return ValueIndex('approved')
