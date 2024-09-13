"""
This module defines AI client classes for scanning code using different AI providers.
"""

import os

import google.generativeai as genai
import groq
import openai
import requests


class BaseAIClient:
    """Abstract base class for AI clients."""

    def __init__(self):
        """Initializes the base AI client."""
        raise NotImplementedError(
            "BaseAIClient is an abstract class and cannot be instantiated directly."
        )

    def scan_code(self, code_summary):
        """Scans the provided code summary for security vulnerabilities."""
        raise NotImplementedError("Each AI client must implement the scan_code method.")


class OpenAIClient(BaseAIClient):
    """Client for interacting with the OpenAI API."""

    def __init__(self, model):
        """Initializes the OpenAI client with the given model."""

        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is not set in the environment.")
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model

    def scan_code(self, code_summary):
        """Scans the code using OpenAI."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert in software security analysis, 
                    adept at identifying and explaining potential vulnerabilities in code. You will be 
                    given complete code snippets from various applications. Your task is to analyze 
                    the provided code, pinpoint potential security risks, and offer clear suggestions 
                    for enhancing the application's security posture. Focus on the critical issues that 
                    could impact the overall security of the application.""",
                    },
                    {"role": "user", "content": code_summary},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:  # pylint: disable=W0718
            return f"Error occurred: {e}"


class GoogleClient(BaseAIClient):
    """Client for interacting with the Google Generative AI API."""

    def __init__(self, model):
        """Initializes the Google client with the given model."""

        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is not set in the environment.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)

    def scan_code(self, code_summary):
        try:
            response = self.model.generate_content(
                """You are a specialist in application security, known for your ability to 
                analyze complex codebases and uncover hidden vulnerabilities. You will be 
                presented with the full code of an application. Your mission is to conduct 
                a thorough security review, identifying potential weaknesses and offering 
                actionable recommendations for improvement. Prioritize the most significant 
                security risks that could compromise the integrity of the application. 
                Here is the code:"""
                + code_summary,
            )
            return response.text
        except Exception as e:  # pylint: disable=W0718
            return f"Error occurred: {e}"


class GroqClient(BaseAIClient):
    """Client for interacting with the Groq."""

    def __init__(self, model):
        """Initializes the Groq client with the given model."""

        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key is not set in the environment.")
        self.client = groq.Groq(
            api_key=self.api_key,
        )
        self.model = model

    def scan_code(self, code_summary):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert in software security analysis, 
                    adept at identifying and explaining potential vulnerabilities in code. You will be 
                    given complete code snippets from various applications. Your task is to analyze 
                    the provided code, pinpoint potential security risks, and offer clear suggestions 
                    for enhancing the application's security posture. Focus on the critical issues that 
                    could impact the overall security of the application.""",
                    },
                    {"role": "user", "content": code_summary},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:  # pylint: disable=W0718
            return f"Error occurred: {e}"


class CustomAIClient(BaseAIClient):
    """Client for interacting with a custom AI server."""

    def __init__(self, model, host, port, token=None, endpoint="/api/v1/scan"):
        """Initializes the custom AI client with the given parameters."""

        self.model = model
        self.host = host
        self.port = port
        self.token = token
        self.endpoint = endpoint
        self.base_url = f"{host}:{port}{endpoint}"

    def scan_code(self, code_summary):
        """Scans the code using the custom AI server."""

        headers = {"Authorization": f"Bearer {self.token}" if self.token else ""}
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": """You are an experienced application security specialist, entrusted with the task of 
                    carefully reviewing the following code for potential security vulnerabilities. Your objective 
                    is to conduct a comprehensive analysis, identifying any weak points that could be exploited 
                    by malicious actors. Once identified, provide clear and actionable recommendations to 
                    mitigate these risks and strengthen the overall security posture of the application. 
                    Focus on issues that could compromise the integrity, confidentiality, or availability 
                    of the system, and ensure that your suggestions are practical and implementable. 
                    Here is the code you need to review:
                    """
                    + code_summary,
                },
            ],
        }
        try:
            response = requests.post(
                self.base_url, json=payload, headers=headers, timeout=120
            )
            response.raise_for_status()
            return (
                response.json()
                .get("message", {})
                .get("content", "No response content.")
            )
        except requests.exceptions.RequestException as e:
            return f"Error occurred while connecting to the server: {e}"
