import os 
import cgi
import helperfunctions
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from dbmodel import User, Table
 
class MainPage(webapp.RequestHandler):
    def get(self):
        u = User.all()
        url = '../'
        url_linktext = 'Home'
        template_values = {
            'userdata': u,
            'url': url,
	    'url_linktext': url_linktext
            }
        path = os.path.join(os.path.dirname(__file__), 'admin/admin.html')
        self.response.out.write(template.render(path, template_values))

class DeleteUser(webapp.RequestHandler):
    def post(self):
        userk = db.Key.from_path('User', int(self.request.get('user_to_delete')))
        userd = db.get(userk)
        tbls = Table.all()
        tbls.filter('user = ', userk)
        for tbl in tbls:
            helperfunctions.deletetable(tbl.key())
        userd.delete()
        self.redirect('/admin/')        
        
application = webapp.WSGIApplication(
                                     [('/admin/', MainPage),
                                      ('/admin/deleteuser', DeleteUser)],
                                     debug=True)
 
def main():
    run_wsgi_app(application)
 
if __name__ == "__main__":
    main()
