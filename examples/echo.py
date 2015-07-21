#!/usr/bin/python
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/..'))
os.chdir(os.path.dirname(__file__))

import pytbot


class EchoBot(pytbot.Bot):
    @pytbot.command()
    def echo(self, msg):
        '''echo command'''
        self.api.send_message(msg["text"])

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(name)s %(message)s')

    try:
        token = open('api_token.txt', 'r').read().strip()
    except:
        print("Please save your api token to examples/api_token.txt")
        sys.exit(1)

    api = pytbot.Api(token)
    pytbot.run(api, EchoBot)
