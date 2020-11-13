#!/usr/bin/python
# -*- coding: utf-8 -*-


# Copyright (C) 2014 <bernd@bzed.de>
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, http.cookiejar, tempfile, os

class DokuWikiFukker:

    def __init__(self, doku_php, user, password, jarfile = os.path.join(os.path.expanduser("~"), '.config', '.dwfukker')):
        self.doku_php = doku_php
        self.jarfile = jarfile
        self.user = user
        self.password = password
        self.jar = http.cookiejar.LWPCookieJar(jarfile)
        try:
            self.jar.load()
        except IOError:
            pass

        self.login()


    def __dw_soup__(self, form_data):
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        resp = opener.open(self.doku_php, urllib.parse.urlencode(form_data).encode("utf-8"))
        html_doc = resp.read()
        soup = BeautifulSoup(html_doc, features="lxml")
        return soup


    def login(self):
        soup = self.__dw_soup__({ 'do' : 'login' })

        login_form_html=soup.find('form', id="dw__login")
        if not login_form_html:
            # jar seems to exist and we are logged in.
            return
        login_data={}
        for form_input in login_form_html.find_all('input'):
            if (form_input.has_attr('name') and form_input.has_attr('value')):
                login_data[form_input['name']]=form_input['value']
        login_data['u']=self.user
        login_data['p']=self.password

        soup =  self.__dw_soup__(login_data)

        self.jar.save()


    def edit(self, page, content=None, replace_function=None):

        soup = self.__dw_soup__({ 'do' : 'edit', 'id' : page })
        edit_form_html=soup.find('form', id='dw__editform')
        edit_data={}
        edit_data['wikitext'] = edit_form_html.find('textarea').string.strip()
        for form_input in edit_form_html.find_all('input'):
            if (form_input.has_attr('class')):
                # buttons...
                continue
            if (form_input.has_attr('name') and form_input.has_attr('value')):
                edit_data[form_input['name']]=form_input['value']
        if content:
            edit_data['wikitext']=content
        if replace_function:
            edit_data['wikitext']=replace_function(edit_data['wikitext'])
        edit_data['do']='save'
        soup = self.__dw_soup__(edit_data)
        # retrieve new page once
        soup = self.__dw_soup__({ 'id' : page })

