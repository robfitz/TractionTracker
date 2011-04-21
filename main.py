import os
import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import models
import appengine_admin

#from google.appengine.dist import use_library
#use_library('django', '1.2')

from google.appengine.ext.webapp import template

class MainPage(webapp.RequestHandler):

    def get(self):

        user = users.get_current_user()

        if user:

            acct_url = users.create_logout_url(self.request.uri)
            acct_url_linktext = 'Logout'

            header_c2a_url = "/dashboard"
            header_c2a_linktext = "Dashboard"

        else:
            acct_url = users.create_login_url(self.request.uri)
            acct_url_linktext = 'Login'

            header_c2a_url = "/new"
            header_c2a_linktext = "Get started"

        template_values = {
                'header_c2a_url': header_c2a_url,
                'header_c2a_linktext': header_c2a_linktext,
                'acct_url': acct_url,
                'acct_url_linktext': acct_url_linktext
            }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


class NewProject(webapp.RequestHandler):

    def get(self):

        user = users.get_current_user()
        if user:

            project = None

            if not project:

                default_flow = models.FlowTemplate.all().filter("is_default =", True)[0]

                project = models.Company(
                        owner=user,
                        name="A wonderful company",
                        flow_template=default_flow)

                project.put()

            self.redirect('/dashboard')

        else:
            self.redirect(users.create_login_url('/new'))

class SaveHypothesis_ajax(webapp.RequestHandler):

    def post(self):

        user = users.get_current_user()
        company = models.Company.all().filter("owner =", user)[0]
        progress = models.Progress.all().filter("company =", company).order("-order")

        key = self.request.get("key")
        hypothesis = self.request.get("hypothesis")

        current_progress = models.Progress.get(key)
        current_progress.hypothesis = hypothesis
        current_progress.put()


class SaveEvidence(webapp.RequestHandler):

    def post(self):

        user = users.get_current_user()
        company = models.Company.all().filter("owner =", user)[0]
        progress = models.Progress.all().filter("company =", company).order("-order")

        key = self.request.get("key")
        hypothesis = self.request.get("hypothesis")
        evidence = self.request.get("evidence")
        next_step_key = self.request.get("next_step")

        current_progress = models.Progress.get(key)
        if hypothesis:
            current_progress.hypothesis = hypothesis
        if evidence:
            current_progress.evidence = evidence
        current_progress.put()

        if next_step_key:
            next_step = models.StepTemplate.get(next_step_key)

            next_progress = models.Progress(
                    step=next_step,
                    company=company,
                    order=models.Progress.all().filter("company =", company).count())
            next_progress.put()

        self.redirect('/dashboard')


class EditProgressPopup(webapp.RequestHandler):

    def get(self):

        user = users.get_current_user()
        key = self.request.get("progress")

        company = models.Company.all().filter("owner =", user)[0]
        progress = models.Progress.get(key)

        template_values = {
                'progress': progress,
            }

        path = os.path.join(os.path.dirname(__file__), 'edit_popup.html')
        self.response.out.write(template.render(path, template_values))


class PivotPopup(webapp.RequestHandler):

    def get(self):

        user = users.get_current_user()
        key = self.request.get("step")

        company = models.Company.all().filter("owner =", user)[0]
        progress = models.Progress.all().filter("company =", company).order("-order")
        current_progress = progress[0]

        pivot_to_step = models.StepTemplate.get(key)

        template_values = {
                'current_progress': current_progress,
                'next_step': pivot_to_step,
            }

        path = os.path.join(os.path.dirname(__file__), 'pivot_popup.html')
        self.response.out.write(template.render(path, template_values))
        

class Dashboard(webapp.RequestHandler):

    def get(self):

        user = users.get_current_user()

        if not user:

            self.redirect(users.create_login_url('/dashboard'))
            return

        company = models.Company.all().filter("owner =", user)[0]

        progress = models.Progress.all().filter("company =", company).order("-order")
        flow = company.flow_template
        steps = models.StepTemplate.all().filter("flow =", flow).order("order")

        if progress.count() == 0:
            first_progress = models.Progress(step=steps[0],
                    company=company,
                    order=0)
            first_progress.put()

        current_progress = progress[0]
        progress = progress[1:progress.count()]

        template_values = {
                'header_c2a_url': '/dashboard/',
                'header_c2a_linktext': 'Dashboard',
                'acct_url': users.create_logout_url(self.request.uri),
                'acct_url_linktext': 'Logout',
                'steps': steps,
                'progress': progress,
                'current_progress': current_progress,

            }
        path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
        self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication([

        ('/', MainPage),
        ('/new/', NewProject),
        ('/new', NewProject),
        ('/dashboard/hypothesis/', SaveHypothesis_ajax),
        ('/dashboard/evidence/', SaveEvidence),
        ('/dashboard/pivot/', PivotPopup),
        ('/dashboard/edit_progress/', EditProgressPopup),
        ('/dashboard', Dashboard),
        ('/dashboard/', Dashboard),
        (r'^(/admin)(.*)$', appengine_admin.Admin),

        ], 
        debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
