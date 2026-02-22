"""Utility for programmatically creating GitHub issues assigned to the Copilot SWE agent."""

import json
import subprocess

# needs gh CLI (must be installed and authenticated)
# example usage create_github_issue("PawelPopkiewicz", "HackEurope", "exampleIssue", "make some example changes!"))
def create_github_issue(
    owner: str,
    repo: str,
    title: str,
    body: str,
    assignees: list[str] | None = None,
    base_branch: str = "main",
    custom_instructions: str = "",
    custom_agent: str = "",
    model: str = "",
):
    """Create a GitHub issue via the ``gh`` CLI and assign it to an agent.

    Args:
        owner: GitHub repository owner (user or organisation).
        repo: Repository name.
        title: Issue title.
        body: Issue body / description.
        assignees: GitHub usernames to assign. Defaults to the Copilot SWE agent.
        base_branch: Branch that the agent should target.
        custom_instructions: Optional extra instructions for the agent.
        custom_agent: Optional custom agent identifier.
        model: Optional LLM model override.

    Returns:
        dict: The parsed JSON response from the GitHub API.

    Raises:
        RuntimeError: If the ``gh api`` command exits with a non-zero status.
    """
    payload = {
        "title": title,
        "body": body,
        "assignees": assignees or ["copilot-swe-agent[bot]"],
        "agent_assignment": {
            "target_repo": f"{owner}/{repo}",
            "base_branch": base_branch,
            "custom_instructions": custom_instructions,
            "custom_agent": custom_agent,
            "model": model,
        },
    }

    result = subprocess.run(
        [
            "gh", "api",
            "--method", "POST",
            "-H", "Accept: application/vnd.github+json",
            "-H", "X-GitHub-Api-Version: 2022-11-28",
            f"/repos/{owner}/{repo}/issues",
            "--input", "-",
        ],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh api failed: {result.stderr}")

    return json.loads(result.stdout)

