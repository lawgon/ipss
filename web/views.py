# Create your views here.
from django.template import Context,loader,RequestContext
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render_to_response, get_object_or_404
from ipss.web.models import *
from django.template import Library, Node, NodeList, resolve_variable
from django.http import HttpResponse, Http404,HttpResponseRedirect,HttpResponseNotFound
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
import md5,re,os,random
from django import forms
from django.utils.encoding import smart_unicode
from django.conf import settings
from django.db import transaction
from django.db.models import get_model
from django.forms import ModelForm
from django.contrib.admin import widgets
from django.db.models.signals import post_save
from tekextensions.widgets import (SelectWithPopUp, MultipleSelectWithPopUp, FilteredMultipleSelectWithPopUp)

def isingroup(user,grp):
    """
    A function to check if the user is a member of the given group.
    """
    return user.is_authenticated() and user.groups.filter(name=grp).count() > 0

def makemsg(username,url):
    """
    Email body to be sent to user.
    """
    msg = _("\
Dear %(username)s,\n\n\
\
Thank you for registering with us. Please visit this url:\n\n\
%(url)s\n\n\
to complete the registration\n\n\
regards\n\
IPSS Team\
") %{'username': username,'url': url}
    return msg
    
def admit(username,url):
    """
    Email body to be sent to user.
    """
    msg = _("\
Dear %(username)s,\n\n\
\
Congratulations, your application has been accepted. please visit the following url:\n\n\
%(url)s\n\n\
and pay your subscription through netbanking or otherwise as described on the righthand column of the site\
 and enter payment details in the account status page\n\n\
regards\n\
IPSS Team\
") %{'username': username,'url': url}
    return msg
    
def rejectedmsg(username):
    """
    Email body to be sent to user
    """
    msg = _("Dear %(username)s, \n\n\
Your application for membership of Indian Python Software Society has not been able to get the minimum number of votes and has hence lapsed. It is possible that you have not given enough details about yourself and hence committee members have not been convinced. You are free to submit another application with more details.\n\
Regards,\n\
Indian Python Software Society\
") %{ 'username': username }
                                                            
    return msg

def comnotmsg(username,url):
    """
    Email body to be sent to user.
    """
    msg = _("\
Dear %(username)s,\n\n\
\
There has been a new membership application. Please visit:\n\n\
%(url)s\n\n\
and vote\n\n\
regards\n\
IPSS Team\
") %{'username': username,'url': url}
    return msg

menu_items = [

                {"name":_("Home"),"url":"home/","id":""},
                {"name":_("News"),"url":"news/","id":""},
                
                
              ]
logged_menu_items = [

                {"name":_("Members"),"url":"members/","id":""},
                {"name":_("Account Status"),"url":"status/","id":""},
                
              ]
admin_menu_items = [

                {"name":_("Pending Members"),"url":"pendingmembers/","id":""},
                
              ]
              
def index(request):
    """front page"""
    return render_to_response('web/index.html',context_instance=RequestContext(request,))

#____________________________________________________________
#user registration stuff



class TempRegisterform(forms.ModelForm):
    class Meta:
        model = Tempreg
        fields = ('username','email')

