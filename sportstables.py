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

COOKIE_TIME = 315360000
 
class MainPage(webapp.RequestHandler):
    def get(self):
        try:
            table_id = int(self.request.get('table'))
        except:
            table_id = 0
        accounttype_id = 1 #once used to set temp account off a button
        if(table_id == 0):
            u = None
            tempu = None
            login_cookie = Cookie.BaseCookie()
            tablecount = 0
            if users.get_current_user():
                u = User.all()
                u.filter('username = ', users.get_current_user())
                u.fetch(1)
                if u.count(1)==0:
                    new_user = User(username=users.get_current_user())
                    new_user.put()
                    u.fetch(limit=1)
                #transfer any current temp tables
                if 'sportablesuser' in self.request.cookies:
                    usercookie = self.request.cookies['sportablesuser']
                    tempu = User.all()
                    tempu.filter('tempusername = ', usercookie)
                    tempu.fetch(1)
                    for me in u:
                        helperfunctions.transfertables(tempu, me.key().id())
                        u.fetch(1)
                    for g in u:
                        for t in g.tables:
                            tablecount += 1                        
                url = users.create_logout_url(self.request.uri)
                url_linktext = 'Sign out'
            else:
                if(int(accounttype_id) == 1):
                    is_temp_account = 1
                    is_logged_in = 1
                    usercookie = None
                    if 'sportablesuser' in self.request.cookies:
                        usercookie = self.request.cookies['sportablesuser']
                        u = User.all()
                        u.filter('tempusername = ', usercookie)
                        login_cookie['sportablesuser'] = usercookie
                        u.fetch(1)
                        for g in u:
                            for t in g.tables:
                                tablecount += 1
                    else:
                        randomid = uuid.uuid4()
                        login_cookie['sportablesuser'] = randomid
                        new_user = User(tempusername=str(randomid))
                        new_user.put()
                        u = User.all()
                        u.filter('tempusername = ', str(randomid))
                        u.fetch(limit=1)
                    login_cookie['sportablesuser']["expires"] = COOKIE_TIME
                url = users.create_login_url(self.request.uri)
                url_linktext = 'Sign in'  
            template_values = {
                'tablecount': tablecount,
                'url': url,
                'url_linktext': url_linktext
                }
            path = os.path.join(os.path.dirname(__file__), 'index.html')
            self.response.out.write(template.render(path, template_values))
            for morsel in login_cookie.values():
                self.response.headers.add_header('Set-Cookie',morsel.OutputString(None))
        else:
            k = db.Key.from_path('Table', int(table_id))
            t = db.get(k)
            tms = Team().all()
            tms.filter('table = ', k)
            tms.order('-points')
            tms.order('-goal_difference')
            tms.order('-goals_for')
            tms.order('name')
            rs = Result().all()
            rs.filter('table = ', k)
            is_table_owner = False
            usercookie = None
            login_cookie = Cookie.BaseCookie()
            #test to see a table has returned
            if users.get_current_user():
                u = User.all()
                u.filter('username = ', users.get_current_user())
                u.fetch(1)
                if not type(t) is NoneType:
                    for o in u:                       
                        if o.key().id() == t.user.key().id():
                            is_table_owner = True
            else:
                if 'sportablesuser' in self.request.cookies:
                    usercookie = self.request.cookies['sportablesuser']
                    login_cookie['sportablesuser'] = usercookie
                    login_cookie['sportablesuser']["expires"] = COOKIE_TIME
                    u = User.all()
                    u.filter('tempusername = ', usercookie)
                    u.fetch(1)
                    if not type(t) is NoneType:
                        for o in u:
                            if o.key().id() == t.user.key().id():
                                is_table_owner = True
            template_values = {
                'tabledata': t,
                'teamsdata': tms,
                'resultsdata': rs,
                'owner': is_table_owner
                }
            path = os.path.join(os.path.dirname(__file__), 'viewer.html')
            self.response.out.write(template.render(path, template_values))
            for morsel in login_cookie.values():
                self.response.headers.add_header('Set-Cookie',morsel.OutputString(None))

