# LDAPAssign
LDAP. Placing accounts to groups based on a given text configuration

Configuration example:

### config.py ###
groups = [
 { 'name': 'Group1',
   'patterns':
    [ 'user11',
      'user12',
      'user13',
    ]
 },
 { 'name': 'Group2',
   'patterns':
    [ 'user21',
      'user22',
    ]
 },
 { 'name': 'Users',
   'patterns':
    [ 'user',
    ]
 },
]

users = [
 'user11-usr',
 'user21-usr',
 'userXX-usr',
]
###
