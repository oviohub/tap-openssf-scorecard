"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import os

from singer_sdk.testing import get_tap_test_class

from tap_openssf_scorecard.tap import TapopenSSFScorecard

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    "auth_token": os.getenv("TEST_GITHUB_TOKENN", "faketoken"),
    "project_urls": [
        # available from deps.dev
        "https://github.com/pytorch/pytorch",
        # not available, runs the binary scorecard
        "https://github.com/meltano/sdk",
    ],
}


# Run standard built-in tap tests from the SDK:
TestTapopenSSFScorecard = get_tap_test_class(
    tap_class=TapopenSSFScorecard, config=SAMPLE_CONFIG
)


# TODO: Create additional tests as appropriate for your tap.
