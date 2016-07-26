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

    def history_url(self):
        return '/history?key=' + self.key.urlsafe()

    def create_budget(self, source_name, user_key, balance):
        Budget(sourcename=source_name, user_key=user_key, balance=balance)

class Item(ndb.Model):
    item_name = ndb.StringProperty()
    cost = ndb.FloatProperty()
    date = ndb.StringProperty()
    user_key = ndb.KeyProperty(kind=User)
    remaining_balance = ndb.FloatProperty()



class Budget(ndb.Model):
    # this model
    source_name = ndb.StringProperty()
    user_key = ndb.KeyProperty(kind=User)
    amount = ndb.FloatProperty()
    date = ndb.StringProperty()
    datetime = ndb.DateTimeProperty(auto_now_add = True)

    # remaining = ndb.FloatProperty()

    def decrease_value(self, value):
        self.amount -= amount


    def add_value(self, value):
        self.amount += amount

    # def calc_remaining(self, value):
    #      self.remaining = balance
    #      self.remaining -= value



class PastBudget(ndb.Model):
    source_name = ndb.StringProperty()
    user_key = ndb.KeyProperty(kind=User)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()



        # if the user is logged in, show the main page. else show the home page
        if current_user:
            logout_url = users.CreateLogoutURL('/')
            # create name based on email address
            email = current_user.email()
            username = email.rsplit('@')[0]
            #interact with db
            current_users = User.query(User.email==email).fetch()

            if not current_users: # if the user doesn't exist in the current users list
                user = User(username=username, email=email)
                user.put()
            else:
                user = User.query(User.username == username).get()


            items = Item.query(Item.user_key==user.key).order(-Item.date).fetch()
            budgets = Budget.query(Budget.user_key==user.key).order(-Budget.date, -Budget.datetime).fetch()

            template = jinja_environment.get_template('main.html')
            template_vals = {'user':user, 'logout_url':logout_url, 'items':items, 'budgets':budgets}
            self.response.write(template.render(template_vals))

        else:
            login_url = users.CreateLoginURL('/')


            template = jinja_environment.get_template('home.html')

            template_vals = {'login_url':login_url, 'script':''}
            self.response.write(template.render(template_vals))

    def post(self):
        # get info

        current_user = users.get_current_user()
        email = current_user.email()

        user = User.query(User.email == email).get()
        self.response.write(user)
        user_key = user.key

        budget = Budget.query(Budget.user_key == user_key).get()
        if not budget:
            script = 'alert({})'.format('You don\'t have a budget yet!')
            #alert the user that they do not currently have a budget

            self.get()
        else:

            date = self.request.get('date')
            cost = self.request.get('cost')
            if cost: # if nonempty, convert to float
                cost = float(cost)
            else: # otherwise set it to 0
                cost = 0
            item_name = self.request.get('name')

            remaining_balance = budget.amount - cost

            # interact with db
            new_item = Item(item_name=item_name, cost=cost, date=date, user_key=user_key, remaining_balance=remaining_balance)
            new_item.put()
            # render
        self.redirect('/')

class HistoryHandler(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        email = current_user.email()
        user = User.query(User.email == email).get()
        user_key = user.key

        items = Item.query(Item.user_key==user.key).order(-Item.date).fetch()

        template = jinja_environment.get_template('history.html')
        template_vals = {'user':user, 'items':items}
        self.response.write(template.render(template_vals))

class BudgetHandler(webapp2.RequestHandler):

    def get(self):
        # get info
        template = jinja_environment.get_template('budget.html')
        # template_vals = {'current_budget':current_budget}
        #
        self.response.write(template.render())
    def post(self):
        current_user = users.get_current_user()
        email = current_user.email()


        user = User.query(User.email == email).get()
        self.response.write(user)
        user_key = user.key

        source_name = self.request.get('source_name')
        amount = self.request.get('amount')
        date = self.request.get('date')
        if amount: # if nonempty, convert to float
            amount = float(amount)
        else: # otherwise set it to 0
            amount = 0


        new_budget = Budget(source_name=source_name, user_key=user_key, amount = amount, date = date)
        new_budget.put()

        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/history', HistoryHandler),
    ('/addbudget', BudgetHandler)
], debug=True)
