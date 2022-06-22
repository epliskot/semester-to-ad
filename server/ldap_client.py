from ldap3 import Server, Connection, Reader, ObjectDef, Writer, extend, NTLM
from ldap3.core.exceptions import LDAPInvalidDnError
import os

class LdapClient:


    def create_group(self, group_name):
        # Kjør ldap3-kall for å opprette gruppen
        return None

    def connect(self):
        #self.log.info(
         #   f"Establishing new connection to the LDAP server {self.ldap_fqdn} on port {self.ldap_port}. Use SSL set to {self.use_ssl}")

        if not self.server:
            raise RuntimeError(
                "It looks like ldap_client's init method hasn't been executed properly, as self.server is none.")

        try:
            # self.connection = Connection(self.server, user="nmbu\\" + self.bind_user, password=self.bind_password,
            #                             authentication='NTLM')
            self.connection = Connection(self.server, user="nmbu\\" + os.getenv('my_user') , password= os.getenv('my_password'),
                                         authentication='NTLM')
        except Exception as e:
            raise Exception("Couldn't connect to the LDAP server. Error message: " + str(e))

        self.log.debug("Connection established, will attempt to bind")
        try:
            if not self.connection.bind():
                self.log.error("Couldn't bind! Will raise an exception.")
                raise Exception(str(self.connection.result))
        except Exception as e:
            raise RuntimeError(f"Couldn't bind to the LDAP server. Error message: {e}")

        self.log.debug(f"Connected to the LDAP {self.ldap_fqdn} using bind user {self.bind_user}")

    def disconnect(self):
        self.connection.unbind()

    def _find_ldap_group_by_name_helper(self, connection, group_name, search_base):
        search_filter = self.ldap_filter_attribute + "=" + group_name

        self.log.debug(
            "Looking for group \"" + group_name + "\" in \"" + search_base + "\" using this filter: " + search_filter)

        try:
            object_class_definition = ObjectDef(self.group_object_class,
                                                connection)  # Search "group" object class entries
        except Exception as e:
            raise Exception("Failed to create AD objectClass filter: " + str(e))

        # Extend the entry with our custom attribute. Use case: We wish to return an AD user object with
        # the extensionAttribute8 attribute. Before returning the AD user object below, we need to extend the
        # AD user object now with extensionAttribute8, which will during the below search operation be
        # filled with the actual data from AD

        reader = Reader(connection, object_class_definition,
                        query=f"(&(objectClass={self.group_object_class})({search_filter}))",
                        base=search_base)

        try:
            reader.search(attributes=[
                "member"])  # The search results will only contain the attributes defined in the attributes list
        except LDAPInvalidDnError as e:
            raise RuntimeError("Could not find the group \"" + group_name + "\" in LDAP. Error message: " + str(e))

        return reader

    def _find_ldap_user_by_uid(self, connection, uid, search_base, attribute_name):
        search_filter = self.ldap_filter_attribute + "=" + uid

        self.log.debug(f"Looking for user {uid} in search base \"{search_base}\" using this filter: {search_filter}")

        try:
            user_object_class = ObjectDef('user', connection)  # Search "user" object class entries
        except Exception as e:
            raise Exception("Failed to create AD objectClass filter: " + str(e))

        # Extend the entry with our custom attribute. Use case: We wish to return an AD user object with
        # the extensionAttribute8 attribute. Before returning the AD user object below, we need to extend the
        # AD user object now with extensionAttribute8, which will during the below search operation be
        # filled with the actual data from AD
        user_object_class += attribute_name

        reader = Reader(connection, user_object_class, query='(&(objectClass=User)(' + search_filter + '))',
                        base=search_base)
        reader.search(attributes=["cn",
                                  attribute_name])  # The search results will only contain the attributes defined in the attributes list

        return reader

    def update_entry_by_username(self, username, attribute_name, new_attribute_value):
        search_results = None

        assert self.connection is not None

        user_found = False
        for search_base in self.search_bases:
            search_results = self._find_ldap_user_by_uid(self.connection, username, search_base, attribute_name)

            number_of_results = len(search_results)
            if number_of_results > 1:
                raise Exception("The LDAP query returned more than one user.")
            elif number_of_results == 1:
                user_found = True
                break
            self.log.info("Didn't find user " + username + " in " + search_base)

        if not user_found:
            raise Exception(
                "Error code: 'mq-to-ldap-01'. Message: Didn't find user " + username + " in AD. See https://confluence.nmbu.no/x/z4DPAg for more info")

        assert search_results is not None

        writer = Writer.from_cursor(search_results)
        ldap_user = writer[0]

        ldap_user_cn = str(ldap_user['cn'])
        if ldap_user_cn != username:
            raise Exception(
                "Something is very wrong. Tried to look up user " + username + " but got this user from AD: " + ldap_user_cn)

        cencored_attrubute_value = new_attribute_value[-3:]
        self.log.info(
            "Found user in AD: " + ldap_user_cn + ". Will now update the attribute " + attribute_name + " with value **********" + cencored_attrubute_value)

        ldap_user[attribute_name] = new_attribute_value

        writer.commit()
        self.log.info(
            "Successfully set the LDAP attribute " + attribute_name + " for user " + ldap_user_cn + " to value ************" + cencored_attrubute_value)

        return username, new_attribute_value, attribute_name

    def find_user_by_uid(self, attribute_name, username):
        assert self.connection is not None

        search_results = None
        user_found = False
        for search_base in self.search_bases:

            # TODO: Rename below method
            search_results = self._find_ldap_user_by_uid(self.connection, username, search_base, attribute_name)

            number_of_results = len(search_results)
            if number_of_results > 1:
                raise Exception("The LDAP query returned more than one user.")
            elif number_of_results == 1:
                user_found = True
                break
            self.log.info("Didn't find user " + username + " in " + search_base)

        if not user_found:
            raise Exception("Didn't find user " + username + " in AD.")

        ldap_user = search_results[0]
        ldap_user_dn = search_results[0].entry_dn
        self.log.info("Found user " + str(ldap_user_dn))

        return ldap_user

    def find_ldap_group_by_name(self, ad_group_name, groups_search_base):
        assert self.connection is not None


        groups_search_results = self._find_ldap_group_by_name_helper(connection=self.connection,
                                                                     group_name=ad_group_name,
                                                                     search_base=groups_search_base)

        number_of_groups = len(groups_search_results)
        if number_of_groups == 0:
            return None

        if number_of_groups > 1:
            self.log.debug("Groups found: " + str(groups_search_results))
            raise RuntimeError("Searching for group " + ad_group_name + " resulted in " + str(number_of_groups) +
                               " matches. Expected 1 match.")

        ldap_group = groups_search_results[0]
        actual_group_dn = groups_search_results[0].entry_dn
        self.log.info("Found group " + str(actual_group_dn))

        expected_group_dn = "cn=" + ad_group_name + "," + groups_search_base
        if actual_group_dn.lower() != expected_group_dn.lower():
            raise RuntimeError(
                "Something is very wrong. Tried to look up group " + ad_group_name + " but got this group from AD: " + actual_group_dn)

        return ldap_group

    def create_ldap_group(self, new_group_name):
        #assert self.connection is not None
        print("Før connection")

        my_server = '10.90.97.35'

        ldap_prod_brukernavn = 'nmbu\sa-fs-ldap'
        ldap_prod_passord =os.getenv("ldap_prod_password")

        s2 = Server(my_server, use_ssl=True, port=636)

        c2 = Connection(s2, ldap_prod_brukernavn, ldap_prod_passord, authentication=NTLM, auto_bind=True)

        group_name = new_group_name
        # ldap_group_name = "cn=" + group_name + ",ou=usergroups,dc=devmiljo,dc=no"
        ldap_group_name = "cn=" + group_name + ",ou=fs,ou=student-groups,dc=nmbu,dc=no"

        # new_group_dn = "cn=" + ldap_group_name + "," + "user"

        # self.log.info("Creating new LDAP group " + new_group_dn)

        object_class = "group"
        attr = {
            'sAMAccountName': group_name,
            'cn': group_name,
            'description': 'Auto generated group'
        }
        print("Etter atributter")
        c2.add(ldap_group_name, object_class, attr)



    def remove_user_from_group(self, ldap_user_object, ad_group) -> bool:
        connection = self.return_connections()

        try:
            extend.microsoft.removeMembersFromGroups.ad_remove_members_from_groups(connection=connection,
                                                                                   members_dn=[ldap_user_object],
                                                                                   groups_dn=[ad_group],
                                                                                   fix=False,
                                                                                   raise_error=True)
            return True
        except Exception as e:
            # self.log.error(f"Failed to remove {ldap_user_object} from {ad_group}. Error message: {e}")
            return False

    def add_user_to_group(self, ldap_user_object, ad_group) -> None:

        connection = self.return_connections()
        assert connection is not None

        ldap_group_dn = ad_group
        ldap_user_dn = ldap_user_object

        try:
            extend.microsoft.addMembersToGroups.ad_add_members_to_groups(connection=connection,
                                                                         members_dn=[ldap_user_dn],
                                                                         groups_dn=[ldap_group_dn],
                                                                         fix=True,
                                                                         #raise_error=True
                                                                        )
            # self.log.info(f"Successfully added user {ldap_user_dn} to group {ldap_group_dn}")
        except Exception as e:
            print("Finner ikke bruker i AD")
            # raise Exception("Finner ikke bruker i AD")
            # raise RuntimeError(f"Failed to add {ldap_user_dn} to group {ldap_group_dn}. Error message: {e}")

    def return_connections(self):

        my_server = '10.90.97.35'

        ldap_prod_brukernavn = 'nmbu\sa-fs-ldap'
        ldap_prod_passord = os.getenv('ldap_prod_password')

        a_sever = Server(my_server, use_ssl=True, port=636)

        a_connection = Connection(a_sever, ldap_prod_brukernavn, ldap_prod_passord, authentication=NTLM, auto_bind=True)

        return a_connection