def register(request):
    """view to register a new user
        """
    if request.POST:
        form = TempRegisterform(request.POST)
        if form.is_valid():
            fm = form.cleaned_data
            if len(fm['username']) > 30 or len(fm['username']) < 4:
                form.errors['username']=[_("User Name must be 4-30 characters long")]
            else:
                r = re.compile(r"[A-Za-z0-9_]")
                for alph in fm['username']:
                    if  not r.match(alph):
                        form.errors['username']=[_("Invalid character %s in Username") %(alph)]
                if not form.errors:
                    test = User.objects.filter(username__iexact=fm['username'])
                    if test:
                        form.errors['username'] = [("Username registered, try something else")]
                    else:
                        test1 = Tempreg.objects.filter(username__iexact=fm['username'])
                        if test1:
                            form.errors['username'] = [_("Username pending registration. Try tomorrow")]
                    teste = User.objects.filter(email__iexact=fm['email'])
                    if teste:
                        form.errors['email'] = [_("Email registered. Try something else")]
                    else:
                        teste1 = Tempreg.objects.filter(email__iexact=fm['email'])
                        if teste1:
                            form.errors['email'] = [("Username pending registration. Try tomorrow")]
            if not form.errors:
                new_reg = form.save()
                new_reg.code = str(random.random())[2:]
                new_reg.save()
                lst = Tempreg.objects.filter(date__lt=datetime.now() - timedelta(1))
                for p in lst:
                    p.delete()
                url = "http://ipss.org.in/adduser/%s/" %(new_reg.code)
                mg = makemsg(new_reg.username,url)
                subj = "Registration for %s at ipss.org.in"\
                       %(new_reg.username)
                frm = "webmaster@ipss.org.in"
                to = [new_reg.email]
                send_mail(subj,mg,frm,to,fail_silently=False)
                return HttpResponseRedirect("/regthank/%i/" % new_reg.id)
    else:
        form = TempRegisterform()
    return render_to_response('web/register.html',
                        context_instance=RequestContext(request,
    
                              {"form":form.as_table(),
                               "request":request,
                               }))
                               
def regthank(request,id):
    """need just one view for all messages and warnings
        """
    p = Tempreg.objects.get(pk=id)
    t = loader.get_template("web/regthank.html")
    c = Context(
                {"p":p,
                 "request":request,
                 })
    return HttpResponse(t.render(c))
    
class Adduserform(forms.Form):
    username = forms.CharField(max_length=30,label=_("Username"))
    pass1 = forms.CharField(max_length=50,widget=forms.PasswordInput,
                                            label=_("Enter Password"))
    pass2 = forms.CharField(max_length=50,widget=forms.PasswordInput,
                                            label=_("Enter Password Again"))
    def clean_pass2(self):
        if len(self.cleaned_data['pass1']) < 6:
            raise forms.ValidationError('Password must be at\
            least 6 letters long')
        else:
            if self.cleaned_data['pass1'] != self.cleaned_data['pass2']:
                raise forms.ValidationError('Passwords do not match')
                
@transaction.commit_on_success    
def adduser(request,code):
    """view to add a user given the username and password
        """
    if code:
        try:
            usr = Tempreg.objects.get(code__exact=code)
            data = {}
            if usr:
                data['email']=usr.email
                data['code']=usr.code
                data['username']=usr.username
        except:
            return HttpResponseRedirect('/sorry/')
    if request.POST:
        form = Adduserform(request.POST)
        if form.is_valid():
            fm = form.cleaned_data
            if fm['username'] != data['username']:
                    form.errors['username'] = [_("Type your username exactly\
                    as you entered it before")]
            if not form.errors:
                newuser = User.objects.create_user(username=fm['username'],
                                        email=data['email'],
                                        password=fm['pass1'])
                newuser.save()
                oldreg = Tempreg.objects.get(username=fm['username'])
                oldreg.delete()
                user = authenticate(username=fm['username'], 
                    password=fm['pass1'])
                login(request,user)
                return HttpResponseRedirect('/edituser/')
    else:
        form = Adduserform()
    return render_to_response('web/adduser.html',
                        context_instance=RequestContext(request,
                              {'form':form.as_table(),
                               'request':request,
                               }))

