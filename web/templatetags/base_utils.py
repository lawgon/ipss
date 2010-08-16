from django.template import Library, Node, NodeList, resolve_variable
from django.template import TemplateSyntaxError, VariableDoesNotExist
from django.db.models import get_model
from web.models import *
from web.views import menu_items, logged_menu_items, admin_menu_items
import datetime

#sample taken form ubernostrums blog

register = Library()



#creates the menu. is it worth the effort to pass the page name?

class MenuNode(Node):
    def __init__(self):
        self.menu_items = menu_items

    def render(self, context):
        l = self.menu_items

        context['mn'] = l
        return ''

def get_menu(parser, token):
    return MenuNode()
get_menu = register.tag(get_menu)

class LoggedMenuNode(Node):
    def __init__(self):
        self.menu_items = logged_menu_items

    def render(self, context):
        l = self.menu_items

        context['lmn'] = l
        return ''

def get_logged_menu(parser, token):
    return LoggedMenuNode()
get_menu = register.tag(get_logged_menu)

class AdminMenuNode(Node):
    def __init__(self):
        self.menu_items = admin_menu_items

    def render(self, context):
        l = self.menu_items

        context['adm'] = l
        return ''

def get_admin_menu(parser, token):
    return AdminMenuNode()
get_menu = register.tag(get_admin_menu)











