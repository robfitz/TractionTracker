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
    
    numeric_question = db.StringProperty(default="How many customers have you interviewed")


    def __unicode__(self):
        return unicode(self.name)

    def icon_big_gray(self):
        return "/media/icons/%s_grey_64.jpg" % self.icon_url_base

    def icon_big(self):
        return "/media/icons/%s_64.jpg" % self.icon_url_base

    def icon_small(self):
        return "/media/icons/%s_32.jpg" % self.icon_url_base

    def prev(self):
        try:
            return StepTemplate.all().filter("flow =", self.flow).filter("order =", self.order - 1)[0]
        except:
            return None

    def next(self):
        try:
            return StepTemplate.all().filter("flow =", self.flow).filter("order =", self.order + 1)[0]
        except:
            return self


class Company(db.Model):

    owner = db.UserProperty()
    name = db.StringProperty(default="A wonderful company")
    owner_name = db.StringProperty("A splendid person")

    flow_template = db.ReferenceProperty(FlowTemplate)
    
    def __unicode__(self):
        return unicode(self.name)


class Progress(db.Model):

    step = db.ReferenceProperty(StepTemplate)
    company = db.ReferenceProperty(Company)

    order = db.IntegerProperty()

    hypothesis = db.StringProperty(default="", multiline=True)
    evidence = db.StringProperty(default="", multiline=True)
    confidence = db.StringProperty(default="",choices=[
      'Very High', 'High', 'Medium', 'Low', 'Very Low'])
    metric = db.StringProperty(default="0")

    timestamp = db.DateTimeProperty(auto_now_add=True)


    def progress_img(self):

        icon = ""

        if self.has_pivoted():
            icon = "pivot.jpg"
        elif self.confidence in ["Very High", "High"]:
            icon = "traffic_green.jpg"
        elif self.confidence in ["Medium"]:
            icon = "traffic_amber.jpg"
        elif self.confidence in ["Low", "Very Low"]:
            icon = "traffic_red.jpg"

        if icon:
            return "/media/icons/%s" % icon
        else:
            return ""


    def in_progress(self):

        #still in progress if we haven't yet moved on to anything new
        return not self.next()


    def has_validated(self):

        next = self.next()
        if not next: 
            return False
        else:
            #we've validated if the next progress item refers
            #to a later step (or repeats the current one)
            return next.step.order > self.step.order


    def has_pivoted(self):

        next = self.next()
        if not next: 
            return False
        else:
            #we've pivoted if the next progress item refers
            #to an earlier step (or repeats the current one)
            return next.step.order <= self.step.order


    def next(self):
        progress =  Progress.all().filter("company =", self.company).filter("order =", self.order + 1)[0]

        if not progress:
            return False
        return progress


class AdminFlowTemplate(appengine_admin.ModelAdmin):
    model = FlowTemplate
    listFields = ('name', 'is_default')

class AdminStepTemplate(appengine_admin.ModelAdmin):
    model = StepTemplate
    listFields = ('name', 'order', 'tooltip', 'is_valid_starting_point', 'flow', 'icon_url_base', 'numeric_question')

class AdminCompany(appengine_admin.ModelAdmin):
    model = Company
    listFields = ('owner', 'name', 'flow_template')

class AdminProgress(appengine_admin.ModelAdmin):
    model = Progress
    listFields = ('step', 'company', 'order', 'hypothesis', 'evidence', 'confidence', 'metric', 'timestamp')

appengine_admin.register(AdminFlowTemplate, AdminStepTemplate, AdminCompany, AdminProgress)


