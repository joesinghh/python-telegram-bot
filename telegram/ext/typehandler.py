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
"""This module contains the TypeHandler class."""

from typing import Callable, Type, TypeVar, Union
from telegram.utils.defaultvalue import DefaultValue, DEFAULT_FALSE

from .handler import Handler
from .utils.types import CCT

RT = TypeVar('RT')
UT = TypeVar('UT')


class TypeHandler(Handler[UT, CCT]):
    """Handler class to handle updates of custom types.

    Warning:
        When setting ``run_async`` to :obj:`True`, you cannot rely on adding custom
        attributes to :class:`telegram.ext.CallbackContext`. See its docs for more info.

    Args:
        type (:obj:`type`): The ``type`` of updates this handler should process, as
            determined by ``isinstance``
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature: ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        strict (:obj:`bool`, optional): Use ``type`` instead of ``isinstance``.
            Default is :obj:`False`
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.
            Defaults to :obj:`False`.

    Attributes:
        type (:obj:`type`): The ``type`` of updates this handler should process.
        callback (:obj:`callable`): The callback function for this handler.
        strict (:obj:`bool`): Use ``type`` instead of ``isinstance``. Default is :obj:`False`.
        run_async (:obj:`bool`): Determines whether the callback will run asynchronously.

    """

    __slots__ = ('type', 'strict')

    def __init__(
        self,
        type: Type[UT],  # pylint: disable=W0622
        callback: Callable[[UT, CCT], RT],
        strict: bool = False,
        run_async: Union[bool, DefaultValue] = DEFAULT_FALSE,
    ):
        super().__init__(
            callback,
            run_async=run_async,
        )
        self.type = type  # pylint: disable=E0237
        self.strict = strict  # pylint: disable=E0237

    def check_update(self, update: object) -> bool:
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:obj:`object`): Incoming update.

        Returns:
            :obj:`bool`

        """
        if not self.strict:
            return isinstance(update, self.type)
        return type(update) is self.type  # pylint: disable=C0123