class Edituserform(forms.Form):
    """
    Form to edit the user credentials.
    """
    def __init__(self, *args, **kwargs):
            super(Edituserform, self).__init__(*args, **kwargs)
            # Generate choices
            self.fields['city'].widget = SelectWithPopUp(model='City')
            self.fields['occupation'].widget = SelectWithPopUp(model='Occupation')
            self.fields['city'].choices = [(chld.id,
            chld.name) for chld in City.objects.all()]
            self.fields['occupation'].choices = [(chld.id,
            chld.name) for chld in Occupation.objects.all()]

    first_name = forms.CharField(max_length=30,
                                 label=_("First Name or Initials"),
                                required=False)
    last_name = forms.CharField(max_length=30,
                                label=_("Last Name"),
                                required=True)
    address = forms.CharField(max_length=200,
                               label=_("Address"),widget=forms.Textarea)
    city = forms.ChoiceField(
                               label=_("City"),
                               choices=())
    occupation = forms.ChoiceField(label=_("Occupation"),
                                   choices=()) 
    membershiptype = forms.ChoiceField(label=_("Type of membership"),
                                   choices=MEMBERSHIPTYPES) 
    companyname = forms.CharField(max_length=200,
                               label=_("Company or institute name"),help_text=_("Only for institutional memberships"),
                               required=False)
    reason = forms.CharField(max_length=200,
                               label=_("Reason for wanting to join"),widget=forms.Textarea)
    pass1 = forms.CharField(max_length=50,widget=forms.PasswordInput,
                            label=_("Enter New Password"),
                            required=False)
    pass2 = forms.CharField(max_length=50,widget=forms.PasswordInput,
                            label=_("Enter New Password Again"),
                            required=False)
                            
    agree = forms.BooleanField(label=_("I agree with the aims of the society"),initial=False)


    def clean_pass2(self):
        """
        Check if the passwords are the same and are atleast 6 characters long.
        """
        if not self.cleaned_data['pass1'] and not self.cleaned_data['pass2']:
            return None
        if self.cleaned_data['pass1'] != self.cleaned_data['pass2']:
                raise forms.ValidationError('Passwords do not match')
        if len(self.cleaned_data['pass1']) < 6:
                raise forms.ValidationError('Password must be at least 6 letters long')
        return self.cleaned_data['pass2']
    def clean_companyname(self):
        if self.cleaned_data.get('membershiptype') in ['A','C'] and not self.cleaned_data.get('companyname'):
            raise forms.ValidationError('Enter institution name as this is an institute membership')
        if self.cleaned_data.get('membershiptype') not in ['A','C'] and self.cleaned_data.get('companyname'):
            raise forms.ValidationError('Remove institution name as this is an individual membership')
        return self.cleaned_data['companyname']
        
@user_passes_test(lambda u: u.is_anonymous()==False ,login_url="/login/")  
@transaction.commit_on_success
def edituser(request):
    """
    Function to save the edited user credentials along with city and organisation
    """


    if request.POST:
        # On POST request.
        
        form = Edituserform(request.POST)
        if form.is_valid():
            fm = form.cleaned_data
            newuser = User.objects.get(pk=request.user.id)
            newuser.first_name = fm['first_name']
            newuser.last_name = fm['last_name']
            if fm.get('pass1') and fm.get('pass2'):
                newuser.set_password(fm['pass1'])
            newuser.save()
            changed = False
            try:
                
                newdel = Member.objects.get(username=request.user)
                newdel.address = fm['address']
                newdel.reason = fm['reason']
                newdel.occupation_id= int(fm['occupation'])
                newdel.city_id = int(fm['city'])
                newdel.membershiptype = fm['membershiptype']
                if fm.get('companyname'):
                    newdel.companyname = fm['companyname']
            except:
                newdel = Member.objects.create(username_id=request.user.id,
                    address = fm['address'],
                    reason = fm['reason'],
                    occupation_id= int(fm['occupation']),
                    city_id = int(fm['city']),
                    membershiptype = fm['membershiptype'])
                if fm.get('companyname'):
                    newdel.companyname = fm['companyname']
            changed = True
            newdel.save()
            
            return HttpResponseRedirect("/status/")
    else:
        id = request.user.id
        usr = User.objects.get(pk=id)
        data = {
                 'username'  : usr.username,
                 'first_name':usr.first_name,
                 'last_name' : usr.last_name
               }
        try:
            a = Member.objects.get(username=request.user)
            data['address'] = a.address
            data['membershiptype'] = a.membershiptype
            data['reason'] = a.reason
            data['occupation'] = a.occupation.id
            data['city'] = a.city.id
            data['companyname'] = a.companyname
            
            form = Edituserform(data)
        except:
            form = Edituserform(data)
    return render_to_response('web/edituser.html',
                        context_instance=RequestContext(request,
                              {'form':form,
                               'request':request,
                               }))
                               
