"""
This module provides a command-line interface (CLI) for an AI-based code security scanner.
It supports scanning code using different AI providers, including OpenAI, Google Generative AI,
and custom AI servers. The CLI allows scanning all files in a directory or only files changed in
a Git repository.
"""

import argparse
from importlib.metadata import PackageNotFoundError, version

from IPython.display import display_markdown

from guard.clients import CustomAIClient, GoogleClient, GroqClient, OpenAIClient
from guard.scanner import scan_changes, scan_files


def get_guardai_version():
    """
    Retrieves the version of the GuardAI package.
    Returns "unknown" if the package is not found.
    """
    try:
        return version("guardai")
    except PackageNotFoundError:
        return "unknown"


def parse_arguments():
    """
    Parses command-line arguments for the AI-based code scanner.
    """
    parser = argparse.ArgumentParser(
        description="A CLI tool for AI-powered code security scanning"
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"GuardAI {get_guardai_version()}",
        help="Show the version of the GuardAI tool and exit",
    )

    parser.add_argument(
        "--provider",
        type=str,
        required=True,
        choices=["openai", "google", "groq", "custom"],
        help="Select the AI provider",
    )
    parser.add_argument(
        "--directory",
        type=str,
        default=".",
        help="Directory to scan (defaults to root)",
    )
    parser.add_argument(
        "--model",
        type=str,
        help="AI model to use (optional, defaults vary by provider)",
    )
    parser.add_argument(
        "--changes_only",
        action="store_true",
        help="Scan only changed files in a git repository",
    )

    # Additional arguments for PR scanning
    parser.add_argument(
        "--repo", type=str, help="GitHub repository in the format 'owner/repo'"
    )
    parser.add_argument("--pr_number", type=int, help="Pull request number")
    parser.add_argument("--github_token", help="GitHub API token")

    # Additional arguments for custom provider
    parser.add_argument(
        "--host", type=str, help="Custom AI server host (e.g., http://localhost)"
    )
    parser.add_argument("--port", type=int, help="Custom AI server port (e.g., 5000)")
    parser.add_argument(
        "--token", type=str, help="Token for authenticating with the custom AI server"
    )
    parser.add_argument(
        "--endpoint",
        type=str,
        default="/api/v1/scan",
        help="API endpoint for the custom server",
    )

    return parser.parse_args()


def initialize_client(provider, model, host=None, port=None, token=None, endpoint=None):
    """
    Initializes and returns the appropriate AI client based on the provider.
    """
    clients = {
        "openai": OpenAIClient,
        "google": GoogleClient,
        "groq": GroqClient,
        "custom": CustomAIClient,
    }

    default_models = {
        "openai": "gpt-4o-mini",
        "google": "gemini-pro",
        "groq": "llama3-8b-8192",
    }

    if provider == "custom":
        client_params = {
            "model": model,
            "host": host,
            "port": port,
            "token": token,
            "endpoint": endpoint,
        }
    else:
        client_params = {
            "model": model if model else default_models[provider],
        }

    return clients[provider](**client_params)


def scan(args, ai_client):
    """
    Scans the code based on the provided arguments and AI client.
    """
    if args.changes_only:
        return scan_changes(
            args.directory,
            ai_client,
            repo=args.repo if args.repo else None,
            pr_number=args.pr_number if args.pr_number else None,
            github_token=args.github_token if args.github_token else None,
        )
    return scan_files(args.directory, ai_client)


def format_as_markdown(result):
    """
    Formats the scan result as Markdown.
    """
    output = "## Code Security Analysis Results\n"
    output += result
    return output


def main():
    """
    Main entry point for the CLI. Parses arguments, initializes the AI client,
    performs the scan, and displays the results.
    """
    args = parse_arguments()
    ai_client = initialize_client(
        args.provider, args.model, args.host, args.port, args.token, args.endpoint
    )
    result = scan(args, ai_client)
    formatted_result = format_as_markdown(result)
    display_markdown(formatted_result)


if __name__ == "__main__":
    main()
