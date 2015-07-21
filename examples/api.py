#!/usr/bin/python
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/..'))
os.chdir(os.path.dirname(__file__))

import pytbot.api
import json

try:
    token = open('api_token.txt', 'r').read().strip()
except:
    print("Please save your api token to examples/api_token.txt")
    sys.exit(1)

api = pytbot.api.Api(token)

if len(sys.argv) < 2:
    print("Usage:\n"
          "./api.py get_updates\n"
          "./api.py send_message chat_id message")
    sys.exit(0)

cmd = sys.argv[1]

if cmd == "send_message":
    chat_id = int(sys.argv[2])
    text = sys.argv[3]
    api.send_message(text, chat_id)
elif cmd == "get_updates":
    while True:
        for update in api.get_updates():
            msg = update['message']
            print(json.dumps(msg))
