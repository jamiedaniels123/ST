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
        table_id = self.request.get('table')
        try:
            test_table_id = int(table_id)
        except:
            table_id = 0
        accounttype_id = 1 #once used to set temp account off a button
        if(table_id == 0):
            u = None
            tempu = None
            login_cookie = Cookie.BaseCookie()
            #tablecount = 0
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
        t = User.all()
        if users.get_current_user() == None:
            if 'sportablesuser' in self.request.cookies:
                usercookie = self.request.cookies['sportablesuser']
                t.filter('tempusername = ', usercookie)
        else:
            t.filter('username = ', users.get_current_user())
        t.fetch(1)
        tab = None
        for p in t:
            table = Table(user=p,
                name=self.request.get('name'),
                points_for_win=int(self.request.get('points_for_win')),
                points_for_draw=int(self.request.get('points_for_draw')),
                points_for_score_draw=int(self.request.get('points_for_score_draw')),
                points_for_lose=int(self.request.get('points_for_lose')),
                viewable=True).put()
            tab = table.id()
        self.redirect('/getteams?table_name=' + str(tab))

class GetTable(webapp.RequestHandler):
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
        rs = Result().all()
        rs.filter('table = ', k)            
        url = './'
        url_linktext = 'Home'
        server_name = os.environ['SERVER_NAME']
        if (server_name == 'localhost'):
            server_port = ':'+os.environ['SERVER_PORT']
        else:
            server_port = ''
        viewable_url  = server_name+server_port+'?table='+str(self.request.get('table_name'))
        score_options = range(200)
        template_values = {
	    'tabledata': tb,
	    'teamsdata': tms,
            'resultsdata': rs,            
	    'url': url,
	    'url_linktext': url_linktext,
	    'disable': disable,
            'disable2': disable2,
            'viewable_url': viewable_url,
            'score_options': score_options
        }
        path = os.path.join(os.path.dirname(__file__), 'table.html')
        self.response.out.write(template.render(path, template_values))
        for morsel in login_cookie.values():
            self.response.headers.add_header('Set-Cookie',morsel.OutputString(None))        

class DeleteTable(webapp.RequestHandler):
    def get(self):
        #test param exists and is right type
        try:
            table_delete = int(self.request.get('table_to_delete'))
        except:
            table_delete = 0;
        if(table_delete == 0):
            #param or type wrong
            #TODO: add a log message
            self.redirect('/existingtable')
        else:
            k = db.Key.from_path('Table', table_delete)
            helperfunctions.deletetable(k)
            table_id = 0
            table_object = 'table'
            return_page = 'Your tables'      
            object_action = 'deleted'
            object_url = 'existingtable'        
            self.redirect('/displaymessage?table_id='+str(table_id)+'&table_object='+table_object+'&return_page='+return_page+'&object_action='+object_action+'&object_url='+object_url)

class AddTeam(webapp.RequestHandler):
    def post(self):
        k = db.Key.from_path('Table', int(self.request.get('tbl_id')))
        t = db.get(k)      
        team = Team(table=t,
            name=self.request.get('name'),
            games_played=0,
            games_won=0,
            games_drawn=0,
            games_lost=0,
            goals_for=0,
            goals_against=0,
            goal_difference=0,
            points_deducted=0,           
            points=0).put()
        table_id = self.request.get('tbl_id')
        table_object = 'team'
        return_page = 'Teams'       
        object_action = 'added'
        object_url = 'getteams'        
        self.redirect('/displaymessage?table_id='+str(table_id)+'&table_object='+table_object+'&return_page='+return_page+'&object_action='+object_action+'&object_url='+object_url)
        