class NewTable(webapp.RequestHandler):
    def get(self):
        accounttype_id = 1
        u = None
        disable = 1
        is_admin = 0
        is_logged_in = 0
        is_temp_account = 0
        login_cookie = Cookie.BaseCookie()
        if users.get_current_user():
            u = User.all()
            u.filter('username = ', users.get_current_user())
            u.fetch(1)
            if u.count(1)==0:
                new_user = User(username=users.get_current_user())
                new_user.put()
                u.fetch(limit=1)
            else:
                for g in u:
                    for t in g.tables:
                        disable = 0
            if users.is_current_user_admin():
                is_admin = 1  
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Sign out'
            is_logged_in = 1
        else:
            if(int(accounttype_id) == 1):
                is_temp_account = 1
                is_logged_in = 1
                usercookie = None
                if 'sportablesuser' in self.request.cookies:
                    usercookie = self.request.cookies['sportablesuser']
                    u = User.all()
                    u.filter('tempusername = ', usercookie)
                    login_cookie['sportablesuser'] = usercookie
                    u.fetch(1)
                    for g in u:
                        for t in g.tables:
                            disable = 0
                else:
                    randomid = uuid.uuid4()
                    login_cookie['sportablesuser'] = randomid
                    new_user = User(tempusername=str(randomid))
                    new_user.put()
                    u = User.all()
                    u.filter('tempusername = ', str(randomid))
                    u.fetch(limit=1)
                login_cookie['sportablesuser']["expires"] = COOKIE_TIME
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Sign in'  
        template_values = {
            'userdata': u,
            'url': url,
            'url_linktext': url_linktext,
            'disable': disable,
            'administrator': is_admin,
            'logged_in': is_logged_in,
            'temp_account': is_temp_account
            }
        path = os.path.join(os.path.dirname(__file__), 'new.html')
        self.response.out.write(template.render(path, template_values))
        for morsel in login_cookie.values():
            self.response.headers.add_header('Set-Cookie',morsel.OutputString(None))

class ExistingTable(webapp.RequestHandler):
    def get(self):
        accounttype_id = 1           
        u = None
        disable = 1
        is_admin = 0
        is_logged_in = 0
        is_temp_account = 0
        login_cookie = Cookie.BaseCookie()
        if users.get_current_user():
            u = User.all()
            u.filter('username = ', users.get_current_user())
            u.fetch(1)
            if u.count(1)==0:
                new_user = User(username=users.get_current_user())
                new_user.put()
                u.fetch(limit=1)
            else:
                for g in u:
                    for t in g.tables:
                        disable = 0
            if users.is_current_user_admin():
                is_admin = 1  
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Sign out'
            is_logged_in = 1
        else:
            if(int(accounttype_id) == 1):
                is_temp_account = 1
                is_logged_in = 1
                usercookie = None
                if 'sportablesuser' in self.request.cookies:
                    usercookie = self.request.cookies['sportablesuser']
                    u = User.all()
                    u.filter('tempusername = ', usercookie)
                    login_cookie['sportablesuser'] = usercookie
                    u.fetch(1)
                    for g in u:
                        for t in g.tables:
                            disable = 0
                else:
                    randomid = uuid.uuid4()
                    login_cookie['sportablesuser'] = randomid
                    new_user = User(tempusername=str(randomid))
                    new_user.put()
                    u = User.all()
                    u.filter('tempusername = ', str(randomid))
                    u.fetch(limit=1)
                login_cookie['sportablesuser']["expires"] = COOKIE_TIME
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Sign in'  
        template_values = {
            'userdata': u,
            'url': url,
            'url_linktext': url_linktext,
            'disable': disable,
            'administrator': is_admin,
            'logged_in': is_logged_in,
            'temp_account': is_temp_account
            }
        path = os.path.join(os.path.dirname(__file__), 'existing.html')
        self.response.out.write(template.render(path, template_values))
        for morsel in login_cookie.values():
            self.response.headers.add_header('Set-Cookie',morsel.OutputString(None))

