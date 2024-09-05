from typing import (
    MutableMapping,
    Tuple,
    Union
    )

ConversationKey = Tuple[Union[int, str], ...]
ConversationDict = MutableMapping[ConversationKey, object]