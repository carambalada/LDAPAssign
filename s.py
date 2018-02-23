#!/usr/bin/env python

import config as cfg

#print(cfg.groups[0]["patterns"][0])

def g_match(user, groups):
 group_list = []
 for group in groups:
  for pattern in group['patterns']:
   if user.startswith(str(pattern)):
    group_list.append(group['name'])
    break
 return group_list

for user in cfg.users:
 g = g_match(user,cfg.groups)
 print('User ' + str(user) + ' should be at groups ' + str(g))
