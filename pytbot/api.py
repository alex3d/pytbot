import json
import requests
import logging
log = logging.getLogger(__name__)


class ApiBase:
    BASE_URL = 'https://api.telegram.org/bot'
    next_update_id = 0
    log = log.getChild('Api')

    def get_me(self):
        return self._req('getMe')

    def send_message(self, text, chat_id=None, disable_web_page_preview=None,
                     reply_to_message_id=None, reply_markup=None):
        return self._req('sendMessage',
                         text=text,
                         chat_id=chat_id,
                         disable_web_page_preview=disable_web_page_preview,
                         reply_to_message_id=reply_to_message_id,
                         reply_markup=reply_markup)

    def forward_message(self, from_chat_id, message_id, chat_id=None):
        return self._req('forwardMessage',
                         from_chat_id=from_chat_id,
                         message_id=message_id)

    def send_photo(self, photo, chat_id=None, caption=None,
                   reply_to_message_id=None, reply_markup=None):
        return self._req('sendPhoto', {'photo': photo},
                         chat_id=chat_id,
                         caption=caption,
                         reply_to_message_id=reply_to_message_id,
                         reply_markup=reply_markup)

    def send_audio(self, audio, chat_id=None, duration=None,
                   reply_to_message_id=None, reply_markup=None):
        return self._req('sendAudio', {'audio': audio},
                         chat_id=chat_id,
                         duration=duration,
                         reply_to_message_id=reply_to_message_id,
                         reply_markup=reply_markup)

    def send_document(self, document, chat_id=None,
                      reply_to_message_id=None, reply_markup=None):
        return self._req('sendDocument', {'document': document},
                         chat_id=chat_id,
                         reply_to_message_id=reply_to_message_id,
                         reply_markup=reply_markup)

    def send_sticker(self, sticker, chat_id=None,
                     reply_to_message_id=None, reply_markup=None):
        return self._req('sendSticker', {'sticker': sticker},
                         chat_id=chat_id,
                         reply_to_message_id=reply_to_message_id,
                         reply_markup=reply_markup)

    def send_video(self, video, chat_id=None, duration=None,
                   reply_to_message_id=None, reply_markup=None):
        return self._req('sendVideo', {'video': video},
                         chat_id=chat_id,
                         duration=duration,
                         reply_to_message_id=reply_to_message_id,
                         reply_markup=reply_markup)

    def send_location(self, latitude, longitude, chat_id=None,
                      reply_to_message_id=None, reply_markup=None):
        return self._req('sendLocation',
                         latitude=latitude,
                         longitude=longitude,
                         chat_id=chat_id,
                         reply_to_message_id=reply_to_message_id,
                         reply_markup=reply_markup)

    def send_chat_action(self, action, chat_id=None):
        return self._req('sendChatAction', chat_id=chat_id, action=action)

    def get_updates(self, offset=None, limit=None, timeout=300):
        if offset is None:
            offset = self.next_update_id
        updates = self._req('getUpdates', offset=offset, limit=limit,
                            timeout=timeout)
        if updates:
            self.next_update_id = updates[-1]['update_id'] + 1
        return updates


class ChatApi(ApiBase):
    def __init__(self, api, chat_id):
        self.api = api
        self.chat_id = chat_id

    def _req(self, method, files=None, **data):
        if data.get('chat_id', False) is None:
            data['chat_id'] = self.chat_id
        return self.api._req(method, files, **data)


class Api(ApiBase):
    def __init__(self, api_token):
        self.session = requests.Session()
        self.api_token = api_token

    def _req(self, method, files=None, **data):
        if files:
            for k,v in files.items():
                if not hasattr(v,'read'):
                    del files[k]
                    data[k] = v
        r = self.session.post(self.BASE_URL+self.api_token+'/'+method,
                              data=data, files=files)
        res = r.text
        try:
            res = json.loads(res)
        except Exception:
            raise Exception("method call failed(can't parse): %s" % res)

        if res.get('ok', False) is not True:
            raise Exception("method call failed %s" % res)
        return res['result']


def reply_keyboard_markup(keyboard, one_time_keyboard=False,
                          resize_keyboard=False):
    return json.dumps({
                      'keyboard': keyboard,
                      'one_time_keyboard': one_time_keyboard,
                      'resize_keyboard': resize_keyboard,
                      })


def reply_keyboard_hide(selective=False):
    return json.dumps({
                      'hide_keyboard': True,
                      'selective': selective,
                      })


def force_reply(selective=False):
    return json.dumps({
                      'force_reply': True,
                      'selective': selective,
                      })
