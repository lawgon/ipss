from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.sites.models import Site

# Create your models here.

MEMBERSHIPTYPES=(
    ('D', _("Donor 1 lakh+")),
    ('C', _("Corporate 5K PA 1 vote")),
    ('A', _("Academic Institution 5K PA 1 vote")),
    ('R', _("Regular 500 PA")),
    ('S', _("Student 200 PA No vote")),
    )
    
VOTES=(
    ('A', _("Accept")),
    ('R', _("Reject")),
    ('N', _("Neutral")),
    )
    
DESCRIPTIONS=(
    ('1', _("Subscription 2010-2011")),
    ('2', _("Subscription 2011-2012")),
    ('3', _("Subscription 2012-2013")),
    ('4', _("Subscription 2013-2014")),
    ('5', _("Subscription 2014-2015")),
    ('6', _("Subscription 2015-2016")),
    ('7', _("Subscription 2016-2017")),
    ('8', _("Subscription 2017-2018")),
    ('9', _("Subscription 2018-2019")),
    )


class Tempreg(models.Model):
    username = models.CharField(_("User Name"),max_length=30,unique=True)
    email = models.EmailField(_("Email Address"),unique=True)
    date = models.DateField(_("Date"),default=datetime.now,editable=False)
    code = models.CharField(_("Code"),max_length=100,blank=True,null=True,
                                                    editable=False,default='123')
    
    def __unicode__(self):
           return _(u"%(username)s %(email)s")\
           %{'username': self.username,'email': self.email}
           
class Occupation(models.Model):   
    name = models.CharField(_("Occupation"),max_length=100,unique=True)

    def __unicode__(self):
        return self.name
class Category(models.Model):   
    name = models.CharField(_("Category"),max_length=100,unique=True)

    def __unicode__(self):
        return self.name
        
class City(models.Model):
    """Names of cities to be used"""
    name  = models.CharField(_("City"),max_length=50,unique=True)
    
    class Meta:
        verbose_name_plural = 'Cities'

    def __unicode__(self):
        return "%s" %(self.name)
        
class Member(models.Model):
    username = models.ForeignKey(User, related_name = "member_user_name",
                                   unique = True,verbose_name = _("User Name"))
    address = models.TextField(_("Address"))
    city = models.ForeignKey(City,verbose_name= _("Town or city"),
                            help_text=_("If your city is not mentioned add it from the menu on the left"))
    occupation = models.ForeignKey(Occupation,
                                   related_name = "occupation", verbose_name = _("Occupation"),
                                   help_text=_("If your occupation is not mentioned add it from the menu on the left"))
    joindate = models.DateTimeField(_("Date of registration"),default=datetime.now,
                                    editable=False)
    membershiptype = models.CharField(_("Membershiptype"),max_length=1,choices=MEMBERSHIPTYPES)
    companyname = models.CharField(_("Company or institution name"),max_length=200,blank=True,null=True,
                help_text=_("Only for institutional memberships"))
    reason = models.TextField(_("Reason for joining"))
    admitted = models.BooleanField(_("Admitted"),default=False)
    admitdate = models.DateTimeField(_("Date of admission"),blank=True,null=True)
    
    def memtypeshort(self):
        return self.get_membershiptype_display().split()[0]
    
    def iscommittee(self):
        return self.username.groups.filter(name='committee').count() > 0
    
    def accept(self):
        votes = self.candidate.all()
        tot = 0
        for vote in votes:
            if vote.votecast=='A':
                tot +=1
        return tot
    def acceptors(self):
        votes = self.candidate.all()
        acc=[]
        for vote in votes:
            if vote.votecast=='A':
                 acc.append(vote.voter)
        return acc
        		
    def reject(self):
        votes = self.candidate.all()
        tot = 0
        for vote in votes:
            if vote.votecast=='R':
                tot +=1
        return tot
    def rejectors(self):
        votes = self.candidate.all()
        rej = []
        for vote in votes:
            if vote.votecast=='R':
                rej.append(vote.voter)
        return rej
        
    def neutral(self):
        votes = self.candidate.all()
        tot = 0
        for vote in votes:
            if vote.votecast=='N':
                tot +=1
        return tot

    def neutors(self):
        votes = self.candidate.all()
        neu = []
        for vote in votes:
            if vote.votecast=='N':
                neu.append(vote.voter)
        return neu
    def __unicode__(self):
        if self.membershiptype in ['C','A']:
            return self.companyname
        else:
            return User.objects.get(username=self.username.username).get_full_name()
    def fullname(self):
        if self.membershiptype in ['C','A']:
            return self.companyname
        else:
            return User.objects.get(username=self.username.username).get_full_name()
    def pending(self):
        if not self.admitted:
            return (datetime.now()-self.joindate).days
    def paid(self):
        pd = True
        for sub in self.subscription_set.all():
            if self.admitted and not sub.paid:
                pd = False
        if not self.admitted:
            pd = False
        return pd
        

    def get_absolute_url(self):
        return u"/memberfull/%d/" %(self.id)
        
class Subscription(models.Model):
    member = models.ForeignKey(Member,verbose_name=_("Member"))
    amount = models.DecimalField(_("Amount"),max_digits=10,decimal_places=2)
    description = models.CharField(_("Description"),max_length=2,choices=DESCRIPTIONS)
    dategenerated = models.DateField(_("Date generated"))
    datepaid = models.DateField(_("Date paid"),blank=True,null=True,
                    help_text=_("yyyy-mm-dd"))    
    paymentdetails = models.TextField(_("Payment details"),blank=True,null=True)
    paid = models.BooleanField(_("Paid"),default = False)
    
    class Meta:
        unique_together = ('member','description')
    
    def __unicode__(self):
        return u"%s %s %s" %(self.member,self.description,self.paid)
        

        
class Vote(models.Model):
    voter = models.ForeignKey(Member,verbose_name = _("Committee member"))
    candidate = models.ForeignKey(Member,related_name=_("candidate"),verbose_name=_("Candidate"))
    votecast = models.CharField(_("Your vote"),max_length=2,choices = VOTES)
    
    class Meta:
        unique_together=('voter','candidate')
    def __unicode__(self):
        return u"%s %s %s" %(self.voter,self.candidate,self.votecast)
        
class Blog(models.Model):
    reporter = models.ForeignKey(Member,verbose_name=_("Member"))
    category = models.ForeignKey(Category,verbose_name=_("Category"))
    title = models.CharField(_("Title"),max_length=100)
    pubdate = models.DateField(_("Date of publication"),default = datetime.today,editable=False)
    matter = models.TextField(_("Matter"))
    class Meta:
        unique_together=('category','title')
        ordering =('-pubdate',)
    def __unicode__(self):
        return "%s by %s in %s" %(self.title,self.reporter,self.category)
        

