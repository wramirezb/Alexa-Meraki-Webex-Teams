# **Meraki Dashboard Integration with Amazon Alexa**

## **Description**

The goal of this project if to highlight the automation and integration capabilities of Cisco product portfolio via its APIs. In this scenario we are integration Meraki Dashboard with Amazon Alexa and Webex Teams via common set of APIs. By leveraging Amazon Alexa’s Natural Language Processing capabilities, we are enabling end users/ the business to perform network configuration changes, gather network status information expressing desired outcome (intent) rather than a network command. In specific, in this project, users can obtain network status, change clients group policies to block and allow access to Internet/ Streaming Video services such as Netflix and YouTube, via Amazon Alexa. In addition, we are also exposing Webex Teams APIs, to post Meraki Dashboards alerts on a Webex Teams room via a Webhook, leveraging Built.io.

## **Integration Workflows**

User speech -- Amazon Alexa -- AWS Lambda Function (Python Script) -- Meraki Dashboard APIs

Meraki Dashboard -- Built.io/ Webhook (JSON format) -- Built.io/ Post Message on Webex Teams (via APIs)

## **Resources**

- alexa developer console -- https://developer.amazon.com
- AWS Lambda Service -- https://console.aws.amazon.com/lambda
- AWS CloudWatch Service --https://console.aws.amazon.com/cloudwatch
- Meraki Dashboard API -- https://create.meraki.io/
- Built.io -- https://www.built.io/
- JSON Formatter -- https://jsonformatter.org/#

## **Installation**

Follow instructions from Shiyue Cheng’s post on https://create.meraki.io/build/meraki-dashboard-with-alexa/

Additional Comments:

When creating your custom skill on your alexa developer console make sure to match the skills’ name with the names you have given them on the lambda_function.py file. Make sure to enter as many utterances as needed to invoke your skill. These are your intents/ desired outcomes. For example, for the BlockIpad intent, we are entering the utterances: block internet on iPads, block all iPads, no more iPads

When updating your lamda_function.py and meraki_info.py files, make sure to:

lambda_function.py: 1.- Create new functions (Block Streaming, Block iPads, Allow Access) 2.- Update intent function to align with your alexa custom skills intents 3.- Add code to execute intent on multiple devices simultaneously (mac addresses) 4.- Cleanup code, remove unwanted functions

meraki_info.py 
1. Define Global Variables 
2. Note from the original post there are new variables introduced
- group_policy = 'Block Video and Music'
- group_policy_2 = 'Normal'
- group_policy_3 = 'Blocked'
- mac_addresses = [‘XX:XX:XX:XX:XX:XX', ‘XX:XX:XX:XX:XX:XX', ‘XX:XX:XX:XX:XX:XX']

You will be using AWS Lambda service to run Python code as a service and CloudWatch service for log streams. To access ClouldWatch, click on services on your AWS console and search for CloudWatch

To create Webhook, search for webhook on Meraki.io and follow instructions. (i.e. https://create.meraki.io/guides/webhooks/)

Log into Built.io and create a new workflow, make sure to use webhook as trigger and Webex Teams Post New Message as action. It is also good to add a logger to your workflow in case you needed.

When configuring Webhook in Built.io, make sure to select payload and enter a sample of your webhook payload in a valid JSON format. This will help you format your Webex Teams message post. To format the payload, I used https://jsonformatter.org/#

## **Usage**

On your Amazon Alex device, mobile app or alexa developer console test say: “Ask Meraki” to invoke the skill follow by the intent, i.e. “block iPads”

Here are all the intents defined in this project

- **WhoAreYou** – replies with predefined message
- **GetLicenseStatus** – replies with license expiration info
- **GetNetworkStatus** – provides status of the network
- **GetDeviceStatus** – provides status of predefined device (i.e. Switch, AP, MX etc.)
- **GetClientDevices** – provides list of connected clients to predefined device in the last hour and combined usage
- **WhyInternetSlow** – look into all clients connected to a predefined device and list top bandwidth hog
- **BlockiPad** – block Internet access to ipads (identified by mac address), by changing their group policy to “Blocked”
- **BlockStreaming** – block streaming video and audio services by predefined client name and/or mac address, by changing their group policy to “Block Video and Music”
- **AllowAccess** – allow internet access to predefined client identified by client name and or mac address, by changing their group policy to “Normal”

Any configuration setting change (i.e. BlockiPad, BlockStreaming, AllowAccess) triggers an Alert that it is posted as a message on a Webex Team room.

## **Files**

- Lambda_function.py
- Meraki_info.py

## **Disclaimer**

This code is based out of Shiyue Cheng’s post (https://create.meraki.io/build/meraki-dashboard-with-alexa/). Special thanks to Shiyue Cheng (Meraki Solutions Architect), Santiago Flores (Americas SP SE), and Gerardo Chaves (GVE VSE) for all the coaching and guidance.
