#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2021
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
from queue import Queue

import pytest

from telegram import (
    Bot,
    Update,
    Message,
    User,
    Chat,
    CallbackQuery,
    InlineQuery,
    ChosenInlineResult,
    ShippingQuery,
    PreCheckoutQuery,
)
from telegram.ext import StringRegexHandler, CallbackContext, JobQueue

message = Message(1, None, Chat(1, ''), from_user=User(1, '', False), text='Text')

params = [
    {'message': message},
    {'edited_message': message},
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat', message=message)},
    {'channel_post': message},
    {'edited_channel_post': message},
    {'inline_query': InlineQuery(1, User(1, '', False), '', '')},
    {'chosen_inline_result': ChosenInlineResult('id', User(1, '', False), '')},
    {'shipping_query': ShippingQuery('id', User(1, '', False), '', None)},
    {'pre_checkout_query': PreCheckoutQuery('id', User(1, '', False), '', 0, '')},
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat')},
]

ids = (
    'message',
    'edited_message',
    'callback_query',
    'channel_post',
    'edited_channel_post',
    'inline_query',
    'chosen_inline_result',
    'shipping_query',
    'pre_checkout_query',
    'callback_query_without_message',
)


@pytest.fixture(scope='class', params=params, ids=ids)
def false_update(request):
    return Update(update_id=1, **request.param)


class TestStringRegexHandler:
    test_flag = False

    def test_slot_behaviour(self, mro_slots):
        inst = StringRegexHandler('pfft', self.callback_context)
        for attr in inst.__slots__:
            assert getattr(inst, attr, 'err') != 'err', f"got extra slot '{attr}'"
        assert len(mro_slots(inst)) == len(set(mro_slots(inst))), "duplicate slot"

    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = False

    def callback_context(self, update, context):
        self.test_flag = (
            isinstance(context, CallbackContext)
            and isinstance(context.bot, Bot)
            and isinstance(update, str)
            and isinstance(context.update_queue, Queue)
            and isinstance(context.job_queue, JobQueue)
        )

    def callback_context_pattern(self, update, context):
        if context.matches[0].groups():
            self.test_flag = context.matches[0].groups() == ('t', ' message')
        if context.matches[0].groupdict():
            self.test_flag = context.matches[0].groupdict() == {'begin': 't', 'end': ' message'}

    def test_basic(self, dp):
        handler = StringRegexHandler('(?P<begin>.*)est(?P<end>.*)', self.callback_context)
        dp.add_handler(handler)

        assert handler.check_update('test message')
        dp.process_update('test message')
        assert self.test_flag

        assert not handler.check_update('does not match')

    def test_other_update_types(self, false_update):
        handler = StringRegexHandler('test', self.callback_context)
        assert not handler.check_update(false_update)

    def test_context(self, dp):
        handler = StringRegexHandler(r'(t)est(.*)', self.callback_context)
        dp.add_handler(handler)

        dp.process_update('test message')
        assert self.test_flag

    def test_context_pattern(self, dp):
        handler = StringRegexHandler(r'(t)est(.*)', self.callback_context_pattern)
        dp.add_handler(handler)

        dp.process_update('test message')
        assert self.test_flag

        dp.remove_handler(handler)
        handler = StringRegexHandler(r'(t)est(.*)', self.callback_context_pattern)
        dp.add_handler(handler)

        dp.process_update('test message')
        assert self.test_flag