class CreateTable(webapp.RequestHandler):
    def get(self):
        tab = None
        u = None
        table_name = self.request.get('name', default_value="Unnamed table")
        try:
            points_for_win = int(self.request.get('points_for_win'))
        except:
            points_for_win = 3
        try:
            points_for_score_draw = int(self.request.get('points_for_score_draw'))
        except:
            points_for_score_draw = 1
        try:
            points_for_draw = int(self.request.get('points_for_draw'))
        except:
            points_for_draw = 1
        try:
            points_for_lose = int(self.request.get('points_for_lose'))
        except:
            points_for_lose = 0            
        if users.get_current_user() == None:
            if 'sportablesuser' in self.request.cookies:
                u = User.gql("WHERE tempusername = :1", self.request.cookies['sportablesuser'])
        else:
            u = User.gql("WHERE username = :1", users.get_current_user())
        if u != None:
            if u.count() == 1:        
                for p in u:
                    table = Table(user=p,
                        name=table_name,
                        points_for_win=points_for_win,
                        points_for_score_draw=points_for_score_draw,
                        points_for_draw=points_for_draw,
                        points_for_lose=points_for_lose,
                        viewable=True).put()
                    tab = table.id()
                self.redirect('/getteams?table_name=' + str(tab))
            else:
                # user has a google or temp account but has no User entity
                #TODO: log what has happened
                self.redirect('/')
        else:
            #user has neither logged in with a google account or a set a cookie
            #TODO: log what has happened
            self.redirect('/')                

class GetTable(webapp.RequestHandler):
    def get(self):
        #test param exists and is right type
        try:
            table_get = int(self.request.get('table_name'))
        except:
            table_get = 0
        if(table_get == 0):
            #param or type wrong
            #TODO: add a log message
            self.redirect('/existingtable')
        else:
            u = None
            if users.get_current_user() == None:
                if 'sportablesuser' in self.request.cookies:
                    u = User.gql("WHERE tempusername = :1", self.request.cookies['sportablesuser'])
            else:
                u = User.gql("WHERE username = :1", users.get_current_user())
            if u != None:
                if u.count() == 1:
                    #test if table exists
                    k = db.Key.from_path('Table', table_get)
                    tb = db.get(k)
                    if not type(tb) is NoneType:
                        for o in u:
                            #test if user is owner
                            if o.key().id() == tb.user.key().id():
                                tms = Team().all()
                                tms.filter('table = ', k)
                                tms.order('-points')
                                tms.order('-goal_difference')
                                tms.order('-goals_for')
                                tms.order('name')
                                rs = Result().all()
                                rs.filter('table = ', k)
                                template_values = {
                                    'tabledata': tb,
                                    'teamsdata': tms,
                                    'resultsdata': rs
                                }
                                path = os.path.join(os.path.dirname(__file__), 'table.html')
                                self.response.out.write(template.render(path, template_values))
                            else:
                                #attempt to get another user's table
                                #TODO: log what has happened
                                self.redirect('/existingtable')
                    else:
                        #attempt to get a table that doesn't exist
                        #TODO: log what has happened
                        self.redirect('/existingtable')
                else:
                    # user has a google or temp account but has no User entity
                    #TODO: log what has happened
                    self.redirect('/existingtable')
            else:
                #user has neither logged in with a google account or a set a cookie
                #TODO: log what has happened
                self.redirect('/existingtable')        

class DeleteTable(webapp.RequestHandler):
    def get(self):
        #test param exists and is right type
        try:
            table_delete = int(self.request.get('table_to_delete'))
        except:
            table_delete = 0
        if(table_delete == 0):
            #param or type wrong
            #TODO: add a log message
            self.redirect('/existingtable')
        else:
            u = None
            if users.get_current_user() == None:
                if 'sportablesuser' in self.request.cookies:
                    u = User.gql("WHERE tempusername = :1", self.request.cookies['sportablesuser'])
            else:
                u = User.gql("WHERE username = :1", users.get_current_user())
            if u != None:
                if u.count() == 1:
                    #test if table exists
                    k = db.Key.from_path('Table', table_delete)
                    tb = db.get(k)
                    if not type(tb) is NoneType:
                        for o in u:
                            #test if user is owner
                            if o.key().id() == tb.user.key().id():
                                helperfunctions.deletetable(k)
                                table_id = 0
                                table_object = 'table'
                                return_page = 'Your tables'      
                                object_action = 'deleted'
                                object_url = 'existingtable'        
                                self.redirect('/displaymessage?table_id='
                                              +str(table_id)+'&table_object='+table_object+'&return_page='
                                              +return_page+'&object_action='+object_action+'&object_url='+object_url)
                            else:
                                #attempt to delete another user's table
                                #TODO: log what has happened
                                self.redirect('/existingtable')
                    else:
                        #attempt to delete a table that doesn't exist
                        #TODO: log what has happened
                        self.redirect('/existingtable')
                else:
                    # user has a google or temp account but has no User entity
                    #TODO: log what has happened
                    self.redirect('/existingtable')
            else:
                #user has neither logged in with a google account or a set a cookie
                #TODO: log what has happened
                self.redirect('/existingtable')

