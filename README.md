<p align="center"><img src="https://raw.githubusercontent.com/codeguardai/guardai/main/logo.png" width="150" ><br><h1 align="center">Code Security Vulnerabilities Scanner</h1></p>

[![Release and Publish](https://github.com/codeguardai/guardai/actions/workflows/release-publish.yml/badge.svg)](https://github.com/codeguardai/guardai/actions/workflows/release-publish.yml)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/codeguardai/guardai)
![GitHub issues](https://img.shields.io/github/issues/codeguardai/guardai)
![GitHub pull requests](https://img.shields.io/github/issues-pr/codeguardai/guardai)
![GitHub](https://img.shields.io/github/license/codeguardai/guardai)

# GuardAI

GuardAI leverages multiple AI models, including OpenAI, Gemini, and custom self-hosted AI servers, to scan code for security vulnerabilities. It is designed to integrate seamlessly into CI/CD pipelines, such as GitHub Actions, allowing developers to automatically analyze their code for potential security issues during the development process.

Full Demo: https://github.com/codeguardai/demo

## Features

- **Multi-AI Model Support:**

  - **OpenAI Integration:** Scan your code using OpenAI's powerful models like GPT-4 to identify potential security vulnerabilities.
  - **Gemini Integration:** Leverage Gemini's capabilities to analyze code for security risks.
  - **Custom AI Server Integration:** Connect to a self-hosted or privately hosted AI server to perform security scans, allowing for fully customizable and self-hosted AI solutions.

- **CI/CD Integration:**

  - Easily integrate the CLI tool into GitHub Actions, enabling automated code scanning for security vulnerabilities on every pull request.
  - Provides support for running scans on specific branches or changes in a repository.

- **Flexible Scanning Options:**
  - **Full Directory Scans:** Analyze all files within a directory for comprehensive security analysis.
  - **PR-Specific Scans:** Focus on files changed in a specific pull request to streamline the scanning process and reduce overhead.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- API keys for the supported AI models:
  - OpenAI API key
  - Gemini API key
  - Access to a custom AI server (host, port, and optional token)

### Installation

#### Option 1: Install via pip

You can install the tool directly from the repository using pip:

```bash
pip install guardai
```

This will allow you to use the `guardai` command directly in your terminal.

#### Option 2: Clone the Repository

If you prefer to clone the repository and install the dependencies manually:

```bash
git clone https://github.com/codeguardai/guardai.git
cd guardai
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Usage

#### Scanning a Directory

To scan all files within a directory:

```bash
guardai --provider openai --directory path/to/your/code
```

#### Scanning with a Custom AI Server

To scan code using a custom AI server:

```bash
guardai --provider custom --host http://localhost --port 5000 --token your_token --directory path/to/your/code
```

### Supported AI Providers

- **OpenAI:** Leverages GPT models for detailed security analysis.
- **Gemini:** Provides robust security analysis using Gemini's capabilities.
- **Custom:** Integrates with a self-hosted or privately hosted AI server, allowing for fully customizable solutions.

## Future Work

- **Caching Implementation:** A caching mechanism to store results of previously scanned files, reducing the number of API calls and optimizing performance.

- **Expanded Git Provider Support:** The tool is currently integrated with GitHub for PR-based scanning, future plans include extending support to other Git providers like GitLab, Bitbucket, and Azure Repos.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
