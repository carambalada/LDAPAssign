#!/usr/bin/env python

# TODO:
# - create groups if they don't exist

import ldap
import config

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# LDAP: Binding
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
# LDAP: Getting list of users
#
def get_users(b, settings):
 users = []
 result_id = b.search(
  settings['base'],
  settings['scope'],
  settings['filter'],
  settings['attributes'],
  settings['attrsonly']
  )
 
 result_type, result_data = b.result(result_id, 1)
 #print(str(result_type))
 #print(str(result_data))
 if result_data != []:
  for entry in result_data:
   users.append(
    { 'dn': entry[0],
      'uid': entry[1]['uid'][0]
    }
   )
  return users
 else:
  print('No configured users found in LDAP - imposible to continue')
  exit(1)
 

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting matching groups
#
def get_matching_groups(user, groups):
 groups_match = []
 for group in groups:
  for pattern in group['patterns']:
   if user['uid'].startswith(pattern):
    groups_match.append(group)
    break
 return groups_match

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# LDAP: Making a list of groups from the config plus:
#        - memberUid
#        - number of members
#
def get_groups(bind, config_groups, settings):
 #
 # making a filter like '(&(objectClass=posixGroup)(cn=Group1))
 # TODO: check that at least one group is valid for forming the filter
 #
 groups = []
 for group in config_groups:
  search_filter = '(&' + settings['filter'] + '(cn=' + group['name'] + '))'
  result_id = bind.search(
   settings['base'],
   settings['scope'],
   search_filter,
   settings['attributes'],
   settings['attrsonly']
   )
  result_type, result_data = bind.result(result_id, 1)
  if result_data != []:
   if result_data[0][1] != {}:
    group['memberUid'] = result_data[0][1]['memberUid']
    group['current'] = len(group['memberUid'])
   else:
    group['memberUid'] = []
    group['current'] = 0
   groups.append(group)
  else:
   print('Group ' + group['name'] + ' was not found in LDAP - skipping')

 if groups != []:
  return groups
 else:
  print('No configured groups found in LDAP - imposible to continue')
  exit(1)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting users that are not found in groups
#
def get_unassigned_users(users, groups):
 #
 # is it okay to use the same variable for looping and removig operation at
 # the same time?
 #
 unassigned_users = users
 for user in users:
  for group in groups:
   if group['memberUid'].count(user['uid']) > 0:
    #print('User ' + user['uid'] + ' found in group ' + group['name'])
    unassigned_users.remove(user)
    break
 return unassigned_users

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Getting groups that are still unfilled
#
def get_unfilled_groups(groups):
 unfilled_groups = groups
 for group in groups:
  if group['current'] >= group['limit']:
   unfilled_groups.remove(group)
 return unfilled_groups

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Arranging user to groups
#
def arrange(users, groups):
 failed_users = []
 for user in users:
  groups_match = get_matching_groups(user, groups)
  if groups_match != []:
   print('Adding user ' + user['uid'] + ' to the first unfilled group ' \
          + groups[0]['name'])
   groups[0]['current'] += 1
   groups = get_unfilled_groups(groups)
  else:
   failed_users.append(user)
 return failed_users

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# Main
#

bind = ldap_connection(
 config.ldap['connection']['hostname'],
 config.ldap['connection']['user_dn'],
 config.ldap['connection']['password']
 )

users = get_users(bind, config.ldap['users'])
groups = get_groups(bind, config.groups, config.ldap['groups'])
users = get_unassigned_users(users, groups)
groups = get_unfilled_groups(groups)
users = arrange(users, groups)
print(groups)
if users != []:
 print('Groupping some users were failed due to groups\' limitation or\
 pattern dismatch. Here are some hints:')
 for user in users:
  print('\nUser ' + user['uid'] + ':')
  groups_match = get_matching_groups(user, config.groups)
  if groups_match == []:
   print(' - no matching groups found')
  else:
   for group in groups_match:
    print(' - matching with group ' + group['name'] + ' (limit: ' + \
           str(group['limit']) + ', users: ' + str(group['current']) + ')')
