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
from zope.i18nmessageid import MessageFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

_ = MessageFactory('zojax.content.discussion')


commentPolicyVocabulary = SimpleVocabulary(
    [SimpleTerm(1, 'open', 'Open'),
     SimpleTerm(2, 'closed', 'Closed'),
     SimpleTerm(3, 'disabled', 'Disabled')])

commentPolicyVocabulary.getTerm(1).description = _(
    'Comments are allowed.')
commentPolicyVocabulary.getTerm(2).description = _(
    'Existing comments will be displayed, new comments are not allowed.')
commentPolicyVocabulary.getTerm(3).description = _(
    'Comments will not be displayed, new comments are not allowed.')

postCommentPositionVocabulary = SimpleVocabulary(
    [SimpleTerm(1, 'under', _('Under comments')),
     SimpleTerm(2, 'above', _('Above comments'))])

commentsOrderVocabulary = SimpleVocabulary(
    [SimpleTerm(1, 'direct', _('Direct order')),
     SimpleTerm(2, 'reversed', _('Reverse order'))])
