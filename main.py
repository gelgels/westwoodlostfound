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
import logging
import webapp2
import datetime
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import mail

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class Posting(db.Model):
    """ Models a posting on the site """
    title = db.StringProperty()
    desc = db.StringProperty(multiline=True)
    email = db.StringProperty()
    category = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    allow_contact = db.BooleanProperty()

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

        spam_check = self.request.get('spam-check')

        if spam_check:
            logging.info('Spam post submitted')

            template_values = {
                'success'   : False
            }

        else:
            p = Posting()
            p.title     = strip_tags(self.request.get('title'))
            p.desc      = strip_tags(self.request.get('desc'))
            p.email     = strip_tags(self.request.get('email'))
            p.category  = self.request.get('category')
            p.allow_contact = True
            p.put()

            template_values = {
                'success'   : True,
                'title'     : p.title,
                'id'        : str(p.key().id())
            }

        template = jinja_environment.get_template('confirm.html')
        self.response.out.write(template.render(template_values))

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
        posting = Posting.get_by_id(int(id_arg))

        template_values = {
            'posting' : posting
        }

        template = jinja_environment.get_template('post.html')
        self.response.out.write(template.render(template_values))

class ContactView(webapp2.RequestHandler):
    def get(self):
        id_arg = self.request.get('id')
        post = Posting.get_by_id(int(id_arg))

        template_values = {
            'allow_contact' : post.allow_contact,
            'id'            : id_arg,
            'title'         : post.title
        }

        template = jinja_environment.get_template('contact.html')
        self.response.out.write(template.render(template_values))

class ContactSubmit(webapp2.RequestHandler):
    def post(self):
        post_id = self.request.get("id")
        sender_email = strip_tags(self.request.get("email"))
        sender_message = strip_tags(self.request.get("message"))

        post = Posting.get_by_id(int(post_id))
        allow_contact = post.allow_contact
        recipient_email = post.email
        success = False


        if self.request.get("spam-check"):
            logging.info("Attempted spam email via contact form")
        elif allow_contact:
            body = """
            You have received a message regarding your post titled %s on Westwood Lost and Found.

            Message:
            %s

            If you wish to respond, contact the following:
            %s

            If you don't want to receive emails regarding your post, click here:
           %s/unsub?key=%s
            """ % (post.title, sender_message, sender_email, self.request.host_url, post.key())

            mail.send_mail(sender="Westwood Lost and Found <admin@westwoodlostandfound.com>",
                           to=recipient_email,
                           subject="Response to '" + post.title + "'",
                           body=body)

            success = True

        template_values = {
            'id'            : post_id,
            'title'         : post.title,
            'success'       : success
        }

        template = jinja_environment.get_template('contact-confirm.html')
        self.response.out.write(template.render(template_values))

class Unsubscribe(webapp2.RequestHandler):
    def get(self):
        post_key = self.request.get('key')
        post = Posting.get(post_key)

        post.allow_contact = False
        post.put()

        template = jinja_environment.get_template('unsub.html')
        self.response.out.write(template.render())


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/post', PostView),
    ('/lost', LostItemsView),
    ('/found', FoundItemsView),
    ('/submit', SubmitPostView),
    ('/submit-post', SubmitPost),
    ('/contact', ContactView),
    ('/contact-submit', ContactSubmit),
    ('/unsub', Unsubscribe)
], debug=True)
