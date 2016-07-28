from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import logging
import webapp2
import os

import datetime
from datetime import date
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(template_dir))

class User(ndb.Model):
    username = ndb.StringProperty()
    email = ndb.StringProperty()
    date = ndb.DateProperty(auto_now = True)
    def history_url(self):
        return '/history?key=' + self.key.urlsafe()

class Budget(ndb.Model):
    # this model
    source_name = ndb.StringProperty()
    user_key = ndb.KeyProperty(kind=User)
    amount = ndb.FloatProperty()
    date = ndb.StringProperty()
    end_date = ndb.StringProperty()
    datetime = ndb.DateTimeProperty(auto_now_add = True)

    # remaining = ndb.FloatProperty()

    def decrease_value(self, value):
        self.amount -= amount


    def add_value(self, value):
        self.amount += amount

    # def calc_remaining(self, value):
    #      self.remaining = balance
    #      self.remaining -= value


class Item(ndb.Model):
    item_name = ndb.StringProperty()
    cost = ndb.FloatProperty()
    note = ndb.StringProperty()
    user_key = ndb.KeyProperty(kind=User)
    budget_key = ndb.KeyProperty(kind=Budget)
    remaining_balance = ndb.FloatProperty()
    datetime = ndb.DateTimeProperty(auto_now_add = True)




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

            user.date = datetime.date.today()

            budgets = Budget.query(Budget.user_key==user.key).order(-Budget.datetime).fetch()

            if budgets:
                items = Item.query(Item.budget_key==budgets[0].key).order(-Item.datetime).fetch()

                template = jinja_environment.get_template('main.html')

                user_date = user.date
                budget_date = budgets[0].end_date
                budget_split = budget_date.rsplit('/')
                end_date = date(int(budget_split[2]), int(budget_split[0]), int(budget_split[1]))

                # month = int(budget_split[0]) - int(user_date.month)
                # day = int(budget_split[1]) - int(user_date.day)
                # year = int(budget_split[2]) - int(user_date.year)

                # countdown = {'year':year, 'month':month, 'day':day}
                countdown = end_date - user_date
                print countdown
                template_vals = {'user':user, 'logout_url':logout_url, 'items':items, 'budgets':budgets,
                'countdown':countdown
                }

                self.response.write(template.render(template_vals))
            else:
                self.redirect('/addbudget')

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

        budget = Budget.query(Budget.user_key == user.key).order(-Budget.datetime).get()
        item = Item.query(Item.budget_key == budget.key).order(-Item.datetime).get()



        note = self.request.get('note')
        cost = self.request.get('cost')
        if cost: # if nonempty, convert to float
            cost = float(cost)
        else: # otherwise set it to 0
            cost = 0
        item_name = self.request.get('name')
        if not item:
            remaining_balance = budget.amount - cost
        else:
            remaining_balance = item.remaining_balance - cost

            # interact with db
        new_item = Item(item_name=item_name, cost=cost, note=note, budget_key=budget.key, remaining_balance=remaining_balance,user_key=user.key)
        new_item.put()
            # render
        self.redirect('/')



class BudgetHandler(webapp2.RequestHandler):

    def get(self):
        # get info
        current_user = users.get_current_user()
        email = current_user.email()


        user = User.query(User.email == email).get()

        user_key = user.key
        template = jinja_environment.get_template('budget.html')
        # template_vals = {'current_budget':current_budget}
        logout_url = users.CreateLogoutURL('/')
        self.response.write(template.render({'user':user,'logout_url':logout_url}))
    def post(self):
        current_user = users.get_current_user()
        email = current_user.email()


        user = User.query(User.email == email).get()

        user_key = user.key

        source_name = self.request.get('source_name')
        amount = self.request.get('amount')
        date = self.request.get('date')
        end_date = self.request.get('end_date')
        if amount: # if nonempty, convert to float
            amount = float(amount)
        else: # otherwise set it to 0
            amount = 0

        old_budget = Budget.query().order(-Budget.datetime).get()
        new_budget = Budget(source_name=source_name, user_key=user_key, amount = amount, date = date, end_date=end_date)
        new_budget.put()


        # if old_budget: # if there is an old budget
        #     self.refresh(old_budget, new_budget)

        self.redirect('/')

    # def refresh(self, old_budget, new_budget):
    #     items = Item.query(Item.budget_key == old_budget.key).order(Item.datetime).fetch()
    #     for i in range(0,len(items)):
    #         if i == 0:
    #             items[i].remaining_balance = new_budget.amount - items[i].cost
    #             Item.budget_key = new_budget.key
    #         else:
    #             items[i].remaining_balance = item.remaining_balance - items[i].cost
    #             Item.budget_key = new_budget.key











class HistoryHandler(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        email = current_user.email()
        user = User.query(User.email == email).get()

        logout_url = users.CreateLogoutURL('/')



        budgets = Budget.query(Budget.user_key == user.key).order(-Budget.datetime).fetch()

        items=[]
        length = len(budgets)

        for budget in budgets:
            items.append(Item.query(Item.budget_key==budget.key).order(-Item.datetime).fetch())



        template = jinja_environment.get_template('history.html')
        template_vals = {'user':user, 'items':items, 'budgets':budgets, 'length':length, 'logout_url':logout_url}
        self.response.write(template.render(template_vals))

    def post(self):
        current_user = users.get_current_user()
        email = current_user.email()
        user = User.query(User.email == email).get()
        user_key = user.key

        current_items = Item.query(Item.user_key==user.key)
        for item in current_items:
            item.key.delete()

        self.redirect('/history')

        #delete

class OldBudgetHangler(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user()
        email = current_user.email()
        user = User.query(User.email == email).get()
        user_key = user.key

        logout_url = users.CreateLogoutURL('/')


        budgets = Budget.query(Budget.user_key == user.key).order(-Budget.datetime).fetch()

        items=[]
        length = len(budgets)

        totalSaved = 0

        for budget in budgets:
            temp = Item.query(Item.budget_key==budget.key).order(-Item.datetime).fetch()
            items.append(temp)
            if temp:
                totalSaved += temp[0].remaining_balance
            else:
                totalSaved += budget.amount

        template = jinja_environment.get_template('budgets.html')
        template_vals = {'user':user, 'budgets':budgets, 'items':items, 'length':length, 'totalSaved':totalSaved, 'logout_url':logout_url}
        self.response.write(template.render(template_vals))

    def post(self):
        current_user = users.get_current_user()
        email = current_user.email()
        user = User.query(User.email == email).get()
        user_key = user.key
        current_budgets = Budget.query(Budget.user_key==user.key)

        for budget in current_budgets:
            items = Item.query(Item.budget_key==budget.key).fetch()
            if items:
                for item in items:
                    item.key.delete()
            budget.key.delete()
        self.redirect('/history')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/history', HistoryHandler),
    ('/addbudget', BudgetHandler),
    ('/budgets', OldBudgetHangler)
], debug=True)
