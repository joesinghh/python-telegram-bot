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
"""This module contains the InlineQueryHandler class."""
import re
from typing import (
    TYPE_CHECKING,
    Callable,
    Match,
    Optional,
    Pattern,
    TypeVar,
    Union,
    cast,
    List,
)

from telegram import Update
from telegram.utils.defaultvalue import DefaultValue, DEFAULT_FALSE

from .handler import Handler
from .utils.types import CCT

if TYPE_CHECKING:
    from telegram.ext import Dispatcher

RT = TypeVar('RT')


class InlineQueryHandler(Handler[Update, CCT]):
    """
    Handler class to handle Telegram inline queries. Optionally based on a regex. Read the
    documentation of the ``re`` module for more information.

    Warning:
        * When setting ``run_async`` to :obj:`True`, you cannot rely on adding custom
          attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.
        * :attr:`telegram.InlineQuery.chat_type` will not be set for inline queries from secret
          chats and may not be set for inline queries coming from third-party clients. These
          updates won't be handled, if :attr:`chat_types` is passed.

    Args:
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature: ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        pattern (:obj:`str` | :obj:`Pattern`, optional): Regex pattern. If not :obj:`None`,
            ``re.match`` is used on :attr:`telegram.InlineQuery.query` to determine if an update
            should be handled by this handler.
        chat_types (List[:obj:`str`], optional): List of allowed chat types. If passed, will only
            handle inline queries with the appropriate :attr:`telegram.InlineQuery.chat_type`.

            .. versionadded:: 13.5
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
            Defaults to :obj:`False`.

    Attributes:
        callback (:obj:`callable`): The callback function for this handler.
        pattern (:obj:`str` | :obj:`Pattern`): Optional. Regex pattern to test
            :attr:`telegram.InlineQuery.query` against.
        chat_types (List[:obj:`str`], optional): List of allowed chat types.

            .. versionadded:: 13.5
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.

    """

    __slots__ = ('pattern', 'chat_types')

    def __init__(
        self,
        callback: Callable[[Update, CCT], RT],
        pattern: Union[str, Pattern] = None,
        run_async: Union[bool, DefaultValue] = DEFAULT_FALSE,
        chat_types: List[str] = None,
    ):
        super().__init__(
            callback,
            run_async=run_async,
        )

        if isinstance(pattern, str):
            pattern = re.compile(pattern)

        self.pattern = pattern
        self.chat_types = chat_types

    def check_update(self, update: object) -> Optional[Union[bool, Match]]:
        """
        Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:class:`telegram.Update` | :obj:`object`): Incoming update.

        Returns:
            :obj:`bool`

        """
        if isinstance(update, Update) and update.inline_query:
            if (self.chat_types is not None) and (
                update.inline_query.chat_type not in self.chat_types
            ):
                return False
            if self.pattern:
                if update.inline_query.query:
                    match = re.match(self.pattern, update.inline_query.query)
                    if match:
                        return match
            else:
                return True
        return None

    def collect_additional_context(
        self,
        context: CCT,
        update: Update,
        dispatcher: 'Dispatcher',
        check_result: Optional[Union[bool, Match]],
    ) -> None:
        """Add the result of ``re.match(pattern, update.inline_query.query)`` to
        :attr:`CallbackContext.matches` as list with one element.
        """
        if self.pattern:
            check_result = cast(Match, check_result)
            context.matches = [check_result]