class AddTeam(webapp.RequestHandler):
    def post(self):
        #test param exists and is right type
        try:
            table_get = int(self.request.get('tbl_id'))
        except:
            table_get = 0
        table_name = self.request.get('name', default_value="Unnamed team")            
        if(table_get == 0):
            #param or type wrong
            #TODO: add a log message
            self.redirect('/existingtable')
        else:
            u = None
            if users.get_current_user() == None:
                if 'sportablesuser' in self.request.cookies:
                    u = User.gql("WHERE tempusername = :1", self.request.cookies['sportablesuser'])
            else:
                u = User.gql("WHERE username = :1", users.get_current_user())
            if u != None:
                if u.count() == 1:
                    #test if table exists
                    k = db.Key.from_path('Table', table_get)
                    tb = db.get(k)
                    if not type(tb) is NoneType:
                        for o in u:
                            #test if user is owner
                            if o.key().id() == tb.user.key().id():
                                team = Team(table=tb,
                                    name=table_name,
                                    games_played=0,
                                    games_won=0,
                                    games_drawn=0,
                                    games_lost=0,
                                    goals_for=0,
                                    goals_against=0,
                                    goal_difference=0,
                                    points_deducted=0,           
                                    points=0).put()
                                table_id = table_get
                                table_object = 'team'
                                return_page = 'Teams'       
                                object_action = 'added'
                                object_url = 'getteams'        
                                self.redirect('/displaymessage?table_id='+str(table_id)+
                                          '&table_object='+table_object+'&return_page='+
                                          return_page+'&object_action='+object_action+'&object_url='+object_url)
                            else:
                                #attempt to add a team to another user's table
                                #TODO: log what has happened
                                self.redirect('/existingtable')
                    else:
                        #attempt to add team to a table that doesn't exist
                        #TODO: log what has happened
                        self.redirect('/existingtable')
                else:
                    # user has a google or temp account but has no User entity
                    #TODO: log what has happened
                    self.redirect('/existingtable')
            else:
                #user has neither logged in with a google account or a set a cookie
                #TODO: log what has happened
                self.redirect('/existingtable')
        
class GetTeams(webapp.RequestHandler):
    def get(self):
        #test param exists and is right type
        try:
            table_get = int(self.request.get('table_name'))
        except:
            table_get = 0           
        if(table_get == 0):
            #param or type wrong
            #TODO: add a log message
            self.redirect('/existingtable')
        else:
            u = None
            if users.get_current_user() == None:
                if 'sportablesuser' in self.request.cookies:
                    u = User.gql("WHERE tempusername = :1", self.request.cookies['sportablesuser'])
            else:
                u = User.gql("WHERE username = :1", users.get_current_user())
            if u != None:
                if u.count() == 1:
                    #test if table exists
                    k = db.Key.from_path('Table', table_get)
                    tb = db.get(k)
                    if not type(tb) is NoneType:
                        for o in u:
                            #test if user is owner
                            if o.key().id() == tb.user.key().id():
                                tms = Team().all()
                                tms.filter('table = ', k)
                                tms.order('-points')
                                tms.order('-goal_difference')
                                tms.order('-goals_for')
                                tms.order('name')
                                if(tms.count()<2):
                                    disable = 1
                                else:
                                    disable = 0
                                if(tms.count()<1):
                                    disable2 = 1
                                else:
                                    disable2 = 0
                                template_values = {
                                    'tabledata': tb,
                                    'teamsdata': tms,
                                    'disable': disable,
                                    'disable2': disable2
                                }
                                path = os.path.join(os.path.dirname(__file__), 'teams.html')
                                self.response.out.write(template.render(path, template_values))
                            else:
                                #attempt to get teams from another user's table
                                #TODO: log what has happened
                                self.redirect('/existingtable')
                    else:
                        #attempt to get teams from a table that doesn't exist
                        #TODO: log what has happened
                        self.redirect('/existingtable')
                else:
                    # user has a google or temp account but has no User entity
                    #TODO: log what has happened
                    self.redirect('/existingtable')
            else:
                #user has neither logged in with a google account or a set a cookie
                #TODO: log what has happened
                self.redirect('/existingtable')        

