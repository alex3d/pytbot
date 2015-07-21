#!/usr/bin/python
import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)+'/..'))
os.chdir(os.path.dirname(__file__))

import pytbot


class AdvancedBot(pytbot.Bot):
    @pytbot.command()
    def join(self, msg):
        """wizard example"""
        keyboard = pytbot.reply_keyboard_markup([['Hello, ', 'world!']],
                                                one_time_keyboard=True,
                                                resize_keyboard=True)
        self.api.send_message('Enter first string:', reply_markup=keyboard)
        first = (yield True)['text']
        self.api.send_message('Enter second string:', reply_markup=keyboard)
        second = (yield True)['text']
        self.api.send_message(first+second,
                              reply_markup=pytbot.reply_keyboard_hide())

    @pytbot.command()
    def text(self, msg):
        '''echo command'''
        self.api.send_message(msg["text"])

    @pytbot.command()
    def photo(self, msg):
        '''dog photo'''
        self.api.send_photo(open('files/dog.jpg', 'r'), caption="dog photo")

    @pytbot.command()
    def sticker(self, msg):
        '''send sticker'''
        self.api.send_sticker('BQADAgADHAADyIsGAAFZfq1bphjqlgI')
        self.api.send_sticker(open('files/dog.png', 'r'))

    @pytbot.command()
    def document(self, msg):
        '''dog document'''
        self.api.send_document(open('files/dog.jpg', 'r'))

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s %(name)s %(message)s')

    try:
        token = open('api_token.txt', 'r').read().strip()
    except:
        print("Please save your api token to examples/api_token.txt")
        sys.exit(1)

    api = pytbot.Api(token)
    pytbot.run(api, AdvancedBot)
