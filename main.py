import logging
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
                        flow_template=default_flow)

                project.put()

            self.redirect('/dashboard')

        else:
            self.redirect(users.create_login_url('/new/'))

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


class SavePersonalDeets(webapp.RequestHandler):

    def post(self):

        user = users.get_current_user()
        company = models.Company.all().filter("owner =", user)[0]

        company.name = self.request.get("company_name")
        company.owner_name = self.request.get("person_name")

        company.put()

        self.redirect('/dashboard/')


class SaveEvidence(webapp.RequestHandler):

    def post(self):

        logging.info("wtf")

        user = users.get_current_user()
        company = models.Company.all().filter("owner =", user)[0]
        progress = models.Progress.all().filter("company =", company).order("-order")

        key = self.request.get("key")
        hypothesis = self.request.get("hypothesis")
        evidence = self.request.get("evidence")
        next_step_key = self.request.get("next_step")

        advance_to_next_step = self.request.get("advance_to_next_step", 'true') == 'true'
        logging.info( 'advance to next step: %s' % advance_to_next_step )
        logging.info( 'next step key: %s' % next_step_key )

        confidence = self.request.get("confidence")
        metric = self.request.get("metric")

        current_progress = models.Progress.get(key)
        if hypothesis:
            current_progress.hypothesis = hypothesis
        if evidence:
            current_progress.evidence = evidence
        if confidence:
            current_progress.confidence = confidence
        if metric:
            try:
                current_progress.metric = int(metric)
            except:
                current_progress.metric = 0

        current_progress.put()

        if next_step_key and advance_to_next_step:
            logging.info ('trying for next step')
            next_step = models.StepTemplate.get(next_step_key)
            logging.info ('got next step: %s' % next_step)

            next_progress = models.Progress(
                    step=next_step,
                    company=company,
                    order=models.Progress.all().filter("company =", company).count())
            logging.info ('made next progress')
            next_progress.put()
            logging.info('put next progress')

        self.redirect('/dashboard')


class AddEvidencePopup(webapp.RequestHandler):

    def get(self):

        user = users.get_current_user()
        key = self.request.get("progress")

        company = models.Company.all().filter("owner =", user)[0]
        progress = models.Progress.get(key)

        template_values = {
                'current_progress': progress,
                'next_step': progress.step.next(),
            }

        path = os.path.join(os.path.dirname(__file__), 'evidence_popup.html')
        self.response.out.write(template.render(path, template_values))


class EditProgressPopup(webapp.RequestHandler):

    def get(self):

        user = users.get_current_user()
        key = self.request.get("progress")

        company = models.Company.all().filter("owner =", user)[0]
        progress = models.Progress.get(key)

        template_values = {
                'current_progress': progress,
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


class SkipStep(webapp.RequestHandler):

    def get(self):

        user = users.get_current_user()
        company = models.Company.all().filter("owner =", user)[0]
        progress = models.Progress.all().filter("company =", company).order("-order")

        current_progress = None
        next_step = None

        if progress.count() >= 1:
            current_progress = progress[0]
            next_step = current_progress.step.next()

        if current_progress and next_step:

            #TODO: decide whether to mark this item as skipped or
            #just entirely delete it from the stream, which is what
            #is currently happening
            current_progress.delete()

            next_progress = models.Progress(
                    step=next_step,
                    company=company,
                    order=models.Progress.all().filter("company =", company).count())
            next_progress.put()

        self.redirect('/dashboard')



class CreateFirstProgress(webapp.RequestHandler):

    def get(self):

        user = users.get_current_user()
        company = models.Company.all().filter("owner =", user)[0]
        key = self.request.get("step")
        step = models.StepTemplate.get(key)

        first_progress = models.Progress(step=step,
                company=company,
                order=0)
        first_progress.put()

        self.redirect('/dashboard/')

        

class Dashboard(webapp.RequestHandler):

    def get(self):

        user = users.get_current_user()

        if not user:

            self.redirect(users.create_login_url('/dashboard/'))
            return

        companies = models.Company.all().filter("owner =", user)
        if companies.count() == 0: 
            self.redirect("/new/")
            return
        company = companies[0]

        progress = models.Progress.all().filter("company =", company).order("-order")
        flow = company.flow_template
        steps = models.StepTemplate.all().filter("flow =", flow).order("order")

        if progress.count() == 0:

            initial_step_options = steps.filter("is_valid_starting_point =", True)

            if initial_step_options.count() == 0:
                first_progress = models.Progress(step=steps[0],
                        company=company,
                        order=0)
                first_progress.put()
            elif initial_step_options.count() == 1:
                first_progress = models.Progress(step=initial_step_options[0],
                        company=company,
                        order=0)
                first_progress.put()
            else:
                #dashboard template will show a popup asking them to select an initial step
                pass

        current_progress = None
        prev_progress = None

        if progress.count() >= 1:
            current_progress = progress[0]
            progress = progress[1:progress.count()]

        if current_progress.step.prev():
            try:
                prev_progress = models.Progress.all().filter("step =", current_progress.step.prev()).order("-order")[0]
            except:
                prev_progress = None

        if current_progress is not None:
            template_values = {
                    'header_c2a_url': '/dashboard/',
                    'header_c2a_linktext': 'Dashboard',
                    'acct_url': users.create_logout_url(self.request.uri),
                    'acct_url_linktext': 'Logout',
                    'steps': steps,
                    'progress': progress,
                    'prev_progress': prev_progress,
                    'current_progress': current_progress,
                    'company': company,
                }
            path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
            self.response.out.write(template.render(path, template_values))
        else:
            template_values = {
                    'header_c2a_url': '/dashboard/',
                    'header_c2a_linktext': 'Dashboard',
                    'acct_url': users.create_logout_url(self.request.uri),
                    'acct_url_linktext': 'Logout',
                    'steps': initial_step_options,
                    'progress': progress,
                }
            path = os.path.join(os.path.dirname(__file__), 'starting_point.html')
            self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication([

        ('/', MainPage),
        ('/new/', NewProject),
        ('/new', NewProject),
        ('/dashboard/hypothesis/', SaveHypothesis_ajax),
        ('/dashboard/evidence/', SaveEvidence),
        ('/dashboard/create_first_progress/', CreateFirstProgress),
        ('/dashboard/skip_step/', SkipStep),
        ('/dashboard/pivot/', PivotPopup),
        ('/dashboard/edit_progress/', EditProgressPopup),
        ('/dashboard/save_personal_deets/', SavePersonalDeets),
        ('/dashboard/add_evidence/', AddEvidencePopup),
        ('/dashboard', Dashboard),
        ('/dashboard/', Dashboard),
        (r'^(/admin)(.*)$', appengine_admin.Admin),

        ], 
        debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
