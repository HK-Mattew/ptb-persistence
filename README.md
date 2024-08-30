# Persistent data for lib PTB

PTBPersistence is a Python library to deal with developed bot data persistence using lib [PTB](https://github.com/python-telegram-bot/python-telegram-bot).

Developed to support multiple data storage.

Data store supported at the moment:
- MongoDB

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install.

```bash
pip install git+https://github.com/HK-Mattew/ptb-persistence.git
```

Use Poetry to install.

```bash
poetry add git+https://github.com/HK-Mattew/ptb-persistence.git
```

## Usage

```python
from ptb_persistence import PTBPersistence

from ptb_persistence.datastores.mongodb import MongoDBDataStore
from telegram.ext import Application


data_store = MongoDBDataStore(
    ...
)

ptb_persistence = PTBPersistence(
    data_store=data_store
)

application = (
    Application
    .builder()
    .token("<bot-token>")
    .persistence(ptb_persistence).build()
)

```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)