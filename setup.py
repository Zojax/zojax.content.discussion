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
"""Setup for zojax.content.discussion package

$Id$
"""
import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0'


setup(name='zojax.content.discussion',
      version=version,
      description="Simple content discussion service.",
      long_description=(
          'Detailed Documentation\n' +
          '======================\n'
          + '\n\n' +
          read('CHANGES.txt')
          ),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
      author='Nikolay Kim',
      author_email='fafhrd91@gmail.com',
      url='http://zojax.net/',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'':'src'},
      namespace_packages=['zojax', 'zojax.content'],
      install_requires = ['setuptools', 'rwproperty', 'pytz',
                          'zope.interface',
                          'zope.component',
                          'zope.schema',
                          'zope.proxy',
                          'zope.location',
                          'zope.security',
                          'zope.i18n',
                          'zope.i18nmessageid',
                          'zope.app.security',
                          'zojax.cache',
                          'zojax.layout',
                          'zojax.layoutform',
                          'zojax.activity',
                          'zojax.catalog',
                          'zojax.extensions',
                          'zojax.content.type',
                          'zojax.content.feeds',
                          'zojax.content.browser',
                          'zojax.wizard',
                          'zojax.content.forms',
                          'zojax.content.notifications',
                          'zojax.principal.profile',
                          'zojax.widget.radio',
                          'zojax.statusmessage',
                          'zojax.batching',
                          ],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.app.zcmlfiles',
                                  'zope.securitypolicy',
                                  'zope.testing',
                                  'zope.testbrowser',
                                  'zojax.security',
                                  'zojax.autoinclude',
                                  'zojax.personal.space',
                                  'zojax.content.browser',
                                  'zojax.content.activity',
                                  ]),
      include_package_data = True,
      zip_safe = False
      )