class DeleteTeam(webapp.RequestHandler):
    def post(self):     
        #test param exists and is right type
        try:
            table_delete = int(self.request.get('tbl_id'))
        except:
            table_delete = 0
        try:
            team_delete = int(self.request.get('team_to_delete'))
        except:
            team_delete = 0            
        if(table_delete == 0 or team_delete == 0):
            #param or type wrong
            #TODO: add a log message
            self.redirect('/existingtable')
        else:            
            u = None
            if users.get_current_user() == None:
                if 'sportablesuser' in self.request.cookies:
                    u = User.gql("WHERE tempusername = :1", self.request.cookies['sportablesuser'])
            else:
                u = User.gql("WHERE username = :1", users.get_current_user())
            if u != None:
                if u.count() == 1:
                    #test if table and team exists
                    tablek = db.Key.from_path('Table', table_delete)
                    tablet = db.get(tablek)
                    teamk = db.Key.from_path('Team', team_delete)
                    teamt = db.get(teamk)
                    if not type(tablet) is NoneType and not type(teamt) is NoneType:
                        for o in u:
                            #test if user is table owner and table owns team
                            if (o.key().id() == tablet.user.key().id() and
                                        tablet.key().id() == teamt.table.key().id()):
                                #delete team using helperfunctions.function
                                helperfunctions.deleteteam(teamk, tablek)
                                table_id = str(tablet.key().id())
                                table_object = 'team'
                                return_page = 'Teams'        
                                object_action = 'deleted'
                                object_url = 'getteams'        
                                self.redirect('/displaymessage?table_id='+
                                              str(table_id)+'&table_object='+
                                              table_object+'&return_page='+
                                              return_page+'&object_action='+object_action+'&object_url='+object_url)
                            else:
                                #attempt to delete another user's team
                                #TODO: log what has happened
                                self.redirect('/existingtable')
                    else:
                        #attempt to delete a team that doesn't exist (or its table doesn't exist)
                        #TODO: log what has happened
                        self.redirect('/existingtable')
                else:
                    # user has a google or temp account but has no User entity
                    #TODO: log what has happened
                    self.redirect('/existingtable')
            else:
                #user has neither logged in with a google account or a set a cookie
                #TODO: log what has happened
                self.redirect('/existingtable')        

