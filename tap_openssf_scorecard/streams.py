"""Stream type classes for tap-openssf-scorecard."""

from __future__ import annotations

import json
import subprocess
from typing import Iterable

from requests import Response
from singer_sdk import typing as th

from tap_openssf_scorecard.client import openSSFScorecardStream

check_object = th.ObjectType(
    # openssf scorecard returns scores between 0 and 10 with
    # 1 decimal position. We 10x them and manipulate them as int
    th.Property("score", th.IntegerType),
    th.Property("reason", th.StringType),
    th.Property("details", th.ArrayType(th.StringType)),
)


class ScorecardStream(openSSFScorecardStream):
    """OpenSSF scorecard results.

    This stream first tries to get data from deps.dev, and if it fails, it falls
    back to running the scorecard tool on the given repo to collect the required
    data from the relevant VCS.

    See https://github.com/ossf/scorecard/blob/main/README.md#scorecard-checks
    for more details.
    """

    name = "scorecard"
    path = ""
    primary_keys = ["repo_name", "repo_commit"]
    replication_key = None
    schema = th.PropertiesList(
        th.Property("repo_name", th.StringType),
        th.Property("repo_commit", th.StringType),
        th.Property("date", th.DateTimeType),
        th.Property(
            "scorecard",
            th.ObjectType(
                th.Property("version", th.StringType),
                th.Property("commit", th.StringType),
            ),
        ),
        th.Property(
            "checks",
            th.ObjectType(
                th.Property("binary_artifacts", check_object),
                th.Property("branch_protection", check_object),
                th.Property("ci_tests", check_object),
                th.Property("cii_best_practices", check_object),
                th.Property("code_review", check_object),
                th.Property("contributors", check_object),
                th.Property("dangerous_workflow", check_object),
                th.Property("dependency_update_tool", check_object),
                th.Property("fuzzing", check_object),
                th.Property("license", check_object),
                th.Property("maintained", check_object),
                th.Property("packaging", check_object),
                th.Property("pinned_dependencies", check_object),
                th.Property("sast", check_object),
                th.Property("security_policy", check_object),
                th.Property("signed_releases", check_object),
                th.Property("token_permissions", check_object),
                th.Property("vulnerabilities", check_object),
            ),
        ),
        th.Property("score", th.IntegerType),
    ).to_dict()

    @property
    def url_base(self) -> str:
        return "https://deps.dev/_/project/github/"

    def get_url(self, context: dict | None) -> str:
        if context is not None:
            url = f"{self.url_base}{context['repo_url']}"
            self.logger.warning(context)
            self.logger.warning(url)
            return url

        return ""

    def normalize(self, s: str) -> str:
        return s.lower().replace("-", "_")

    def parse_response(self, response: Response) -> Iterable[dict]:
        """
        Read API response and fallback to running scorecard subprocess in case of error.

        Args:
            response: the requests.Response object

        Returns:
            Iterable of records (dicts)
        """
        if response.status_code in [200]:
            obj = response.json()
            return [obj["project"]["scorecardV2"]]
        else:
            # data not available from the API, let's build the scorecard
            self.logger.info(f"No data for {response.url}: running scorecard locally.")
            repo_name = response.url.rsplit("/", 1)[-1].replace("%2F", "/")
            repo_url = f"https://github.com/{repo_name}"

            cmd = self.get_scorecard_command(repo_url)
            # temp_env is only really used by the local cli, not docker
            temp_env = {"GITHUB_AUTH_TOKEN": self.config["auth_token"]}

            result = subprocess.run(cmd, capture_output=True, env=temp_env)
            if len(result.stdout) == 0:
                self.logger.error(
                    f"Scorecard returned nothing for {repo_url}: {str(result.stderr)}"
                )
                # No data found at all for this repo, just give up
                return []
            record = json.loads(result.stdout)
            self.logger.info(f"Local record {record}")
            if record["score"] < 0:
                # scorecard returns -1 when it fails
                return []
            transformed_record = self.post_process(record, None)
            if transformed_record is not None:
                return transformed_record
            return []

    def validate_response(self, response: Response) -> None:
        # we expect errors for repos that are not on deps.dev.
        # pretend everything is alright and let the local binary fix things
        return None

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        repo = row.pop("repo")
        row["repo_name"] = repo["name"]
        row["repo_commit"] = repo["commit"]
        # return scores as integers between 0-100 instead of decimals 0-10
        row["score"] = int(row["score"] * 10)
        new_checks = dict()

        assert row is not None, f"Scorecard result error: {row}"
        if not (("checks" in row) or ("check" in row)):
            self.logger.error(f"Scorecard checks empty for {repo}")
            return None

        if "check" in row:
            row["checks"] = row["check"]

        for check in row["checks"]:
            d = {k: check[k] for k in check if k not in ["documentation", "name"]}
            d["score"] = int(d["score"] * 10)
            new_checks[f"{self.normalize(check['name'])}"] = d
        row["checks"] = new_checks
        return row
