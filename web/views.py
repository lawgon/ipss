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

menu_items = [

                {"name":_("Home"),"url":"home/","id":""},
                
                
              ]
logged_menu_items = [

                {"name":_("Application form"),"url":"edituser/","id":""},
                {"name":_("Pending Members"),"url":"pendingmembers/","id":""},
                {"name":_("Members"),"url":"members/","id":""},
                {"name":_("Add city"),"url":"addcity/","id":""},
                
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
    return render_to_response('web/user.html',
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
            self.fields['occupation'].choices = [(chld.id,
            chld.name) for chld in Occupation.objects.all()]
            self.fields['city'].choices = [(chld.id,
            chld.name) for chld in City.objects.all()]

    first_name = forms.CharField(max_length=30,
                                 label=_("First Name or Initials"),
                                 required=False)
    last_name = forms.CharField(max_length=30,
                                label=_("Last Name"),
                                required=True)
    address = forms.CharField(max_length=200,
                               label=_("Address"))
    
    city = forms.ChoiceField(
                               label=_("City"),
                               choices=())
    occupation = forms.ChoiceField(label=_("Occupation"),
                                   choices=()) 
                                   
    reason = forms.CharField(max_length=200,
                               label=_("Remarks"))
    pass1 = forms.CharField(max_length=50,widget=forms.PasswordInput,
                            label=_("Enter New Password"),
                            required=False)
    pass2 = forms.CharField(max_length=50,widget=forms.PasswordInput,
                            label=_("Enter New Password Again"),
                            required=False)


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
            newdel,created = Delegate.objects.get_or_create(username=request.user)
            newdel.address = fm['address']
            newdel.reason = fm['reason']
            newdel.occupation_id= int(fm['occupation'])
            newdel.city_id = int(fm['city'])
            changed = True
            newdel.save()
            
            return HttpResponseRedirect("/memberfull/%d/" %newdel.id )
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
            data['occupation'] = a.occupation.id
            data['city'] = a.city.id
            
            
            form = Edituserform(data)
        except:
            form = Edituserform(data)
    return render_to_response("web/edituser.html",
                              {'form':form,
                               'request':request,
                               })
                               
def sorry(request):
    t = loader.get_template("web/sorry.html")
    c = Context(
                {
                 "request":request,
                 })
    return HttpResponse(t.render(c))

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
