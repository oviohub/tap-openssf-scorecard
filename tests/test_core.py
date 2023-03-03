"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import os

from singer_sdk.testing import get_tap_test_class

from tap_openssf_scorecard.tap import TapopenSSFScorecard

SAMPLE_CONFIG = {
    "start_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
    "auth_token": os.getenv("GITHUB_TOKEN"),
    "project_urls": ["https://github.com/laurentS/slowapi"],
}


# Run standard built-in tap tests from the SDK:
TestTapopenSSFScorecard = get_tap_test_class(
    tap_class=TapopenSSFScorecard, config=SAMPLE_CONFIG
)


# TODO: Create additional tests as appropriate for your tap.
