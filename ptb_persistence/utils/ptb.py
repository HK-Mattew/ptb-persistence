from telegram import Update
from telegram.ext import (
    ExtBot,
    Application,
    ConversationHandler,
    ApplicationHandlerStop
    )
from telegram.ext._application import (
    _logger
)
from telegram._utils.defaultvalue import (
    DEFAULT_TRUE
)
from typing import Coroutine

from .. import PTBPersistence



async def _refresh_conversation_data(
        update: Update,
        application: Application,
        handler: ConversationHandler
        ) -> None:
    
    if (
        not isinstance(update, Update) or
        not isinstance(application, Application) or
        not isinstance(handler, ConversationHandler) or
        not isinstance(application.persistence, PTBPersistence) or
        not handler.persistent
        ):
        return None
    
    # Ignore messages in channels
    if update.channel_post or update.edited_channel_post:
        return None
    if handler.per_chat and not update.effective_chat:
        return None
    if handler.per_user and not update.effective_user:
        return None
    if handler.per_message and not update.callback_query:
        return None
    if update.callback_query and handler.per_chat and not update.callback_query.message:
        return None
    

    key = handler._get_key(update)

    persistence: PTBPersistence = application.persistence
    
    assert handler.name, 'The handler needs a name'

    await persistence.refresh_conversation(
        name=handler.name,
        conversations_data=handler._conversations,
        key=key
    )



"""
Modified process_update(...) method from PTB's Application.process_update.

PTB currently does not have an integrated method for refreshing conversation data.,
However, this is essential when working with a bot that runs in multi-worker webhook mode.,
Refreshing conversation data is essential for synchronizing data from the datastore (database),
with the current conversation data in the process memory.


So since PTB does not have this integrated method,
I created this custom process_update method to be able to refresh conversation data.

How to Use:
from ptb_persistence import PTBPersistence
from ptb_persistence.utils.ptb import process_update

from ptb_persistence.datastores.mongodb import MongoDBDataStore
from telegram.ext import Application

data_store = MongoDBDataStore( ... )

ptb_persistence = PTBPersistence( data_store=data_store )

application = Application.builder().token("<bot-token>").persistence(ptb_persistence).build()

# Overwrite the original process_update method with the custom
application.process_update = process_update


# Remember that:
# 
# To work with persistent conversation data,
# you must enable this in your preferred data store.
# Example: MongoDBDataStore(..., collection_conversationsdata=...)
# 
# Another very important point: In the PTB ConversationHandler class,
# you must define the parameters persistent=True and name='<any-name-here>'.
# Example: ConversationHandler(..., persistent=True, name='my-handler')
"""
async def process_update(self: Application, update: object) -> None:
    """Processes a single update and marks the update to be updated by the persistence later.
    Exceptions raised by handler callbacks will be processed by :meth:`process_error`.

    .. seealso:: :wiki:`Concurrency`

    .. versionchanged:: 20.0
        Persistence is now updated in an interval set by
        :attr:`telegram.ext.BasePersistence.update_interval`.

    Args:
        update (:class:`telegram.Update` | :obj:`object` | \
            :class:`telegram.error.TelegramError`): The update to process.

    Raises:
        :exc:`RuntimeError`: If the application was not initialized.
    """
    # Processing updates before initialize() is a problem e.g. if persistence is used
    self._check_initialized()

    context = None
    any_blocking = False  # Flag which is set to True if any handler specifies block=True

    for handlers in self.handlers.values():
        try:
            for handler in handlers:

                # [ Modified part ]
                if (
                    isinstance(self.persistence, PTBPersistence) and
                    isinstance(handler, ConversationHandler) and
                    handler.persistent
                    ):
                    await _refresh_conversation_data(
                        update=update,
                        application=self,
                        handler=handler
                        )
                # [ Ends Modified part ]

                check = handler.check_update(update)  # Should the handler handle this update?
                if not (check is None or check is False):  # if yes,
                    if not context:  # build a context if not already built
                        context = self.context_types.context.from_update(update, self)
                        await context.refresh_data()
                    coroutine: Coroutine = handler.handle_update(update, self, check, context)

                    if not handler.block or (  # if handler is running with block=False,
                        handler.block is DEFAULT_TRUE
                        and isinstance(self.bot, ExtBot)
                        and self.bot.defaults
                        and not self.bot.defaults.block
                    ):
                        self.create_task(coroutine, update=update)
                    else:
                        any_blocking = True
                        await coroutine
                    break  # Only a max of 1 handler per group is handled

        # Stop processing with any other handler.
        except ApplicationHandlerStop:
            _logger.debug("Stopping further handlers due to ApplicationHandlerStop")
            break

        # Dispatch any error.
        except Exception as exc:
            if await self.process_error(update=update, error=exc):
                _logger.debug("Error handler stopped further handlers.")
                break

    if any_blocking:
        # Only need to mark the update for persistence if there was at least one
        # blocking handler - the non-blocking handlers mark the update again when finished
        # (in __create_task_callback)
        self._mark_for_persistence_update(update=update)