class GetTeams(webapp.RequestHandler):
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
        url = './'
        url_linktext = 'Home'
        server_name = os.environ['SERVER_NAME']
        if (server_name == 'localhost'):
            server_port = ':'+os.environ['SERVER_PORT']
        else:
            server_port = ''
        viewable_url  = server_name+server_port+'?table='+str(self.request.get('table_name'))
        score_options = range(200)
        template_values = {
	    'tabledata': tb,
	    'teamsdata': tms,	    
	    'url': url,
	    'url_linktext': url_linktext,
	    'disable': disable,
            'disable2': disable2,
            'viewable_url': viewable_url,
            'score_options': score_options
        }
        path = os.path.join(os.path.dirname(__file__), 'teams.html')
        self.response.out.write(template.render(path, template_values))
        for morsel in login_cookie.values():
            self.response.headers.add_header('Set-Cookie',morsel.OutputString(None))        

class DeleteTeam(webapp.RequestHandler):
    def post(self):
        tablek = db.Key.from_path('Table', int(self.request.get('tbl_id')))
        tablet = db.get(tablek)
        teamk = db.Key.from_path('Team', int(self.request.get('team_to_delete')))
        #delete team using helperfunctions.function
        helperfunctions.deleteteam(teamk, tablek)
        table_id = str(tablet.key().id())
        table_object = 'team'
        return_page = 'Teams'        
        object_action = 'deleted'
        object_url = 'getteams'        
        self.redirect('/displaymessage?table_id='+str(table_id)+'&table_object='+table_object+'&return_page='+return_page+'&object_action='+object_action+'&object_url='+object_url)        

class AddResult(webapp.RequestHandler):
    def post(self):
        k = db.Key.from_path('Table', int(self.request.get('tbl_id')))
        t = db.get(k)
        #update home team
        htk = db.Key.from_path('Team', int(self.request.get('home_team')))
        htm = db.get(htk)            
        htm.games_played = htm.games_played + 1
        pts = 0
        if int(self.request.get('home_team_score')) > int(self.request.get('away_team_score')):
            htm.games_won = htm.games_won + 1
            pts = t.points_for_win  
        elif int(self.request.get('home_team_score')) > 0 and (int(self.request.get('home_team_score')) == int(self.request.get('away_team_score'))):
            htm.games_drawn = htm.games_drawn + 1
            pts = t.points_for_score_draw
        elif int(self.request.get('home_team_score')) == 0 and (int(self.request.get('home_team_score')) == int(self.request.get('away_team_score'))):
            htm.games_drawn = htm.games_drawn + 1
            pts = t.points_for_draw             
        else:
            htm.games_lost = htm.games_lost + 1
            pts = t.points_for_lose
        htm.goals_for = htm.goals_for + int(self.request.get('home_team_score'))
        htm.goals_against = htm.goals_against + int(self.request.get('away_team_score'))
        htm.goal_difference = htm.goals_for - htm.goals_against
        htm.points =  htm.points + int(pts)       
        htm.put()
        #update away team
        atk = db.Key.from_path('Team', int(self.request.get('away_team')))
        atm = db.get(atk)            
        atm.games_played = atm.games_played + 1
        pts = 0
        if int(self.request.get('home_team_score')) < int(self.request.get('away_team_score')):
            atm.games_won = atm.games_won + 1
            pts = t.points_for_win  
        elif int(self.request.get('home_team_score')) > 0 and (int(self.request.get('home_team_score')) == int(self.request.get('away_team_score'))):
            atm.games_drawn = atm.games_drawn + 1
            pts = t.points_for_score_draw
        elif int(self.request.get('home_team_score')) == 0 and (int(self.request.get('home_team_score')) == int(self.request.get('away_team_score'))):
            atm.games_drawn = atm.games_drawn + 1
            pts = t.points_for_draw             
        else:
            atm.games_lost = atm.games_lost + 1
            pts = t.points_for_lose
        atm.goals_for = atm.goals_for + int(self.request.get('away_team_score'))
        atm.goals_against = atm.goals_against + int(self.request.get('home_team_score'))
        atm.goal_difference = atm.goals_for - atm.goals_against
        atm.points =  atm.points + int(pts)       
        atm.put()
        #add result      
        result = Result(table=t,
            home_team_id=int(self.request.get('home_team')),
            home_team_name=htm.name,
            home_team_score=int(self.request.get('home_team_score')),
            away_team_id=int(self.request.get('away_team')),
            away_team_name=atm.name,
            away_team_score=int(self.request.get('away_team_score')),
            time_added=datetime.now()).put()
        table_id = str(t.key().id())
        table_object = 'result'
        return_page = 'Results'       
        object_action = 'added'
        object_url = 'getresults'        
        self.redirect('/displaymessage?table_id='+str(table_id)+'&table_object='+table_object+'&return_page='+return_page+'&object_action='+object_action+'&object_url='+object_url)

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
        score_options = range(200)
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
        rsk = db.Key.from_path('Result', int(self.request.get('result_id')))
        k = db.Key.from_path('Table', int(self.request.get('table_id')))        
        helperfunctions.deleteresult(rsk, k)
        table_id = self.request.get('table_id')
        table_object = 'result'
        return_page = 'Results'       
        object_action = 'deleted'
        object_url = 'getresults'
        result_set = self.request.get('result_set')
        self.redirect('/displaymessage?table_id='+str(table_id)+'&table_object='+table_object+'&return_page='+return_page+'&object_action='+object_action+'&object_url='+object_url+'&result_set='+result_set)

