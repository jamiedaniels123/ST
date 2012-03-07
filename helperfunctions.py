import sys
import re
from google.appengine.ext import db
from dbmodel import Table, Team, Result
from types import NoneType
import translate
import logging

def deletetable(tablek):
    tb = db.get(tablek)
    tms = Team().all()
    tms.filter('table = ', tablek)
    for tm in tms:
        deleteteam(tm.key(), tablek)
    tb.delete()

def transfertables(tempuser, uid):
    #get user key from id
    uk = db.Key.from_path('User', uid)
    for tu in tempuser:
        for t in tu.tables:
            t.user = uk
            t.put()   

def deleteteam(teamk , tablek):
    teamt = db.get(teamk)    
    #get all home results for this team
    htmrs = Result().all()
    htmrs.filter('home_team_id = ', teamk.id())
    #delete all home results for this team
    for rsk_home in htmrs:
        deleteresult(rsk_home.key(), tablek)
    #get all away results for this team
    atmrs = Result().all()
    atmrs.filter('away_team_id = ', teamk.id())    
    #delete all away results for this team
    for rsk_away in atmrs:
        deleteresult(rsk_away.key(), tablek)    
    #delete team
    teamt.delete()

def deleteresult(rsk, k):
    rs = db.get(rsk)
    t = db.get(k)
    #update home team
    htk = db.Key.from_path('Team', rs.home_team_id)
    htm = db.get(htk)            
    htm.games_played = htm.games_played - 1
    pts = 0
    if rs.home_team_score > rs.away_team_score:
        htm.games_won = htm.games_won - 1
        pts = t.points_for_win  
    elif rs.home_team_score > 0 and (rs.home_team_score == rs.away_team_score):
        htm.games_drawn = htm.games_drawn - 1
        pts = t.points_for_score_draw
    elif rs.home_team_score == 0 and (rs.home_team_score == rs.away_team_score):
        htm.games_drawn = htm.games_drawn - 1
        pts = t.points_for_draw             
    else:
        htm.games_lost = htm.games_lost - 1
        pts = t.points_for_lose
    htm.goals_for = htm.goals_for - rs.home_team_score
    htm.goals_against = htm.goals_against - rs.away_team_score
    htm.goal_difference = htm.goals_for - htm.goals_against
    htm.points =  htm.points - int(pts)       
    htm.put()
    #update away team
    atk = db.Key.from_path('Team', rs.away_team_id)
    atm = db.get(atk)            
    atm.games_played = atm.games_played - 1
    pts = 0
    if rs.home_team_score < rs.away_team_score:
        atm.games_won = atm.games_won - 1
        pts = t.points_for_win  
    elif rs.home_team_score > 0 and (rs.home_team_score == rs.away_team_score):
        atm.games_drawn = atm.games_drawn - 1
        pts = t.points_for_score_draw
    elif rs.home_team_score == 0 and (rs.home_team_score == rs.away_team_score):
        atm.games_drawn = atm.games_drawn - 1
        pts = t.points_for_draw             
    else:
        atm.games_lost = atm.games_lost - 1
        pts = t.points_for_lose
    atm.goals_for = atm.goals_for - rs.away_team_score
    atm.goals_against = atm.goals_against - rs.home_team_score
    atm.goal_difference = atm.goals_for - atm.goals_against
    atm.points =  atm.points - int(pts)       
    atm.put()
    #delete result        
    rs.delete()

def parse_accept_language(accept_language):
    if not accept_language: return []
    ll=[ v.strip().split(';') for v in accept_language.split(',') ]
    ll=[ len(l)==1 and l.append(1.0) or l for l in ll]
    ll=[ [l[0],float(re.sub('q\s*=\s*','',str(l[1])))] for l in ll]    
    ll=[ l[0] for l in sorted(ll,lambda l1,l2: l1[1] > l2[1]) ] 
    ll=[ re.sub('-','_',l).lower() for l in ll ]
    return ll

def get_messages(languages=[]):
    msgs=translate.en
    for lang in languages:
        if hasattr(translate,lang):
            msgs=getattr(translate,lang)            
            logging.debug('languages='+str(languages)+', using '+str(lang))
            break
    return msgs

    
    
