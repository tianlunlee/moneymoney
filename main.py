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
    username = ndb.StringProperty()
    email = ndb.StringProperty()
    # university = ndb.StringProperty()
    # university_key = ndb.KeyProperty(kind=University)
# class CurrentBudget(ndb.Model):
#     value = ndb.FloatProperty()
    def create_budget(self, source_name, user_key, balance)
        Budget(source_name, user_key, balance)

class Item(ndb.Model):
    item_name = ndb.StringProperty()
    cost = ndb.FloatProperty()
    date = ndb.StringProperty()
    user_key = ndb.KeyProperty(kind=User)




class Budget(ndb.Model):
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
        current_user = users.get_current_user()

        # if the user is logged in, show the main page. else show the home page
        if current_user:
            logout_url = users.CreateLogoutURL('/')

            email = current_user.email()
            username = email.rsplit('@')[0]
            #interact with db
            current_users = User.query(User.email==email).fetch()

            if not current_users: # if the user doesn't exist in the current users list
                user = User(username=username, email=email)
                user.put()
            else:
                user = User.query(User.username == username).get()

            template = jinja_environment.get_template('main.html')
            template_vals = {'user':user, 'logout_url':logout_url}
            self.response.write(template.render(template_vals))

        else:
            login_url = users.CreateLoginURL('/')


            template = jinja_environment.get_template('home.html')

            template_vals = {'login_url':login_url}
            self.response.write(template.render(template_vals))

    def post(self):
        # get info
        current_user = users.get_current_user()

        email = current_user.email()

        user = User.query(User.email == email).get()
        self.response.write(user)
        user_key = user.key


        date = self.request.get('date')
        cost = self.request.get('cost')
        if cost: # if nonempty, convert to float
            cost = float(cost)
        else: # otherwise set it to 0
            cost = 0
        item_name = self.request.get('name')

        # interact with db
        new_item = Item(item_name=item_name, cost=cost, date=date, user_key=user_key)
        new_item.put()
        # render
        self.redirect('/')


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
