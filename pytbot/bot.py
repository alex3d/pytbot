import inspect
import threading
import types
import re
import functools
from . import api
import sys
if sys.version_info > (3,):
    from queue import Queue
else:
    from Queue import Queue
import logging
log = logging.getLogger(__name__)


class Matcher(object):
    def __call__(self, msg):
        pass


class RegexMatcher(Matcher):
    def __init__(self, regex):
        self.regex = regex
        self.regex1 = re.compile(regex)

    def __call__(self, msg):
        return 'text' in msg and self.regex1.match(msg['text'])


def command(cmd=None, regex=None):
    def dec(func):
        cmd1 = cmd or func.__name__
        if regex:
            cmd1 = RegexMatcher(regex)
        else:
            cmd1 = RegexMatcher('/'+cmd1+'(?: |@|$)')
        func.bot_matcher = cmd1
        return func
    return dec


def run(api, bot_class, middlewares=None):
    if middlewares is None:
        middlewares = [
            PerChat,
            Threaded,
            BotStack,
            HelpGenerator
        ]
    b = bot_class
    for mw in reversed(middlewares):
        b = functools.partial(mw, child_class=b)
    bot = b(api)

    while True:
        try:
            for u in api.get_updates():
                bot(u['message'])
        except Exception:
            log.exception('Exception')


class Bot(object):
    def __init__(self, api):
        self.api = api

        if not hasattr(self.__class__, 'commands'):
            commands = []
            for name, func in inspect.getmembers(self.__class__,
                                                 predicate=inspect.isroutine):
                if getattr(func, 'bot_matcher', None) is not None:
                    commands.append(func)
            self.__class__.commands = commands

    def __call__(self, message):
        for func in self.commands:
            match = getattr(func, 'bot_matcher')(message)
            if match:
                ret = func(self, message, *match.groups())
                if isinstance(ret, types.GeneratorType):
                    ret1 = next(ret, None)
                    if ret1:
                        return ret
                return ret
        else:
            return False
        return True


class Middleware(object):
    def __call__(self, msg):
        pass

    @property
    def commands(self):
        return self.child.commands


class PerChat(Middleware):
    def __init__(self, api, child_class):
        self.api = api
        self.child_class = child_class
        self.bots = {}

    def __call__(self, message):
        chat_id = message['chat']['id']
        bot = self.bots.get(chat_id, None)
        if bot is None:
            bot = self.child_class(api.ChatApi(self.api, chat_id))
            self.bots[chat_id] = bot
        return bot(message)


class Auth(Middleware):
    def __init__(self, api, child_class, users):
        self.api = api
        self.child = child_class(api)
        self.users = users

    def __call__(self, message):
        from_id = message['from']['id']
        if from_id not in self.users:
            self.api.send_message('You are not authorized!')
            return
        return self.child(message)


class Threaded(Middleware):
    def __init__(self, api, child_class):
        self.api = api
        self.child = child_class(api)
        self.queue = Queue()
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def __call__(self, msg):
        self.queue.put(msg)

    def run(self):
        while True:
            msg = self.queue.get()
            try:
                self.child(msg)
            except Exception:
                log.exception("Can't handle message")


class HelpGenerator(Middleware):
    def __init__(self, api, child_class):
        self.api = api
        self.child = child_class(api)

    def __call__(self, msg):
        ret = self.child(msg)
        if ret:
            return ret

        if 'text' in msg and msg['text'] == '/help':
            txt = []
            for func in self.commands:
                m = re.match(r"/([-a-zA-Z_0-9]*)"+re.escape("(?: |@|$)")+"$",
                             func.bot_matcher.regex)
                if m:
                    txt.append('%s - %s' % (m.group(1), func.__doc__))
            self.api.send_message('Help:\n%s' % ('\n'.join(txt)))
            return True


class BotStack(Middleware):
    def __init__(self, api, child_class):
        self.api = api
        self.stack = [child_class(api)]

    def __call__(self, message):
        result = None
        while not result:
            if not self.stack:
                return None
            try:
                result = self.stack[-1](message)
            except StopIteration:
                self.stack.pop()
                continue
            if isinstance(result, types.GeneratorType):
                self.stack.append(result.send)
            return result
