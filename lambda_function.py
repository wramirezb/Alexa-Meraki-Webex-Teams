from __future__ import print_function
from datetime import datetime
from meraki import meraki
import meraki_info

# ---------- GLOBAL VARIABLES ----------
# These are the variables used in the script defined in the meraki_info.py file

API_KEY = meraki_info.api_key
LAB_ORG = meraki_info.lab_org
KIT_ORG = meraki_info.kit_org
KIT_NET = meraki_info.kit_net
KIT_SN = meraki_info.kit_sn
KIT_CITY = meraki_info.kit_city
TIMESTAMP = meraki_info.time_days * 24 * 60 * 60
CLIENT_NAME = meraki_info.client_name.lower()
# Group Policy to Block Streaming Video and Audio
GROUP_POLICY = meraki_info.group_policy
# Group Policy to Allow Internet Access and Streaming Video and Audio
GROUP_POLICY_2 = meraki_info.group_policy_2
# Group Plocy to BLock Internet Access on iPads
GROUP_POLICY_3 = meraki_info.group_policy_3
SM_ORG = meraki_info.sm_org
SM_NET = meraki_info.sm_net
SM_DEVICE = meraki_info.sm_device
SM_OLD = meraki_info.sm_old_profile
SM_NEW = meraki_info.sm_new_profile
MACS_ADDRESSES = meraki_info.mac_addresses

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.1',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Alexa Meraki skill. " \
                    "You can ask me to get network status, check license expiration, " \
                    "query device status, get client devices."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me a command, " \
                    "like asking why the Internet is slow."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def who_are_you(intent, session):
    session_attributes = {}
    reprompt_text = None

    speech_output = "I am the Cisco Meraki Cloud, for the Ramirez's Family. You can interact with me via voice commands"
    should_end_session = True

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def get_license_status(intent, session):
    session_attributes = {}
    reprompt_text = None

    licensing = meraki.getlicensestate(API_KEY, KIT_ORG)
    status = licensing['status']
    date = licensing['expirationDate'].strip(' UTC')
    days = (datetime.strptime(date, '%b %d, %Y') - datetime.today()).days

    speech_output = 'Your license is {0} and expires on {1}, which is {2} days from today.'.format(status, date, days)
    should_end_session = True

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def why_internet_slow(intent, session):
    session_attributes = {}
    reprompt_text = None

    clients = meraki.getclients(API_KEY, KIT_SN, timestamp=TIMESTAMP)
    usage = [client['usage']['sent'] + client['usage']['recv'] for client in clients]
    max_client = clients[usage.index(max(usage))]
    bw_use = round((max_client['usage']['sent'] + max_client['usage']['recv']) / 1024)

    traffic = meraki.getnetworktrafficstats(API_KEY, KIT_NET, timespan=TIMESTAMP)
    applications = [app['application'] for app in traffic]
    bws = [app['recv'] + app['sent'] for app in traffic]
    max_bw = max(bws)
    max_app = applications[bws.index(max_bw)]

    speech_output = 'That\'s because among the {0} clients connected, the top bandwidth hog is {1}. That device used {2} megabytes of data in the last {3}, {4} percent just on {5}.'.format(len(clients), max_client['description'], bw_use, ('hour' if TIMESTAMP == 3600 else str(round(TIMESTAMP / 60 / 60)) + ' hours'), round((max_bw / 1024) / bw_use * 100), max_app)
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# Block Streaming and Audio in iPads identified by mac addresses

def block_Streaming(intent, session):
    session_attributes = {}
    reprompt_text = None

    speech_output = 'The device '
    clients = meraki.getclients(API_KEY, KIT_SN)

    targets = []
# Identify clients by MAC addresses
    MACS_ADDRESSES = [address.lower() for address in meraki_info.mac_addresses]
    for client in clients:
        if client['mac'] in MACS_ADDRESSES:
            targets.append(client)

    group_policies = meraki.getgrouppolicies(API_KEY, KIT_NET)
    gp_names = [gp['name'].lower() for gp in group_policies]
    try:
        gp_num = group_policies[gp_names.index(GROUP_POLICY.lower())]['groupPolicyId']
    except:
        gp_num = 'blocked'
    for target in targets:
        if gp_num == 'blocked':
            meraki.updateclientpolicy(API_KEY, KIT_NET, target['mac'], 'blocked')
        else:
            meraki.updateclientpolicy(API_KEY, KIT_NET, target['mac'], 'group', gp_num)
        speech_output += target['description'] + ' '

    if gp_num == 'blocked':
        speech_output += ' now blocked on the network'
    else:
        speech_output += ' now applied with ' + GROUP_POLICY
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# Block Internet Access in All iPads

def block_ipad(intent, session):
    session_attributes = {}
    reprompt_text = None

    speech_output = 'The device '
    clients = meraki.getclients(API_KEY, KIT_SN)

    targets = []
