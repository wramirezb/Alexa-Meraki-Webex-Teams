# Your Meraki admin login's corresponding API key
# Add yourself as a full org admin to the Demo API Lab org @
# https://n27.meraki.com/o/Z8Zbqb/manage/organization/admins
# "Become user" if needed to add yourself as an admin
# Ensure this key has access to both the Demo API Lab org as well as your kit org
api_key = 'XXXXXXXXXXXXXXX'

# Do NOT modify, this is the Alexa API Lab org ID for https://n27.meraki.com/o/Z8Zbqb/manage/organization/
### DO NOT MODIFY
lab_org = '694549'
### DO NOT MODIFY

# Your city, to be added onto the map for the provision.py script
kit_city = 'Coral Gables, FL'

# Your own lab kit org, for local client device demo
kit_org = 'XXX'

# Network ID within that org, where the Meraki device lives
kit_net = 'XXXXX'

# Serial number of a device in network, which your client device is connected
kit_sn = 'XXX-XXX-XXX'

# How far back in days (decimals OK, so fraction of a day if needed) should we search for your client device & usage?
# 0.5 for 12 hours, 0.25 for 6 hours, 0.125 for 3 hours, 0.0834 for 2 hours (minimum)
time_days = 0.5

# What name should we look for in client devices? (you'll have to rename clients in Dashboard manually)
# Make sure this matches in Dashboard exactly (must CONTAIN the following string)
client_name = 'XXXXXXXX'

# What group policy should we look for to assign to those client devices with client_name?
# Make sure this matches in Dashboard exactly (must EQUAL the following string)
group_policy = 'Block Video and Music'
group_policy_2 = 'Normal'
group_policy_3 = 'Blocked'

#List of MAC addresses to block by group policy
mac_addresses = ['XX:XX:XX:XX:XX:XX', 'XX:XX:XX:XX:XX:XX', 'XX:XX:XX:XX:XX:XX']

# Optional section: SM network, device name, and profile settings to remove then apply
# Certain profile settings such as wallpaper only work for DEP/supervised devices
sm_org = 'ORG_ID'
sm_net = 'NET_ID'

