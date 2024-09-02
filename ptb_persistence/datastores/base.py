from ..abc import DataStore
from logging import Logger


class BaseDataStore(DataStore):
    """Base class for data stores."""

    _inited: bool = None
    _logger: Logger = None

    async def post_init(self, logger: Logger) -> None:
        if self._inited:
            return
        
        self._logger = logger
        self._inited = True
        