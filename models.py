from google.appengine.ext import db
import appengine_admin



class FlowTemplate(db.Model):

    name = db.StringProperty()

    is_default = db.BooleanProperty(default=False)


class StepTemplate(db.Model):

    name = db.StringProperty()
    order = db.IntegerProperty()

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


class Progress(db.Model):

    step = db.ReferenceProperty(StepTemplate)
    company = db.ReferenceProperty(Company)

    order = db.IntegerProperty()

    hypothesis = db.StringProperty(default="", multiline=True)
    evidence = db.StringProperty(default="", multiline=True)

    timestamp = db.DateTimeProperty(auto_now_add=True)


class AdminFlowTemplate(appengine_admin.ModelAdmin):
    model = FlowTemplate


class AdminStepTemplate(appengine_admin.ModelAdmin):
    model = StepTemplate

appengine_admin.register(AdminFlowTemplate, AdminStepTemplate)