def sorry(request):
    return render_to_response('web/sorry.html',
                        context_instance=RequestContext(request,))

@user_passes_test(lambda u: u.is_anonymous()==False ,login_url="/login/")                        
def status(request):
    return render_to_response('web/status.html',
                        context_instance=RequestContext(request,))
                        
@user_passes_test(lambda u: u.is_anonymous()==False ,login_url="/login/")                        
def members(request):
    mems = Member.objects.filter(admitted=True)
    sub = Subscription.objects.filter(paid=False)
    return render_to_response('web/members.html',
                        context_instance=RequestContext(request,
                                {'mems':mems, 'sub':sub}))
    

class Cityaddform(ModelForm):
    class Meta:
        model = City
        
@user_passes_test(lambda u: u.is_anonymous()==False ,login_url="/login/")
def addcity(request):
    """creates or edits a account
        """
    if request.POST:
        if 'cancel' in request.POST.keys():
            return HttpResponseRedirect('/addcity/')
        form = Cityaddform(request.POST)
        if form.is_valid():
            f=form.save()
            return HttpResponseRedirect('/addcity/')
    else:
        form = Cityaddform()
    return render_to_response('web/addcity.html',
                        context_instance=RequestContext(request,
                          {'form': form,
                          }))
                          
class Occupationaddform(ModelForm):
    class Meta:
        model = Occupation
        
@user_passes_test(lambda u: u.is_anonymous()==False ,login_url="/login/")
def addoccupation(request):
    """creates or edits a account
        """
    if request.POST:
        if 'cancel' in request.POST.keys():
            return HttpResponseRedirect('/addoccupation/')
        form = Occupationaddform(request.POST)
        if form.is_valid():
            f=form.save()
            return HttpResponseRedirect('/addoccupation/')
    else:
        form = Occupationaddform()
    return render_to_response('web/addoccupation.html',
                        context_instance=RequestContext(request,
                          {'form': form,
                          }))
                          
class Subscriptionaddform(ModelForm):
    
    class Meta:
        model = Subscription
        fields = ('datepaid','paymentdetails')
        
@user_passes_test(lambda u: u.is_anonymous()==False ,login_url="/login/")
def addsubscription(request,id):
    """
    Function to add/edit subscription.
    """
    
    instance = Subscription.objects.get(pk=id)
    if instance.member.username.id != request.user.id:
        return HttpResponseRedirect('/message/%s/' %('NO'))

    if request.POST:
        form = Subscriptionaddform(request.POST,instance=instance)
        if form.is_valid():
            fm = form.save()
            
            return HttpResponseRedirect('/status/')
    else:
        form = Subscriptionaddform(instance=instance)

    return render_to_response("web/addsubscription.html",
                              context_instance=RequestContext(request,{'form':form
                                                                }))
                                                                
@user_passes_test(lambda u: isingroup(u,'committee') == True,login_url="/login/")                                                                
def pendingmembers(request):
    pms = Member.objects.filter(admitted=False)
    vote = Vote.objects.all()
    return render_to_response("web/pendingmembers.html",
                              context_instance=RequestContext(request,{'pms':pms,'vote':vote
                                                                }))
                                                                
class Voteaddform(ModelForm):
    def __init__(self,mem,can, *args, **kwargs):
            super(Voteaddform, self).__init__(*args, **kwargs)
            self.mem = mem
            self.can = can
            # Generate choices
            self.fields['voter'].choices = [(chld.id,chld)
            for chld in Member.objects.filter(pk=self.mem)]
            self.fields['candidate'].choices = [(chld.id,
            chld) for chld in Member.objects.filter(pk=self.can)]
    
    class Meta:
        model = Vote
