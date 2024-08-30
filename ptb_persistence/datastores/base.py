from ..abc import DataStore


class BaseDataStore(DataStore):
    """Base class for data stores."""

    _inited: bool = None

    async def post_init(self) -> None:
        if self._inited:
            return
        
        self._inited = True
        