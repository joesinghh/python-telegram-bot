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
"""This module contains the StringCommandHandler class."""

from typing import TYPE_CHECKING, Callable, List, Optional, TypeVar, Union

from telegram.utils.defaultvalue import DefaultValue, DEFAULT_FALSE

from .handler import Handler
from .utils.types import CCT

if TYPE_CHECKING:
    from telegram.ext import Dispatcher

RT = TypeVar('RT')


class StringCommandHandler(Handler[str, CCT]):
    """Handler class to handle string commands. Commands are string updates that start with ``/``.
    The handler will add a ``list`` to the
    :class:`CallbackContext` named :attr:`CallbackContext.args`. It will contain a list of strings,
    which is the text following the command split on single whitespace characters.

    Note:
        This handler is not used to handle Telegram :attr:`telegram.Update`, but strings manually
        put in the queue. For example to send messages with the bot using command line or API.

    Warning:
        When setting ``run_async`` to :obj:`True`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.

    Args:
        command (:obj:`str`): The command this handler should listen for.
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature: ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
            Defaults to :obj:`False`.

    Attributes:
        command (:obj:`str`): The command this handler should listen for.
        callback (:obj:`callable`): The callback function for this handler.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.

    """

    __slots__ = ('command',)

    def __init__(
        self,
        command: str,
        callback: Callable[[str, CCT], RT],
        run_async: Union[bool, DefaultValue] = DEFAULT_FALSE,
    ):
        super().__init__(
            callback,
            run_async=run_async,
        )
        self.command = command

    def check_update(self, update: object) -> Optional[List[str]]:
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:obj:`object`): The incoming update.

        Returns:
            :obj:`bool`

        """
        if isinstance(update, str) and update.startswith('/'):
            args = update[1:].split(' ')
            if args[0] == self.command:
                return args[1:]
        return None

    def collect_additional_context(
        self,
        context: CCT,
        update: str,
        dispatcher: 'Dispatcher',
        check_result: Optional[List[str]],
    ) -> None:
        """Add text after the command to :attr:`CallbackContext.args` as list, split on single
        whitespaces.
        """
        context.args = check_result