class GetShare(webapp.RequestHandler):
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
        url = './'
        url_linktext = 'Home'
        server_name = os.environ['SERVER_NAME']
        if (server_name == 'localhost'):
            server_port = ':'+os.environ['SERVER_PORT']
        else:
            server_port = ''
        viewable_url  = server_name+server_port+'?table='+str(self.request.get('table_name'))
        score_options = range(200)
        template_values = {
	    'tabledata': tb,
	    'teamsdata': tms,	    
	    'url': url,
	    'url_linktext': url_linktext,
	    'disable': disable,
            'disable2': disable2,
            'viewable_url': viewable_url,
            'score_options': score_options
        }
        path = os.path.join(os.path.dirname(__file__), 'share.html')
        self.response.out.write(template.render(path, template_values))
        for morsel in login_cookie.values():
            self.response.headers.add_header('Set-Cookie',morsel.OutputString(None))        

class MakeViewable(webapp.RequestHandler):
    def get(self):
        k = db.Key.from_path('Table', int(self.request.get('tbl_id')))
        t = db.get(k)
        #update viewable boolean
        t.viewable = bool(int(self.request.get('viewable')))
        t.put()
        self.redirect('/getshare?table_name=' + str(t.key().id()))

class ReceiveMessage(webapp.RequestHandler):
    def get(self):
        #collect the vars, test them though
        table_id = self.request.get('table_id')
        table_object = self.request.get('table_object')
        return_page = self.request.get('return_page')        
        object_action = self.request.get('object_action')
        object_url = self.request.get('object_url')
        result_set = self.request.get('result_set')
        try:
            result_set = int(result_set)
        except:
            result_set = 0        
        #call message object maker method
        #pass params on to the displayer
        self.redirect('/displaymessage?table_id='+str(table_id)+'&table_object='+table_object+'&return_page='+return_page+'&object_action='+object_action+'&object_url='+object_url+'&result_set='+result_set)        

class DisplayMessage(webapp.RequestHandler):
    def get(self):
        #parse the params method into template values
        table_id = int(self.request.get('table_id'))
        table_object = self.request.get('table_object')
        return_page = self.request.get('return_page')        
        object_action = self.request.get('object_action')
        object_url = self.request.get('object_url')
        result_set = self.request.get('result_set')        
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

class TestMessage(webapp.RequestHandler):
    def get(self):
        #build some vars to pass
        table_id = 298
        table_object = 'Result'
        object_action = 'Deleted'
        object_url = 'getresults'
        self.redirect('/receivemessage?table_id='+str(table_id)+'&table_object='+table_object+'&object_action='+object_action+'&object_url='+object_url)       

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
                                      ('/receivemessage', ReceiveMessage),
                                      ('/displaymessage', DisplayMessage),
                                      ('/testmessage', TestMessage)],
                                      debug=True)
 
def main():
    run_wsgi_app(application)
 
if __name__ == "__main__":
    main()
