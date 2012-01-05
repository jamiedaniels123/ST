from google.appengine.ext import db
 
class User(db.Model):
    username = db.UserProperty()
    tempusername = db.StringProperty()
  
class Table(db.Model):
    user = db.ReferenceProperty(User, collection_name='tables')
    name = db.StringProperty()
    points_for_win = db.IntegerProperty()
    points_for_draw = db.IntegerProperty()
    points_for_score_draw = db.IntegerProperty()
    points_for_lose = db.IntegerProperty()
    viewable = db.BooleanProperty()
    
class Team(db.Model):
    table = db.ReferenceProperty(Table, collection_name='teams')
    name = db.StringProperty()
    games_played = db.IntegerProperty()
    games_won = db.IntegerProperty()
    games_drawn = db.IntegerProperty()
    games_lost = db.IntegerProperty()
    goals_for = db.IntegerProperty()
    goals_against = db.IntegerProperty()
    goal_difference = db.IntegerProperty()
    points_deducted = db.IntegerProperty()
    points = db.IntegerProperty()

class Result(db.Model):
    table = db.ReferenceProperty(Table, collection_name='results')
    home_team_id = db.IntegerProperty()
    home_team_name = db.StringProperty()    
    home_team_score = db.IntegerProperty()
    away_team_id = db.IntegerProperty()
    away_team_name = db.StringProperty()    
    away_team_score = db.IntegerProperty()
    time_added = db.DateTimeProperty()

    
    
