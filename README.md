# Easy to use python telegram bot api

## Echo bot example
```python
import pytbot

class EchoBot(pytbot.Bot):
    @pytbot.command()
    def echo(self, msg):
        self.api.send_message(msg["text"])

api = pytbot.Api("%API_TOKEN%")
pytbot.run(api, EchoBot)
```
[Examples](examples)

## Features
 - Wizard bots ("yield")

 ```python
    @pytbot.command()
    def join(self, msg):
        self.api.send_message('Enter first string:')
        first = (yield True)['text']
        self.api.send_message('Enter second string:')
        second = (yield True)['text']
        self.api.send_message(first+second)
```
 - Automatic "help" command generation
 - Connection pool / keepalive