class AddResult(webapp.RequestHandler):
    def post(self):
        #test param exists and is right type
        try:
            table_get = int(self.request.get('tbl_id'))
        except:
            table_get = 0
        try:
            home_team = int(self.request.get('home_team'))
        except:
            home_team = 0
        try:
            away_team = int(self.request.get('away_team'))
        except:
            away_team = 0
        try:
            home_team_score = int(self.request.get('home_team_score'))
        except:
            home_team_score = None
        try:
            away_team_score = int(self.request.get('away_team_score'))
        except:
            away_team_score = None           
        if (table_get == 0 or home_team == 0 or away_team == 0 or home_team_score == None
               or away_team_score == None):
            #param or type wrong
            #TODO: add a log message
            self.redirect('/existingtable')
        else:
            u = None
            if users.get_current_user() == None:
                if 'sportablesuser' in self.request.cookies:
                    u = User.gql("WHERE tempusername = :1", self.request.cookies['sportablesuser'])
            else:
                u = User.gql("WHERE username = :1", users.get_current_user())
            if u != None:
                if u.count() == 1:
                    #test if table and teams exist
                    k = db.Key.from_path('Table', table_get)
                    t = db.get(k)
                    htk = db.Key.from_path('Team', home_team)
                    htm = db.get(htk)
                    atk = db.Key.from_path('Team', away_team)
                    atm = db.get(atk)                    
                    if not type(t) is NoneType and not type(htm) is NoneType and not type(atm) is NoneType:
                        for o in u:
                            #test if user is owner and check that home and away is isn't the same team
                            if (o.key().id() == t.user.key().id() and
                                        t.key().id() == htm.table.key().id() and t.key().id() == atm.table.key().id() and
                                        htm.key().id() != atm.key().id()):
                                #update home team            
                                htm.games_played = htm.games_played + 1
                                pts = 0
                                if home_team_score > away_team_score:
                                    htm.games_won = htm.games_won + 1
                                    pts = t.points_for_win  
                                elif home_team_score > 0 and (home_team_score == away_team_score):
                                    htm.games_drawn = htm.games_drawn + 1
                                    pts = t.points_for_score_draw
                                elif home_team_score == 0 and (home_team_score == away_team_score):
                                    htm.games_drawn = htm.games_drawn + 1
                                    pts = t.points_for_draw             
                                else:
                                    htm.games_lost = htm.games_lost + 1
                                    pts = t.points_for_lose
                                htm.goals_for = htm.goals_for + home_team_score
                                htm.goals_against = htm.goals_against + away_team_score
                                htm.goal_difference = htm.goals_for - htm.goals_against
                                htm.points =  htm.points + int(pts)       
                                htm.put()
                                #update away team            
                                atm.games_played = atm.games_played + 1
                                pts = 0
                                if home_team_score < away_team_score:
                                    atm.games_won = atm.games_won + 1
                                    pts = t.points_for_win  
                                elif home_team_score > 0 and (home_team_score == away_team_score):
                                    atm.games_drawn = atm.games_drawn + 1
                                    pts = t.points_for_score_draw
                                elif home_team_score == 0 and (home_team_score == away_team_score):
                                    atm.games_drawn = atm.games_drawn + 1
                                    pts = t.points_for_draw             
                                else:
                                    atm.games_lost = atm.games_lost + 1
                                    pts = t.points_for_lose
                                atm.goals_for = atm.goals_for + away_team_score
                                atm.goals_against = atm.goals_against + home_team_score
                                atm.goal_difference = atm.goals_for - atm.goals_against
                                atm.points =  atm.points + int(pts)       
                                atm.put()
                                #add result      
                                result = Result(table=t,
                                    home_team_id=home_team,
                                    home_team_name=htm.name,
                                    home_team_score=home_team_score,
                                    away_team_id=away_team,
                                    away_team_name=atm.name,
                                    away_team_score=away_team_score,
                                    time_added=datetime.now()).put()
                                table_id = str(t.key().id())
                                table_object = 'result'
                                return_page = 'Results'       
                                object_action = 'added'
                                object_url = 'getresults'        
                                self.redirect('/displaymessage?table_id='+
                                              str(table_id)+'&table_object='+table_object+'&return_page='+
                                              return_page+'&object_action='+object_action+'&object_url='+object_url)
                            else:
                                #attempt to add a result to another user's table or team
                                #TODO: log what has happened
                                self.redirect('/existingtable')
                    else:
                        #attempt to add result to a table or a team that doesn't exist
                        #TODO: log what has happened
                        self.redirect('/existingtable')
                else:
                    # user has a google or temp account but has no User entity
                    #TODO: log what has happened
                    self.redirect('/existingtable')
            else:
                #user has neither logged in with a google account or a set a cookie
                #TODO: log what has happened
                self.redirect('/existingtable')

class GetResults(webapp.RequestHandler):
    def get(self):
        usercookie = None
        login_cookie = Cookie.BaseCookie()
        if 'sportablesuser' in self.request.cookies:
            usercookie = self.request.cookies['sportablesuser']
            login_cookie['sportablesuser'] = usercookie
            login_cookie['sportablesuser']["expires"] = COOKIE_TIME
        k = db.Key.from_path('Table', int(self.request.get('table_name')))
        tb = db.get(k)
        tms = Team().all()
        tms.filter('table = ', k)
        tms.order('-points')
        tms.order('-goal_difference')
        tms.order('-goals_for')
        tms.order('name')
        if(tms.count()<2):
            disable = 1
        else:
            disable = 0
        if(tms.count()<1):
            disable2 = 1
        else:
            disable2 = 0
        try:
            result_set = int(self.request.get('result_set'))
        except:
            result_set = 0           
        #new test part
        rs = Result().all()
        rs.filter('table = ', k)
        rs_away = Result().all()
        rs_away.filter('table = ', k)
        hrl = []
        if int(result_set) != 0:
            rs.filter('home_team_id = ', result_set)
            rs_away.filter('away_team_id = ', result_set)
            for r in rs:
                hrl.append(int(r.key().id()))
            for r in rs_away:
                hrl.append(int(r.key().id()))
            rs = Result.get_by_id(hrl)
            rs.sort(key=lambda result: result.time_added)        
        #new test end            
        url = './'
        url_linktext = 'Home'
        server_name = os.environ['SERVER_NAME']
        if (server_name == 'localhost'):
            server_port = ':'+os.environ['SERVER_PORT']
        else:
            server_port = ''
        viewable_url  = server_name+server_port+'?table='+str(self.request.get('table_name'))
        score_options = range(300)
        template_values = {
	    'tabledata': tb,
	    'teamsdata': tms,
            'result_set_data': result_set,
	    'resultsdata': rs,            
	    'url': url,
	    'url_linktext': url_linktext,
	    'disable': disable,
            'disable2': disable2,
            'viewable_url': viewable_url,
            'score_options': score_options
        }
        path = os.path.join(os.path.dirname(__file__), 'results.html')
        self.response.out.write(template.render(path, template_values))
        for morsel in login_cookie.values():
            self.response.headers.add_header('Set-Cookie',morsel.OutputString(None))
            
