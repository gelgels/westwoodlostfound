#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import cgi
import urllib
import webapp2
import datetime

from google.appengine.ext import db


class Posting(db.Model):
    """ Models a posting on the site """
    title = db.StringProperty()
    desc = db.StringProperty(multiline=True)
    email = db.StringProperty()
    category = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):

        self.response.write("""
            <html>
                <body>
                    <div class="header">
                        Westwood Lost and Found
                    </div>
                    <div class="submit-post">
                        <a href="/submit">Submit a post</a>
                    </div>
        """)

        postings = db.GqlQuery("SELECT * "
                               "FROM Posting "
                               "ORDER BY date DESC LIMIT 10")
        for p in postings:
            self.response.out.write('<div class="post">')
            self.response.out.write('<div class="post-title">%s</div>' % p.title)
            self.response.out.write('<div class="post-desc">%s</div>' % p.desc)
            self.response.out.write('<div class="post-date">%s</div>' % p.date)
            self.response.out.write('<div class="post-category">%s</div>' % p.category)
            self.response.out.write('</div>')

        self.response.write("""
                </body>
            </html>
        """)

class SubmitPostView(webapp2.RequestHandler):
    def get(self):
        self.response.write('Submit a lost or found item below:')
        self.response.write("""
            <html>
                <body>
                    <form action="/submit-post" method="post">
                        <div> <textarea name="title"></textarea> </div>
                        <div> <textarea name="desc"></textarea> </div>
                        <div> <textarea name="email"></textarea> </div>
                        <div> <input type="submit"> </div>
                    </form>
                </body>
            </html>
            """)

class SubmitPost(webapp2.RequestHandler):
    def post(self):
        p = Posting()
        p.title = self.request.get('title')
        p.desc = self.request.get('desc')
        p.email = self.request.get('email')
        p.category = 'lost'
        p.put()

        self.response.out.write("Your posting about %s has been posted." % self.request.get('title'))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/submit', SubmitPostView),
    ('/submit-post', SubmitPost)
], debug=True)
