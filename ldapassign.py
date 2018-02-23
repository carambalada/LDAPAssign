#!/usr/bin/env python

import config
import ldap

def g_match(user, groups):
 group_list = []
 for group in groups:
  for pattern in group['patterns']:
   if user.startswith(str(pattern)):
    group_list.append(group['name'])
    break
 return group_list

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# LDAP connection
#
def ldap_connection(hostname, username, password):
 url = "ldap://" + hostname
 ldap_connection = ldap.initialize(url)

 try:
  ldap_connection.protocol_version = ldap.VERSION3
  ldap_connection.simple_bind_s(username, password)
  return_value = ldap_connection

 except ldap.LDAPError, e:
  if type(e.message) == dict and e.message.has_key('desc'):
   emsg = e.message['desc']
  else:
   emsg = e
  print('LDAP connection failure: ' + str(emsg))
  exit(1)

 return return_value

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Main
#

# for user in config.users:
#  g = g_match(user,config.groups)
#  print('User ' + str(user) + ' should be at groups ' + str(g))

bind = ldap_connection(
 config.ldap_settings['hostname'],
 config.ldap_settings['user_dn'],
 config.ldap_settings['password']
 )
