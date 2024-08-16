"""
This module provides functions for working with Git repositories and interacting 
with GitHub to retrieve and scan changed files. It includes utilities for checking 
if a directory is a Git repository, retrieving changed files from local repositories 
or GitHub pull requests, and generating summaries of code for analysis by AI clients.
"""

import logging
import os
import subprocess

from github import Github

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def is_git_repo(directory):
    """
    Checks if the directory is a valid Git repository.
    """
    try:
        subprocess.check_output(
            ["git", "-C", directory, "rev-parse", "--is-inside-work-tree"],
            stderr=subprocess.STDOUT,
        )
        return True
    except subprocess.CalledProcessError:
        logging.error("Directory is not a valid Git repository: %s", directory)
        return False


def get_pr_changed_files(repo_name, pr_number, github_token):
    """
    Returns a list of files that have been changed in the specified pull request.
    """
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    files = pr.get_files()

    changed_files = [file.filename for file in files]
    logging.info(
        "Fetched %d changed files from PR #%d in repo %s",
        len(changed_files),
        pr_number,
        repo_name,
    )
    return changed_files


def read_files_and_generate_summary(file_paths):
    """
    Reads the content of the given files and generates a code summary.
    Skips files that cannot be decoded as text.
    """
    code_summary = ""
    for file_path in file_paths:
        if os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    logging.info("Reading %s", file_path)
                    code_summary += f"\n\nFile: {os.path.basename(file_path)}\n"
                    code_summary += f.read()
            except (UnicodeDecodeError, IOError) as e:
                logging.warning("Skipping file %s: %s", file_path, e)
        else:
            logging.warning("Skipped %s: Not a valid file.", file_path)
    return code_summary


def scan_files(directory, ai_client):
    """
    Scans all files in the specified directory.
    """
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))

    code_summary = read_files_and_generate_summary(file_paths)
    return ai_client.scan_code(code_summary)


def generate_code_summary(directory, changed_files):
    """
    Generates a summary of the code from the changed files.
    """
    file_paths = [os.path.join(directory, file) for file in changed_files]
    return read_files_and_generate_summary(file_paths)


def get_changed_files(directory):
    """
    Returns a list of files that have been changed locally.
    """
    changed_files = []
    try:
        os.chdir(directory)
        result = subprocess.check_output(["git", "diff", "--name-only"], text=True)
        if result.strip():
            changed_files = result.strip().split("\n")
            logging.info(
                "Found %d changed files in local repository", len(changed_files)
            )
    except subprocess.CalledProcessError as e:
        logging.error("Error getting changed files: %s", e)
    return changed_files


def fetch_changed_files_from_pr(repo, pr_number, github_token):
    """
    Fetches the list of changed files from a GitHub PR.
    """
    if not github_token:
        logging.error("GitHub token is required for scanning PR changes.")
        raise ValueError("GitHub token is required for scanning PR changes.")
    return get_pr_changed_files(repo, pr_number, github_token)


def fetch_changed_files_from_repo(directory):
    """
    Fetches the list of changed files from a local Git repository.
    """
    if not is_git_repo(directory):
        logging.error("Directory is not a valid Git repository: %s", directory)
        raise ValueError("Directory is not a valid Git repository.")
    return get_changed_files(directory)


def scan_changes(directory, ai_client, repo=None, pr_number=None, github_token=None):
    """
    Scans only the files that have been changed in the specified directory or PR.
    """
    try:
        if repo and pr_number:
            changed_files = fetch_changed_files_from_pr(repo, pr_number, github_token)
        else:
            changed_files = fetch_changed_files_from_repo(directory)
    except ValueError as e:
        logging.error(e)
        return str(e)

    if not changed_files:
        logging.info("No changes detected in the directory.")
        return "No changes detected in the directory."

    code_summary = generate_code_summary(directory, changed_files)

    return ai_client.scan_code(code_summary)
