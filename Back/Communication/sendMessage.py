# This file is to send a message with discord webhook
#

import requests
import json

def sendMessage(message):
    url = 'https://discord.com/api/webhooks/1265666843448709202/SJyr_8SfsZuKB0fm1w4u6AhwbExoXyFQP6znNLoR6EFbkBrQMH7eZn2FRk919_MUvxSE'
    data = {"content": message}
    headers = {"Content-Type": "application/json"}
    result = requests.post(url, data=json.dumps(data), headers=headers)
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        print(result.text)
    return result.status_code

if __name__ == "__main__":
    sendMessage("Hello World")
