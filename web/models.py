from django.db import models
from django.contrib.auth.models import User
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
        
class City(models.Model):
    """Names of cities to be used"""
    name  = models.CharField(_("City"),max_length=50,unique=True)
    
    class Meta:
        verbose_name_plural = 'Cities'

    def __unicode__(self):
        return "%s" %(self.name)
        
class Member(models.Model):
    username = models.ForeignKey(User, related_name = "delegate_user_name",
                                   unique = True,verbose_name = _("User Name"))
    address = models.TextField(_("Address"))
    city = models.ForeignKey(City,verbose_name= _("Town or city"))
    occupation = models.ForeignKey(Occupation,
                                   related_name = "occupation", verbose_name = _("Occupation"))
    joindate = models.DateTimeField(_("Date of registration"),default=datetime.now,
                                    editable=False)
    membershiptype = models.CharField(_("Membershiptype"),max_length=1,choices=MEMBERSHIPTYPES)
    reason = models.TextField(_("Reason for joining"))
    admitted = models.BooleanField(_("Admitted"),default=False)
    admitdate = models.DateTimeField(_("Date of admission"),blank=True,null=True)
    

    def __unicode__(self):
        return User.objects.get(username=self.username.username).get_full_name()

    def get_absolute_url(self):
        return u"/memberfull/%d/" %(self.id)
        
class Subscription(models.Model):
    member = models.ForeignKey(Member,verbose_name=_("Member"))
    datepaid = models.DateField(_("Date paid"),blank=True,null=True)
    paid = models.BooleanField(_("Paid"),default = False)
    paymentdetails = models.TextField(_("Payment details"),blank=True,null=True)
    
    def __unicode__(self):
        return u"%s %s %s" %(self.member,self.year,self.paid)
        
class Vote(models.Model):
    voter = models.ForeignKey(Member,verbose_name = _("Committee member"))
    candidate = models.ForeignKey(Member,related_name=_("candidate"),verbose_name=_("Candidate"))
    votecast = models.CharField(_("Your vote"),max_length=2,choices = VOTES)
    
    class Meta:
        unique_together=('voter','candidate')
    def __unicode__(self):
        return u"%s %s %s" %(self.voter,self.candidate,self.votecast)
