# -*- coding: utf-8 -*-
import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
import cgi
import helperfunctions
import uuid
import Cookie
from types import *
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from dbmodel import User, Table, Team, Result
from datetime import datetime
 
class MainPage(webapp.RequestHandler):
    def get(self):
        u = User.all()
        url = '../'
        url_linktext = 'Home'
        disable = 1
        template_values = {
            'disable': disable
            }
        path = os.path.join(os.path.dirname(__file__), 'admin/admin.html')
        self.response.out.write(template.render(path, template_values))

class GetSpecialReport(webapp.RequestHandler):
    def post(self):
        disable = 0
        #get tables that match
        tot_ts = Table.gql("")
        #add the beginning count
        total_tables = tot_ts.count()
        ts = Table.gql("WHERE name IN('SVB', :1)", u'SV Böblingen D1')
        #add the number affected with SVB and SV B
        total_bad = ts.count()
        deletecounter = 0
        for t in ts:
            teams = Team.gql("WHERE table = :1", t)
            if teams.count() == 0:
                deletecounter += 1
        #add the number of would be deleted tables        
        delete_tables = deletecounter        
        post_ts = Table.gql("WHERE name IN('SVB', :1)", u'SV Böblingen D1')
        #add the number remainig after the delete operation
        remaining_tables = post_ts.count()
        template_values = {
            'total_tables': total_tables,
            'total_bad': total_bad,
            'delete_tables': delete_tables,
            'remaining_tables': remaining_tables,
            'disable': disable
            }
        path = os.path.join(os.path.dirname(__file__), 'admin/admin.html')
        self.response.out.write(template.render(path, template_values))

class DoSpecialDeleteOp(webapp.RequestHandler):
    def post(self):
        disable = 1
        #list to hold IDs of matched tables without teams
        no_team_tables = []
        #get tables that match
        tot_ts = Table.gql("")
        #add the beginning count
        total_tables = tot_ts.count()
        ts = Table.gql("WHERE name IN('SVB', :1)", u'SV Böblingen D1')
        #add the number affected with SVB and SV B
        total_bad = ts.count()
        deletecounter = 0
        for t in ts:
            teams = Team.gql("WHERE table = :1", t)
            if teams.count() == 0:
                #do the delete thing
                helperfunctions.deletetable(t.key())         
                deletecounter += 1
        #add the number of deleted tables        
        delete_tables = deletecounter        
        post_ts = Table.gql("WHERE name IN('SVB', :1)", u'SV Böblingen D1')
        #add the number remainig after the delete operation
        remaining_tables = post_ts.count()
        template_values = {
            'total_tables': total_tables,
            'total_bad': total_bad,
            'delete_tables': delete_tables,
            'remaining_tables': remaining_tables,
            'disable': disable
            }
        path = os.path.join(os.path.dirname(__file__), 'admin/admin.html')
        self.response.out.write(template.render(path, template_values))        
        
application = webapp.WSGIApplication(
                                     [('/admin/', MainPage),
                                      ('/admin/getspecialreport', GetSpecialReport),
                                      ('/admin/dospecialdeleteop', DoSpecialDeleteOp)],
                                     debug=True)
 
def main():
    run_wsgi_app(application)
 
if __name__ == "__main__":
    main()