@user_passes_test(lambda u: isingroup(u,'committee') == True,login_url="/login/")        
def vote(request,id):
    pm = Member.objects.get(pk=id)
    can = pm.id
    mem = Member.objects.get(username=request.user).id
    if request.POST:
        form = Voteaddform(mem,can,request.POST)
        if form.is_valid():
            fm = form.save()
            
            return HttpResponseRedirect('/pendingmembers/')
    else:
        form = Voteaddform(mem,can)
    return render_to_response("web/vote.html",
                              context_instance=RequestContext(request,{'pm':pm,
                                                                        'form':form,
                                                                }))
                                                                
def generateinvoice(mem):
    amt = 600
    if mem.membershiptype == 'D':
        amt = 100100
    if mem.membershiptype == 'C':
        amt = 5100
    if mem.membershiptype == 'A':
        amt = 5100
    if mem.membershiptype == 'S':
        amt = 300
    dscr = '1'
    sub = Subscription.objects.create(amount= amt,
                                        member=mem,
                                        description=dscr,
                                        dategenerated=datetime.today())
    return 1
    
def news(request):
    news = Blog.objects.all()
    return render_to_response('web/news.html',context_instance=RequestContext(request,{'news':news}))
    
def newsfull(request,id):
    nw = Blog.objects.get(pk=id)
    return render_to_response('web/newsfull.html',context_instance=RequestContext(request,{'nw':nw}))
    
        
        
def applicationhandler(sender,**kwargs):
    """
        if created then mail goes to committee, if admitted then
        a subscription is created.
        """
    print "Hellow world"
    frm = settings.DEFAULT_FROM_EMAIL

    mems = Member.objects.filter(admitted=False)
    subj = _("Sorry!!! Your Application got rejected")  
    for cm in mems:
        tot= cm.accept()-cm.reject()
        print "Total Votes:",tot
        a=cm.pending()
        print "Pending for",a

        if (tot<3 and a>30):
                msg = rejectedmsg(cm.username)
                to = [cm.email()]
                print to, msg
                send_mail(subj,msg,frm,to)
                print "Caution: DELETED"
                cm.delete()
            
    if kwargs['created']:
        print "Hellow world2"
        subj = _("New membership application") 
        url = "http://%s/pendingmembers/" %(Site.objects.get_current().domain)
        
        com = Group.objects.get(name="committee")
        for cm in com.user_set.all():
            to = [cm.email]
            msg = comnotmsg(cm.username,url)
            send_mail(subj,msg,frm,to)
            
    else:
        if kwargs['instance'].admitted:
            print "Hellow world3"
            try:
                Subscription.objects.get(member=kwargs['instance'],description='1')
            except:
                generateinvoice(kwargs['instance'])
            url = "http://%s/status/" %(Site.objects.get_current().domain)
            print kwargs['instance']
            msg = admit(kwargs['instance'],url)
            subj = _("IPSS: Acceptance of your application")
            to = [kwargs['instance'].username.email]
            send_mail(subj,msg,frm,to)
        
   
post_save.connect(applicationhandler, sender=Member,dispatch_uid="member")

def paymenthandler(sender,**kwargs):
    """
        if created then mail goes to committee, if admitted then
        a subscription is created.
        """
    frm = settings.DEFAULT_FROM_EMAIL
    if not kwargs['created']:
        if (not kwargs['instance'].paid) and (kwargs['instance'].paymentdetails):
            subj = _("payment made") 
            url = "http://%s/admin/web/subscription/%d/" %(Site.objects.get_current().domain,
                                                            int(kwargs['instance'].id))
            msg = _("Please verify the payment and mark as paid\n\n%s") % (url)
            com = Group.objects.get(name="treasurer")
            for cm in com.user_set.all():
                to = [cm.email]
                
                send_mail(subj,msg,frm,to)
                
    
        
   
post_save.connect(paymenthandler, sender=Subscription, dispatch_uid="subscription")



    

    


            