class DeleteResult(webapp.RequestHandler):
    def post(self):
        #test param exists and is right type
        try:
            table_delete = int(self.request.get('table_id'))
        except:
            table_delete = 0
        try:
            result_delete = int(self.request.get('result_id'))
        except:
            result_delete = 0
        try:
            result_set = int(self.request.get('result_set'))
        except:
            result_set = 0            
        if(table_delete == 0 or result_delete == 0):
            #param or type wrong
            #TODO: add a log message
            self.redirect('/existingtable')
        else:            
            u = None
            if users.get_current_user() == None:
                if 'sportablesuser' in self.request.cookies:
                    u = User.gql("WHERE tempusername = :1", self.request.cookies['sportablesuser'])
            else:
                u = User.gql("WHERE username = :1", users.get_current_user())
            if u != None:
                if u.count() == 1:
                    #test if table and team exists
                    tablek = db.Key.from_path('Table', table_delete)
                    tablet = db.get(tablek)
                    resultk = db.Key.from_path('Result', result_delete)
                    resultt = db.get(resultk)                    
                    if not type(tablet) is NoneType and not type(resultt) is NoneType:
                        for o in u:
                            #test if user is table owner and table owns team                           
                            if (o.key().id() == tablet.user.key().id() and
                                        tablet.key().id() == resultt.table.key().id()):
                                #delete team using helperfunctions.function
                                helperfunctions.deleteresult(resultk, tablek)
                                table_object = 'result'
                                return_page = 'Results'       
                                object_action = 'deleted'
                                object_url = 'getresults'
                                self.redirect('/displaymessage?table_id='+
                                          str(table_delete)+'&table_object='+table_object+'&return_page='+
                                          return_page+'&object_action='+object_action+'&object_url='+
                                          object_url+'&result_set='+str(result_set))
                            else:
                                #attempt to delete another user's team
                                #TODO: log what has happened
                                self.redirect('/existingtable')
                    else:
                        #attempt to delete a team that doesn't exist (or its table doesn't exist)
                        #TODO: log what has happened
                        self.redirect('/existingtable')
                else:
                    # user has a google or temp account but has no User entity
                    #TODO: log what has happened
                    self.redirect('/existingtable')
            else:
                #user has neither logged in with a google account or a set a cookie
                #TODO: log what has happened
                self.redirect('/existingtable')

