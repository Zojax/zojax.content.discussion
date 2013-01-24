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
from zope.component import getUtilitiesFor
from zope import interface
from zope.schema.interfaces import IVocabularyFactory
from zope.i18nmessageid import MessageFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from zojax.content.type.interfaces import IPortalType


_ = MessageFactory('zojax.content.discussion')

def commentPolicyVocabulary(context):
    """ returns Policy for discussion
    """
    vocab = SimpleVocabulary([
        SimpleTerm(1, 'open', 'Open'),
        SimpleTerm(4, 'approval', 'Open with approval'),
        SimpleTerm(2, 'closed', 'Closed'),
        SimpleTerm(3, 'disabled', 'Disabled')])

    vocab.getTerm(1).description = _(
        'Comments are allowed.')
    vocab.getTerm(2).description = _(
        'Existing comments will be displayed, new comments are not allowed.')
    vocab.getTerm(3).description = _(
        'Comments will not be displayed, new comments are not allowed.')
    vocab.getTerm(4).description = _(
        'Comments are allowed but require approval for non auth users.')

    return vocab

postCommentPositionVocabulary = SimpleVocabulary(
    [SimpleTerm(1, 'under', _('Under comments')),
     SimpleTerm(2, 'above', _('Above comments'))])

commentsOrderVocabulary = SimpleVocabulary(
    [SimpleTerm(1, 'direct', _('Direct order')),
     SimpleTerm(2, 'reversed', _('Reverse order'))])


class PortletTypesVocabulary(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        pt = []

        for name, ct in getUtilitiesFor(IPortalType, context=context):
            pt.append((ct.title, name))

        pt.sort()

        return SimpleVocabulary(
            [SimpleTerm('__all__', '__all__', _('All portal types'))] +
            [SimpleTerm(name, name, title) for title, name in pt])
