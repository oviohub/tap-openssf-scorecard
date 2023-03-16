# tap-openssf-scorecard

`tap-openssf-scorecard` is a Singer tap for openSSF-scorecard.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

Install from PyPi:

```bash
pipx install tap-openssf-scorecard
```

Install from GitHub:

```bash
pipx install git+https://github.com/oviohub/tap-openssf-scorecard.git@main
```

## Configuration

### Accepted Config Options

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`
* `schema-flattening`

## Settings

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| auth_token          | True     | None    | The token to authenticate against the API service |
| project_urls        | True     | None    | Project urls (eg. https://github.com/meltano/sdk |
| start_date          | False    | None    | The earliest record date to sync |
| api_url             | False    | https://api.mysample.com | The url for the API service |
| use_local_scorecard_cli| False | False | Use a locally installed version of the scorecard CLI. |
| local_scorecard_cli_path| False| "./scorecard" | Path to your locally installed version of the scorecard CLI. |
| stream_maps         | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config   | False    | None    | User-defined config values to be used within map expressions. |
| flattening_enabled  | False    | None    | 'True' to enable schema flattening and automatically expand nested properties. |
| flattening_max_depth| False    | None    | The max depth to flatten schemas. |

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-openssf-scorecard --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

To run tests, please set `TEST_GITHUB_TOKEN` to a valid token (classic) as detailed in the
[openssf docs](https://github.com/ossf/scorecard/blob/main/README.md#authentication).

## Usage

You can easily run `tap-openssf-scorecard` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-openssf-scorecard --version
tap-openssf-scorecard --help
tap-openssf-scorecard --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_openssf_scorecard/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-openssf-scorecard` CLI interface directly using `poetry run`:

```bash
poetry run tap-openssf-scorecard --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-openssf-scorecard
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-openssf-scorecard --version
# OR run a test `elt` pipeline:
meltano elt tap-openssf-scorecard target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
