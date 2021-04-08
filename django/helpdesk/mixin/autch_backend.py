from socket import AF_UNIX, SOCK_DGRAM, socket,timeout
import json,ldap3
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group as CustomGroup
UserModel = get_user_model()
from django.contrib.auth.backends import ModelBackend
import os
import re
DEFAULT_GROUP_FOR_LDAP ="LDAP_USER"
from django.conf import settings
import logging
import time

logger = logging.getLogger(__name__)

class CustomLdapDriver(object):
    host = settings.LDAP_HOST
    port = settings.LDAP_PORT
    atr_full =  {
        "sAMAccountName", "givenName", "sn", "initials", "displayName", "memberOf", "department", "mail",
        "telephoneNumber", "description",
    }
    atr_shor = {
        "sAMAccountName", "givenName", "sn", "initials", "displayName", "memberOf", "department",
    }

    AUTH_LDAP_USER_ATTR_MAP = {
        "givenName": "first_name",
        "sn": "last_name",
        # "displayName": "full_name_ldap",
        # "mail": "email",
        "memberOf": "groups",
    }


    def connect(self,conn):
        conn.unbind()
        if conn.bind():
            return
        else:
            raise ("Not bind")


    def __init__(self):
        self.serv =ldap3.Server(host=self.host,port=self.port)

    def __delete__(self, instance):
        self.conn.unbind()


    def Upn(self,username):
        return username + "@" + settings.LDAP_BINDDN

    def proccess_auch_ldap(self, username, password):
        # test autch in ldap
        userPrincipalName = self.Upn(username)
        conn =ldap3.Connection(self.serv,userPrincipalName,password)
        self.connect(conn)
        conn.search(settings.LDAP_BASEDN,"(userPrincipalName={})".format(userPrincipalName), attributes=self.atr_shor)
        env = conn.entries
        if len(env)!=1:
            return
        valid_date = self.valid_date_ldap(env[0])
        data = self.conver_ldap_to_django(valid_date)
        return data

    def valid_date_ldap(self,data):
        slov = dict()
        for i in self.atr_shor:
            try:
                d = getattr(data, i)
                if len(d) != 0:
                    if i == "memberOf":
                        d = list(d)
                    slov[i]=d
            except ldap3.core.exceptions.LDAPCursorAttributeError:
                pass
        return slov

    def conver_ldap_to_django(self, date):
        slov = dict()
        for k in date.keys():
            if k in self.AUTH_LDAP_USER_ATTR_MAP.keys():
                slov[self.AUTH_LDAP_USER_ATTR_MAP[k]] = date[k]
        return slov

class CheckUserDjango():
    IGNORE_ATTR = ["groups",]

    def is_valid_user(self, username):
        try:
            user = UserModel._default_manager.get(username=username)
            return user
        except UserModel.DoesNotExist:
            return None

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def get_user(self, user_id):
        try:
            user = UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None


    def groups_a(self,gr_list):
        q = list()
        if gr_list == None:
            gr, flag = CustomGroup.objects.get_or_create(name=DEFAULT_GROUP_FOR_LDAP)
            q.append(gr)
            return q
         
        result = [ re.findall(r'CN=\w*', gr)[0] for gr in gr_list ]
        result.append("CN="+DEFAULT_GROUP_FOR_LDAP)
        result = list(set(result))
        for g in result:
            _,gr = g.split("=")
            gr ,flag = CustomGroup.objects.get_or_create(name=gr)
            q.append(gr)
        return q

    def attr_user_update(self,user,date):
        for k in date.keys():
            if k not in self.IGNORE_ATTR:
                setattr(user,k,date[k])
        user.save()
        return user


    def user_create(self,username,date):
        groups = self.groups_a(date.get("groups"))
        date['username'] = username
        user = UserModel(username=username)
        user = self.attr_user_update(user, date)
        user.is_active = True
        user.save()
        user.groups.add(*groups)
        user.save()
        return user

    def update_user(self,user,date):

        # update user
        self.attr_user_update(user, date)
        groups = self.groups_a(date.get("groups"))
        ugroups = list(user.groups.all())
        res = [x for x in groups + ugroups if x not in groups or x not in ugroups]
        if not res:
            return user
        else:
            user.groups.add(*res)
            user.save()
            return user
        raise AssertionError('case down')

class LdapBackend(CustomLdapDriver, CheckUserDjango, ModelBackend,):

    def authenticate(self, request, username=None, password=None, **kwargs):
        password = password
        user = self.is_valid_user(username)
        if user!=None:
            if user.is_superuser:
                return user
        # Check the username/password and return a User.
        try:
            data = self.proccess_auch_ldap(username, password)
        except:
            return None
        if data == None:
            return None

        if user is None:
            user = self.user_create(username,data)
            user.save()
            return  self.authenticate(request,username,password,**kwargs)
        else:
            user =self.update_user(user,data)
            user.save()
            return user
