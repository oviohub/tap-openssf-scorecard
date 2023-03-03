"""Custom client handling, including openSSF-scorecardStream base class."""

from __future__ import annotations

import json
import subprocess
from typing import Iterable

from singer_sdk.streams import Stream


class openSSFScorecardStream(Stream):
    """Stream class for openSSF-scorecard streams."""

    def get_records(self, context: dict | None) -> Iterable[dict]:
        """Return a generator of record-type dictionary objects.

        The optional `context` argument is used to identify a specific slice of the
        stream if partitioning is required for the stream. Most implementations do not
        require partitioning and should ignore the `context` argument.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            dict of records
        """

        for repo_url in self.config["project_urls"]:
            cmd = [
                "docker",
                "run",
                "-e",
                f"GITHUB_AUTH_TOKEN={self.config['auth_token']}",
                "gcr.io/openssf/scorecard:stable",
                "--show-details",
                "--format=json",
                f"--repo={repo_url}",
            ]
            result = subprocess.run(cmd, capture_output=True)
            if len(result.stdout) == 0:
                self.logger.error(result.stderr)
                continue
            record = json.loads(result.stdout)
            transformed_record = self.post_process(record, context)
            if transformed_record is None:
                continue
            # the cli returns a single json line, so no need to iterate here
            yield transformed_record
