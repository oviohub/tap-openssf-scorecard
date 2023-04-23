"""Stream type classes for tap-openssf-scorecard."""

from __future__ import annotations

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

    See https://github.com/ossf/scorecard/blob/main/README.md#scorecard-checks
    for more details.
    """

    name = "scorecard"
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

    def normalize(self, s: str) -> str:
        return s.lower().replace("-", "_")

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        repo = row.pop("repo")
        row["repo_name"] = repo["name"]
        row["repo_commit"] = repo["commit"]
        # return scores as integers between 0-100 instead of decimals 0-10
        row["score"] = int(row["score"] * 10)
        new_checks = dict()

        assert row is not None, f"Scorecard result error: {row}"
        if row["checks"] is None:
            self.logger.error(f"Scorecard checks empty for {repo}")
            return None

        for check in row["checks"]:
            d = {k: check[k] for k in check if k not in ["documentation", "name"]}
            d["score"] = int(d["score"] * 10)
            new_checks[f"{self.normalize(check['name'])}"] = d
        row["checks"] = new_checks
        return row
