# off-grid

[![PyPI - Version](https://img.shields.io/pypi/v/off-grid.svg)](https://pypi.org/project/off-grid)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/off-grid.svg)](https://pypi.org/project/off-grid)

---

## Table of Contents

- [Usage](#usage)
- [Deployment](#deployment)
- [License](#license)

## Usage

### Prerequisites

- `hatch`
- `npm`

### Backend

1. Download the data.

```
hatch run python scripts/download_slf_layers.py
./scripts/convert_cat.sh
```

_Note: This will take a while, and download ~2GB of raster data._

1. Start the fastapi dev server.

```shell
hatch run fastapi dev src/off_grid/main.py
```

Now you can have a look at the API docs at `localhost:8000/docs`.

### Frontend

1. Install the dependencies

```shell
npm install
```

1. Start the Next.js dev server.

```shell
npm run dev
```

Now you can visit the app at `localhost:3000`

## Deployment

// TODO

## License

`off-grid` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
