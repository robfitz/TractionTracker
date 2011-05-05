from google.appengine.ext import db
import appengine_admin



class FlowTemplate(db.Model):

    name = db.StringProperty()

    is_default = db.BooleanProperty(default=False)

    def __unicode__(self):
        return unicode(self.name)


class StepTemplate(db.Model):

    name = db.StringProperty()
    order = db.IntegerProperty()
    tooltip = db.StringProperty()

    is_valid_starting_point = db.BooleanProperty(default=False)

    flow = db.ReferenceProperty(FlowTemplate)
    icon_url_base = db.StringProperty()


    def __unicode__(self):
        return unicode(self.name)

    def icon_big(self):
        return "/media/icons/%s_64.jpg" % self.icon_url_base

    def icon_small(self):
        return "/media/icons/%s_32.jpg" % self.icon_url_base

    def next(self):
        try:
            return StepTemplate.all().filter("flow =", self.flow).filter("order =", self.order + 1)[0]
        except:
            return self


class Company(db.Model):

    owner = db.UserProperty()
    name = db.StringProperty()

    flow_template = db.ReferenceProperty(FlowTemplate)
    
    def __unicode__(self):
        return unicode(self.name)


class Progress(db.Model):

    step = db.ReferenceProperty(StepTemplate)
    company = db.ReferenceProperty(Company)

    order = db.IntegerProperty()

    hypothesis = db.StringProperty(default="", multiline=True)
    evidence = db.StringProperty(default="", multiline=True)

    timestamp = db.DateTimeProperty(auto_now_add=True)


class AdminFlowTemplate(appengine_admin.ModelAdmin):
    model = FlowTemplate
    listFields = ('name', 'is_default')

class AdminStepTemplate(appengine_admin.ModelAdmin):
    model = StepTemplate
    listFields = ('name', 'order', 'tooltip','flow', 'icon_url_base')

class AdminCompany(appengine_admin.ModelAdmin):
    model = Company
    listFields = ('owner', 'name', 'flow_template')

class AdminProgress(appengine_admin.ModelAdmin):
    model = Progress
    listFields = ('step', 'company', 'order', 'hypothesis', 'evidence', 'timestamp')

appengine_admin.register(AdminFlowTemplate, AdminStepTemplate, AdminCompany, AdminProgress)


