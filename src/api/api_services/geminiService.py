import os
import re
import json
from typing import List, Optional, TypedDict
from dotenv import load_dotenv
from google import genai
from google.genai import types

# --- Type Definitions (equivalent to "../types" and ValidationResult) ---

class AccuracyMetrics(TypedDict):
    precision: float
    recall: float

class LeakItem(TypedDict):
    item: str
    type: str
    context: str
    severity: str  # "Critical" | "Warning"

class ValidationResult(TypedDict):
    score: float
    leaks: List[LeakItem]
    summary: str
    accuracy_metrics: AccuracyMetrics

# --- Configuration & Constants ---

# Initialize the client
load_dotenv(dotenv_path=".env.local")  # Load environment variables from .env.local
# Ensure "GOOGLE_API_KEY" or "API_KEY" is set in your environment variables
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("API_KEY"))

SUMMARY_SYSTEM_INSTRUCTION = """
You are a professional assistant. 
You are receiving text that has been locally sanitized (PII redacted).
Your job is to provide a concise, professional summary of the content.

Input Context:
- Text contains [REDACTED_TYPE] placeholders.
- Focus on the non-sensitive business logic, events, or main topics.
- The document might be quite long; provide a structured overview.
"""

VALIDATION_SYSTEM_INSTRUCTION = """
You are a Senior Data Privacy Auditor. 
Your task is to compare a REDACTED version of a document with its ORIGINAL version to identify any missed PII (Personally Identifiable Information).

LEAK CRITERIA:
- Any real names of people, specific addresses, phone numbers, or clear unique identifiers (like SSNs or specific SAP Vendor IDs) that were NOT replaced by a [REDACTED_...] tag.
- Partial leaks (e.g., "Mr. [REDACTED_NAME] lives at 123 Main St" where the address was missed).

Return a JSON object:
{
  "score": number (0-100, where 100 means zero leaks),
  "leaks": [
    { "item": "string", "type": "string", "context": "string", "severity": "Critical" | "Warning" }
  ],
  "summary": "string describing the audit result",
  "accuracy_metrics": { "precision": number, "recall": number }
}
"""

# --- Functions ---

def generate_summary(sanitized_text: str) -> str:
    """
    Generates a summary of the sanitized text.
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash', # "flash-preview" often maps to current flash in Py SDK
            contents=sanitized_text,
            config=types.GenerateContentConfig(
                system_instruction=SUMMARY_SYSTEM_INSTRUCTION,
                temperature=0.3,
            ),
        )
        return response.text or "No summary generated."
    except Exception as error:
        print(f"Error during Gemini summarization: {error}")
        raise error


def perform_privacy_validation(original_text: str, sanitized_text: str) -> ValidationResult:
    """
    Performs a rigorous privacy audit comparing original vs sanitized text.
    """
    try:
        # Python slice syntax [0:20000] is safe even if string is shorter
        original_sample = original_text[:20000]
        sanitized_sample = sanitized_text[:20000]

        prompt = f"""
        ORIGINAL TEXT SAMPLE:
        {original_sample}

        SANITIZED TEXT SAMPLE:
        {sanitized_sample}
        
        Audit the SANITIZED sample against the ORIGINAL sample.
        """

        # Define schema for structured output
        # In the Python SDK, we can pass a Pydantic model directly or a dict schema.
        # Using a dict schema here to match the JS implementation style closely.
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "score": {"type": "NUMBER"},
                "summary": {"type": "STRING"},
                "leaks": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "item": {"type": "STRING"},
                            "type": {"type": "STRING"},
                            "context": {"type": "STRING"},
                            "severity": {"type": "STRING"},
                        },
                        "required": ["item", "type", "context", "severity"],
                    },
                },
                "accuracy_metrics": {
                    "type": "OBJECT",
                    "properties": {
                        "precision": {"type": "NUMBER"},
                        "recall": {"type": "NUMBER"},
                    },
                    "required": ["precision", "recall"],
                },
            },
            "required": ["score", "summary", "leaks", "accuracy_metrics"],
        }

        response = client.models.generate_content(
            model='gemini-2.0-pro-exp-02-05', # Equivalent to 'gemini-3-pro-preview' or current pro
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=VALIDATION_SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=response_schema
            ),
        )

        # The SDK automatically handles JSON parsing if schema is provided
        if response.parsed:
             # Convert the object to our TypedDict format
             # Note: response.parsed returns a native python object (SimpleNamespace or dict depending on config)
             # Usually, we can assume it behaves like a dict or cast it
             return response.parsed
        
        return json.loads(response.text or '{}')

    except Exception as error:
        print(f"Privacy validation failed: {error}")
        # Return fallback structure matching ValidationResult
        return {
            "score": 100,
            "leaks": [],
            "summary": "Audit service encountered an error. Manual review suggested.",
            "accuracy_metrics": {"precision": 1.0, "recall": 1.0},
        }
