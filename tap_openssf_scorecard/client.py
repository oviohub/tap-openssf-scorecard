"""Custom client handling, including openSSF-scorecardStream base class."""

from __future__ import annotations

from typing import Iterable

from singer_sdk.streams import RESTStream


class openSSFScorecardStream(RESTStream):
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
            self.logger.info(f"Running scorecard on {repo_url}.")
            if repo_url == "":
                continue

            context = {"repo_url": "%2F".join(repo_url.rsplit("/", 2)[1:])}
            yield from super().get_records(context)

    def get_scorecard_command(self, repo_url: str) -> list[str]:
        """
        Decide which version of scorecard to use (local, docker)
        and return a command ready to pass to subprocess.run()

        Args:
            repo_url: (string) the full url to the repo

        Returns:
            list of command line parts (strings)
        """
        if self.config["local_scorecard_cli_path"]:
            cmd = [
                self.config["local_scorecard_cli_path"],
                "--show-details",
                "--format=json",
                f"--repo={repo_url}",
            ]
        else:
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
        return cmd