# Identify clients by MAC addresses
    MACS_ADDRESSES = [address.lower() for address in meraki_info.mac_addresses]
    for client in clients:
        if client['mac'] in MACS_ADDRESSES:
            targets.append(client)

    group_policies = meraki.getgrouppolicies(API_KEY, KIT_NET)
    gp_names = [gp['name'].lower() for gp in group_policies]
    try:
        gp_num = group_policies[gp_names.index(GROUP_POLICY_3.lower())]['groupPolicyId']
    except:
        gp_num = 'blocked'
    for target in targets:
        if gp_num == 'blocked':
            meraki.updateclientpolicy(API_KEY, KIT_NET, target['mac'], 'blocked')
        else:
            meraki.updateclientpolicy(API_KEY, KIT_NET, target['mac'], 'group', gp_num)
        speech_output += target['description'] + ' '

    if gp_num == 'blocked':
        speech_output += ' now blocked on the network'
    else:
        speech_output += ' now applied with ' + GROUP_POLICY_3
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# Allow Internet Access back on blocked devices by changing them to Group Policy Normal

def allow_access(intent, session):
    session_attributes = {}
    reprompt_text = None

    speech_output = 'The device '
    clients = meraki.getclients(API_KEY, KIT_SN)

    targets = []
# Identify clients by MAC addresses
    MACS_ADDRESSES = [address.lower() for address in meraki_info.mac_addresses]
    for client in clients:
        if client['mac'] in MACS_ADDRESSES:
            targets.append(client)

    group_policies = meraki.getgrouppolicies(API_KEY, KIT_NET)
    gp_names = [gp['name'].lower() for gp in group_policies]
    try:
        # group_policy 102 is the group number for Group Policy Normal
        gp_num = '102'
    except:
        gp_num = 'blocked'
    for target in targets:
        meraki.updateclientpolicy(API_KEY, KIT_NET, target['mac'], 'group', gp_num)
        speech_output += target['description'] + ' '

    speech_output += ' now applied with ' + GROUP_POLICY_2
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# This function provides information about the netowrk status

def get_network_status(intent, session):
    session_attributes = {}
    reprompt_text = None

    network = meraki.getnetworkdetail(API_KEY, KIT_NET)
    devices = meraki.getnetworkdevices(API_KEY, KIT_NET)
    device_uplinks = [meraki.getdeviceuplink(API_KEY, KIT_NET, device['serial']) for device in devices]
    active = 0
    for uplinks in device_uplinks:
        for uplink in uplinks:
            if uplink['status'] == 'Active':
                active += 1
                break
    if len(devices) == 1:
        speech_output = 'The {0} network contains just a single device, and that device is currently {1} active and online.'.format(network['name'], ('not' if active == 0 else ''))
    else:
        speech_output = 'The {0} network contains a total of {1} devices, and {2} of them {3} currently active and online.'.format(network['name'], len(devices), active, ('is' if active == 1 else 'are'))
    should_end_session = True

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# This function provides information about the Device Status that has been identified in the meraki_info.py file

def get_device_status(intent, session):
    session_attributes = {}
    reprompt_text = None

    device = meraki.getdevicedetail(API_KEY, KIT_NET, KIT_SN)
    uplinks = meraki.getdeviceuplink(API_KEY, KIT_NET, KIT_SN)
    state = 'offline'
    for uplink in uplinks:
        if uplink['status'] == 'Active':
            state = 'online'
            break
    speech_output = 'The {0} device is a {1} located at {2}, and is currently {3}.'.format((device['name'] if device['name'] != '' else 'Meraki'), device['model'], (device['address'] if device['address'] != '' else 'somewhere on the interwebs'), state)
    should_end_session = True

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# This function list all clients connected to the network in the last hour

def get_client_devices(intent, session):
    session_attributes = {}
    reprompt_text = None

    clients = meraki.getclients(API_KEY, KIT_SN, timestamp=3600)
    usage = 0
    for client in clients:
        usage += client['usage']['sent'] + client['usage']['recv']
    if usage < 1024:
        speech_output = 'In the last hour there are a total of {0} client devices connected, with total network usage of {1} kilobytes.'.format(len(clients), round(usage))
    elif usage < 1024 * 1024:
        speech_output = 'In the last hour there are a total of {0} client devices connected, with total network usage of {1} megabytes.'.format(len(clients), round(usage/1024, 1))
    else:
        speech_output = 'In the last hour there are a total of {0} client devices connected, with total network usage of {1} gigabytes.'.format(len(clients), round(usage/1024/1024, 2))
    should_end_session = True

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()

# Here is where you map the intents defined in Amazon Echo to the functions in the code

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "WhoAreYou":
        return who_are_you(intent, session)
    elif intent_name == "GetLicenseStatus":
        return get_license_status(intent, session)
    elif intent_name == "WhyInternetSlow":
        return why_internet_slow(intent, session)
    elif intent_name == "BlockStreaming":
        return block_block_Streaming(intent, session)
    elif intent_name == "AllowAccess":
        return allow_access(intent, session)
    elif intent_name == "GetNetworkStatus":
        return get_network_status(intent, session)
    elif intent_name == "BlockiPad":
        return block_ipad(intent, session)    
    elif intent_name == "GetDeviceStatus":
        return get_device_status(intent, session)
    elif intent_name == "GetClientDevices":
        return get_client_devices(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
