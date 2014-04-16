#
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
#
"""

$Id$
"""
import time
import urllib
import oauth2 as oauth
import simplejson as json

from zope.app.http.httpdate import build_http_date
from zope.component import getUtility
from zope.traversing.browser import absoluteURL

from ..interfaces import ITwitterCommentingConfig, IFacebookCommentingConfig


# urls for twitter
access_token_url = "https://api.twitter.com/oauth/access_token"
request_token_url = "https://api.twitter.com/oauth/request_token"
authorize_url = "https://twitter.com/oauth/authorize"
show_url = "https://api.twitter.com/1.1/users/show.json?screen_name="

# urls for facebook
fb_authorize_url = "https://graph.facebook.com/oauth/authorize?"
fb_access_token_url = "https://graph.facebook.com/oauth/access_token?"
fb_show_url = "https://graph.facebook.com/me?"
fb_logout_url = "https://www.facebook.com/logout.php?"


def _parse_qsl(url):
    """
    Parse_qsl method.
    for python 2.5
    """
    param = {}
    for i in url.split('&'):
        # p = i.rsplit("=")
        p = i.split('=')
        try:
            param.update({p[0]: p[1]})
        except:
            raise Exception('Invalid response: %s' % param)
    return param


def _expire_time(period):
    """
    period = 30000000 #347 days
    period = 1800 #30 min
    """
    return build_http_date(time.time() + period)


class Twitter(object):

    def update(self):
        context, request = self.context, self.request

        configlet = getUtility(ITwitterCommentingConfig)

        consumer = oauth.Consumer(
            key=configlet.apiKey, secret=configlet.apiSecret)

        if not 'oauth_verifier' in request.keys() or 'logout' in request.keys():

            # step1: Get a request token

            client = oauth.Client(consumer)
            token = oauth.Token(
                key=configlet.apiKey, secret=configlet.apiSecret)

            params = {
                'oauth_version': "1.0",
                'oauth_callback': absoluteURL(self, request),
                'oauth_nonce': oauth.generate_nonce(),
                'oauth_timestamp': int(time.time()),
                'oauth_signature_method': "HMAC-SHA1",
                'oauth_consumer_key': token.key,
                'oauth_signature': consumer.key,
            }
            resp, content = client.request(
                request_token_url, "POST", urllib.urlencode(params))
            if resp.status != 200:
                raise Exception('Invalid response %s' % resp['status'])

            request_token = dict(_parse_qsl(content))

            exptime = _expire_time(1800)  # 30 min

            request.response.setCookie(
                'auth_token', request_token['oauth_token'], expires=exptime)
            request.response.setCookie(
                'auth_token_secret', request_token['oauth_token_secret'], expires=exptime)

            # step2 Redirect to the provider

            url = '%s?oauth_token=%s' % (
                authorize_url, request_token['oauth_token'])

            if 'logout' in request.keys():
                request.response.setCookie(
                    'force_authorise', 'true', expires=exptime)
                url += '&force_login=true'

            request.response.redirect(url)

        if 'oauth_verifier' in self.request.keys():

            # step3: Get an access token

            token = oauth.Token(
                self.request['auth_token'], self.request['auth_token_secret'])
            token.set_verifier(self.request['oauth_verifier'])
            client = oauth.Client(consumer, token)

            resp, content = client.request(access_token_url, "POST")
            if resp.status != 200:
                raise Exception(
                    'Invalid response: %s - %s' % (resp['status'], content))

            access_token = dict(_parse_qsl(content))

            twname = access_token['screen_name']

            exptime = _expire_time(30000000)  # 347 days

            self.request.response.setCookie(
                'screen_name', twname, expires=exptime)
            self.request.response.setCookie(
                'user_id', access_token['user_id'], expires=exptime)

            # step4: get user's real name

            client = oauth.Client(consumer)

            resp, content = client.request(
                show_url + access_token['screen_name'], 'GET')
            if resp.status == 200:
                twname = json.loads(content)['name']

            self.request.response.setCookie('tw_name', twname, expires=exptime)


class Facebook(object):

    def update(self):
        context, request = self.context, self.request

        configlet = getUtility(IFacebookCommentingConfig)

        params = {
            'client_id': configlet.appID,
            'redirect_uri': absoluteURL(self, request)
        }

        if 'logout' in self.request.keys():
            params['redirect_uri'] += '?logout=true'

        # step1: log in at facebook

        if not 'code' in self.request.keys():
            request.response.redirect(
                fb_authorize_url + urllib.urlencode(params))

        # step2: authorize App and grants necessary permissions

        if 'code' in self.request.keys():
            params["client_secret"] = configlet.appSecret
            params["code"] = self.request.get("code")

            response = dict(
                _parse_qsl(urllib.urlopen(fb_access_token_url + urllib.urlencode(params)).read()))

            access_token = response["access_token"]

            if not access_token:
                raise Exception('Invalid response from Facebook')

            if 'logout' in self.request.keys():
                request.response.expireCookie('fb_author')
                request.response.expireCookie('facebook_id')
                # request.response.expireCookie('fb_author_url')
                url = fb_logout_url + \
                    "next=%s&access_token=%s" % (
                        absoluteURL(self, request), access_token)
                request.response.redirect(url)

            # step3: make call to GraphAPI and get required user info

            profile = json.load(
                urllib.urlopen(fb_show_url + urllib.urlencode(dict(access_token=access_token))))

            exptime = _expire_time(30000000)  # 347 days

            self.request.response.setCookie(
                'fb_author', profile["name"], expires=exptime)
            self.request.response.setCookie(
                'facebook_id', str(profile["id"]), expires=exptime)
            # self.request.response.setCookie(
            #    'fb_author_url', str(profile["link"]), expires=exptime)
