# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path
import sys
import json
from Config import config
try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = config.CLIENT_ACCESS_TOKEN


def sendTelegramMessage(chatid,TelegramMessage):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    request.session_id=chatid

    request.query = TelegramMessage
    response = request.getresponse()

    string = response.read().decode('utf-8')
    json_obj = json.loads(string)
    if json_obj is not None:
        result = json_obj.get("result")
        if 'fulfillment' in result:
            message=result.get("fulfillment")
            text = message.get("speech")
            if text is None:
                text=message.get("messages")[0].get("speech")

            return text
    return "Errore"

