"""openSSF-scorecard tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_openssf_scorecard import streams


class TapopenSSFScorecard(Tap):
    """openSSF-scorecard tap class."""

    name = "tap-openssf-scorecard"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "auth_token",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "project_urls",
            th.ArrayType(th.StringType),
            required=True,
            description="Project urls (eg. https://github.com/meltano/sdk",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
        th.Property(
            "api_url",
            th.StringType,
            default="https://api.mysample.com",
            description="The url for the API service",
        ),
        th.Property(
            "use_local_scorecard_cli",
            th.BooleanType,
            required=False,
            default=False,
            description="Use a locally installed version of the scorecard cli.",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.openSSFScorecardStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.ScorecardStream(self),
        ]


if __name__ == "__main__":
    TapopenSSFScorecard.cli()
