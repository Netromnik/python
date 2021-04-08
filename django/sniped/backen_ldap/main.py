import ldap3
class settings():
    LDAP_HOST=""
    LDAP_PORT=
    BaseDN=""
    BindDN=""

class CustomLdapDriver(object):
    host = settings.LDAP_HOST
    port = settings.LDAP_PORT
    atr_full =  {
        "sAMAccountName", "givenName", "cn", "initials", "displayName", "memberOf", "department", "mail",
        "telephoneNumber", "description",
    }
    atr_shor = {
        "sAMAccountName", "givenName", "cn", "initials", "displayName", "memberOf", "department",
    }

    AUTH_LDAP_USER_ATTR_MAP = {
        "givenName": "first_name",
        "cn": "last_name",
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
        return username + "@" + settings.BindDN

    def proccess_auch_ldap(self, username, password):
        # test autch in ldap
        userPrincipalName = self.Upn(username)
        conn =ldap3.Connection(self.serv,userPrincipalName,password)
        self.connect(conn)
        conn.search(settings.BaseDN,"(userPrincipalName={})".format(userPrincipalName), attributes=self.atr_shor)
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
