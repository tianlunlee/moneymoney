from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import logging
import webapp2
import os

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(template_dir))

class User(ndb.Model):
    name = ndb.StringProperty()
    goal = ndb.FloatProperty()
    score = ndb.IntegerProperty()

    # university = ndb.StringProperty()
    # university_key = ndb.KeyProperty(kind=University)
class CurrentBudget(ndb.Model):
    value = ndb.FloatProperty()

class Money(ndb.Model):
    # this model
    source_name = ndb.StringProperty()
    user_key = ndb.KeyProperty(kind=User)
    balance = ndb.FloatProperty()

    def decrease_value(self, amount):
        self.balance -= amount

    # def set_value(self, amount):
    #     self.balance = amount

    def add_value(self, amount):
        self.balance += amount

class PastBudget(ndb.Model):
    source_name = ndb.StringProperty()
    user_key = ndb.KeyProperty(kind=User)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()


        if user:
            logout_url = users.CreateLogoutURL('/')

            template = jinja_environment.get_template('main.html')
            template_vals = {'user':user, 'logout_url':logout_url}
            self.response.write(template.render(template_vals))

        else:
            login_url = users.CreateLoginURL('/')


            template = jinja_environment.get_template('home.html')

            template_vals = {'user':user, 'login_url':login}
            self.response.write(template.render(template_vals))

            # self.response.write(
            #     '<br><html><body>{}</body></html>'.format(greeting))




    def post(self):
        self.redirect('/')




app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