class GetShare(webapp.RequestHandler):
    def get(self):
        #test param exists and is right type
        try:
            table_get = int(self.request.get('table_name'))
        except:
            table_get = 0
        if(table_get == 0):
            #param or type wrong
            #TODO: add a log message
            self.redirect('/existingtable')
        else:
            u = None
            if users.get_current_user() == None:
                if 'sportablesuser' in self.request.cookies:
                    u = User.gql("WHERE tempusername = :1", self.request.cookies['sportablesuser'])
            else:
                u = User.gql("WHERE username = :1", users.get_current_user())
            if u != None:
                if u.count() == 1:
                    #test if table exists
                    k = db.Key.from_path('Table', table_get)
                    tb = db.get(k)
                    if not type(tb) is NoneType:
                        for o in u:
                            #test if user is owner
                            if o.key().id() == tb.user.key().id():
                                server_name = os.environ['SERVER_NAME']
                                if (server_name == 'localhost'):
                                    server_port = ':'+os.environ['SERVER_PORT']
                                else:
                                    server_port = ''
                                viewable_url  = server_name+server_port+'?table='+str(table_get)
                                template_values = {
                                    'tabledata': tb,
                                    'viewable_url': viewable_url
                                }
                                path = os.path.join(os.path.dirname(__file__), 'share.html')
                                self.response.out.write(template.render(path, template_values))
                            else:
                                #attempt to get another user's table
                                #TODO: log what has happened
                                self.redirect('/existingtable')
                    else:
                        #attempt to get a table that doesn't exist
                        #TODO: log what has happened
                        self.redirect('/existingtable')
                else:
                    # user has a google or temp account but has no User entity
                    #TODO: log what has happened
                    self.redirect('/existingtable')
            else:
                #user has neither logged in with a google account or a set a cookie
                #TODO: log what has happened
                self.redirect('/existingtable')       

class MakeViewable(webapp.RequestHandler):
    def get(self):
        #test param exists and is right type
        try:
            table_get = int(self.request.get('tbl_id'))
        except:
            table_get = 0
        try:
            viewable_get = int(self.request.get('viewable'))
        except:
            viewable_get = None            
        if(table_get == 0):
            #param or type wrong
            #TODO: add a log message
            self.redirect('/existingtable')
        else:
            u = None
            if users.get_current_user() == None:
                if 'sportablesuser' in self.request.cookies:
                    u = User.gql("WHERE tempusername = :1", self.request.cookies['sportablesuser'])
            else:
                u = User.gql("WHERE username = :1", users.get_current_user())
            if u != None:
                if u.count() == 1:
                    #test if table exists
                    k = db.Key.from_path('Table', table_get)
                    tb = db.get(k)
                    if not type(tb) is NoneType:
                        for o in u:
                            #test if user is owner
                            if o.key().id() == tb.user.key().id():
                                #update viewable boolean if set to number
                                if viewable_get != None:
                                    tb.viewable = bool(viewable_get)
                                    tb.put()
                                self.redirect('/getshare?table_name=' + str(table_get))
                            else:
                                #attempt to get another user's table
                                #TODO: log what has happened
                                self.redirect('/existingtable')
                    else:
                        #attempt to get a table that doesn't exist
                        #TODO: log what has happened
                        self.redirect('/existingtable')
                else:
                    # user has a google or temp account but has no User entity
                    #TODO: log what has happened
                    self.redirect('/existingtable')
            else:
                #user has neither logged in with a google account or a set a cookie
                #TODO: log what has happened
                self.redirect('/existingtable')

class DisplayMessage(webapp.RequestHandler):
    def get(self):
        #parse the params method into template values
        try:
            table_id = int(self.request.get('table_id'))
        except:
            table_id = 0
        try:
            result_set = int(self.request.get('result_set'))
        except:
            result_set = 0
        table_object = self.request.get('table_object', default_value="message")            
        return_page = self.request.get('return_page', default_value="Your tables")
        object_action = self.request.get('object_action', default_value="displayed")
        object_url = self.request.get('object_url', default_value="existingtable")      
        template_values = {
            'table_id': table_id,
	    'table_object': table_object,
            'return_page': return_page,
	    'object_action': object_action,
            'object_url': object_url,
            'result_set': result_set
        }        
        path = os.path.join(os.path.dirname(__file__), 'displaymessage.html')
        self.response.out.write(template.render(path, template_values))       

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/newtable', NewTable),
                                      ('/existingtable', ExistingTable),
                                      ('/createtable', CreateTable),
                                      ('/gettable', GetTable),
                                      ('/deletetable', DeleteTable),
                                      ('/addteam', AddTeam),
                                      ('/getteams', GetTeams),
                                      ('/deleteteam', DeleteTeam),
                                      ('/addresult', AddResult),
                                      ('/getresults', GetResults),
                                      ('/deleteresult', DeleteResult),
                                      ('/getshare', GetShare),
                                      ('/makeviewable', MakeViewable),
                                      ('/displaymessage', DisplayMessage)],
                                      debug=False)
 
def main():
    run_wsgi_app(application)
 
if __name__ == "__main__":
    main()
