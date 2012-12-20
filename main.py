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
import os
import cgi
import time
import jinja2
import urllib
import webapp2
import datetime

from google.appengine.ext import db

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Posting(db.Model):
    """ Models a posting on the site """
    title = db.StringProperty()
    desc = db.StringProperty(multiline=True)
    email = db.StringProperty()
    category = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        postings = db.GqlQuery("SELECT * "
                               "FROM Posting "
                               "ORDER BY date DESC LIMIT 10")

        template_values = {
            'postings' : postings
        }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

class SubmitPostView(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('submit.html')
        self.response.out.write(template.render())

class SubmitPost(webapp2.RequestHandler):
    def post(self):
        p = Posting()
        p.title = self.request.get('title')
        p.desc = self.request.get('desc')
        p.email = self.request.get('email')
        p.category = 'lost'
        p.put()

        self.response.out.write("Your posting about %s has been posted." % self.request.get('title'))

class LostItemsView(webapp2.RequestHandler):
    def get(self):
        postings = db.GqlQuery("SELECT * FROM Posting WHERE category = 'lost'")
        template_values = {
            'postings' : postings
        }
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

class FoundItemsView(webapp2.RequestHandler):
    def get(self):
        postings = db.GqlQuery("SELECT * FROM Posting WHERE category = 'found'")
        template_values = {
            'postings' : postings
        }
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

class PostView(webapp2.RequestHandler):
    def get(self):
        id_arg = self.request.get('id')
        post = Posting.get_by_id(int(id_arg))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/post', PostView),
    ('/lost', LostItemsView),
    ('/found', FoundItemsView),
    ('/submit', SubmitPostView),
    ('/submit-post', SubmitPost)
], debug=True)
