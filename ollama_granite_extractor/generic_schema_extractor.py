"""Generic schema-driven extraction using Ollama.

This module allows extracting structured JSON for any domain by passing:
- a context JSON object (e.g., inventory, catalog, HR policy, CRM records)
- an output schema JSON object (JSON Schema)
"""

import json
import os
import re
from typing import Optional

import requests

DEFAULT_OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11435/api")
DEFAULT_MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
DEFAULT_API_TIMEOUT = 60


def _load_json_file(json_path: str) -> dict:
    """Load a JSON file with resilient relative path resolution."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.isabs(json_path):
        full_path = json_path
    else:
        workspace_root = os.path.dirname(script_dir)
        candidates = [
            os.path.abspath(json_path),
            os.path.join(script_dir, json_path),
            os.path.join(workspace_root, json_path),
        ]

        full_path = None
        for candidate in candidates:
            if os.path.exists(candidate):
                full_path = candidate
                break

        if full_path is None:
            full_path = candidates[0]

    with open(full_path, "r") as file:
        return json.load(file)


class GenericSchemaExtractor:
    """Generic extractor that enforces caller-provided JSON schema."""

    def __init__(
        self,
        ollama_api_url: Optional[str] = None,
        model_name: Optional[str] = None,
        api_timeout: int = DEFAULT_API_TIMEOUT,
    ):
        self.ollama_api_url = ollama_api_url or DEFAULT_OLLAMA_API_URL
        self.model_name = model_name or DEFAULT_MODEL_NAME
        self.api_timeout = api_timeout

    def check_ollama_server(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(
                f"{self.ollama_api_url.replace('/api', '')}/api/tags",
                timeout=2,
            )
            return response.status_code == 200
        except Exception:
            return False

    def load_model(self, verbose: bool = True):
        """Verify Ollama is running and model is available."""
        if not self.check_ollama_server():
            raise RuntimeError(
                f"Ollama server not running at {self.ollama_api_url}\n"
                f"Start it with: ollama serve\n"
                f"Pull model: ollama pull {self.model_name}"
            )

        if verbose:
            print(f"Ollama server online at {self.ollama_api_url}")
            print(f"Model: {self.model_name}")

        return None, None, "ollama"

    def build_prompt(
        self,
        input_text: str,
        context_json: dict,
        output_schema: dict,
        instructions: Optional[str] = None,
    ) -> str:
        """Build a generic extraction prompt from caller-provided context and schema."""
        extra_instructions = instructions or (
            "Extract only information grounded in CONTEXT JSON and INPUT TEXT. "
            "If unknown, return safe defaults according to schema."
        )

        return f"""You are an expert structured extraction assistant.

TASK:
Return only valid JSON that matches OUTPUT_SCHEMA exactly.

INSTRUCTIONS:
{extra_instructions}

CONTEXT_JSON:
{json.dumps(context_json, indent=2)}

INPUT_TEXT:
{input_text}

OUTPUT_SCHEMA:
{json.dumps(output_schema, indent=2)}

Respond with only JSON and no extra text.
"""

    def generate_json_with_schema(
        self,
        input_text: str,
        context_json: dict,
        output_schema: dict,
        instructions: Optional[str] = None,
    ) -> tuple[dict, str]:
        """Call Ollama with caller-provided schema for guaranteed JSON shape."""
        prompt = self.build_prompt(
            input_text=input_text,
            context_json=context_json,
            output_schema=output_schema,
            instructions=instructions,
        )

        try:
            response = requests.post(
                f"{self.ollama_api_url}/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "format": output_schema,
                    "options": {
                        "temperature": 0,
                        "num_predict": 400,
                    },
                },
                timeout=self.api_timeout,
            )
            response.raise_for_status()

            result = response.json()
            raw_output = result.get("response", "").strip()

            try:
                parsed = json.loads(raw_output)
            except json.JSONDecodeError:
                json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                else:
                    parsed = {}

            return parsed, raw_output

        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.ollama_api_url}\n"
                f"Start server: ollama serve\n"
                f"Pull model: ollama pull {self.model_name}"
            )
        except Exception as error:
            raise RuntimeError(f"Ollama API error: {error}")

    def extract_structured(
        self,
        input_text: str,
        context_json: dict,
        output_schema: dict,
        instructions: Optional[str] = None,
    ) -> tuple[dict, str]:
        """Extract structured JSON using provided context and output schema."""
        if not isinstance(context_json, dict):
            raise ValueError("context_json must be a dictionary")
        if not isinstance(output_schema, dict):
            raise ValueError("output_schema must be a dictionary")
        if not input_text or not input_text.strip():
            raise ValueError("input_text must be a non-empty string")

        return self.generate_json_with_schema(
            input_text=input_text,
            context_json=context_json,
            output_schema=output_schema,
            instructions=instructions,
        )


def create_generic_extractor(
    ollama_api_url: Optional[str] = None,
    model_name: Optional[str] = None,
    api_timeout: int = DEFAULT_API_TIMEOUT,
) -> GenericSchemaExtractor:
    """Create a generic schema-driven extractor."""
    return GenericSchemaExtractor(
        ollama_api_url=ollama_api_url,
        model_name=model_name,
        api_timeout=api_timeout,
    )


def extract_with_schema(
    input_text: str,
    context_json: dict,
    output_schema: dict,
    instructions: Optional[str] = None,
    ollama_api_url: Optional[str] = None,
    model_name: Optional[str] = None,
    api_timeout: int = DEFAULT_API_TIMEOUT,
) -> tuple[dict, str]:
    """One-shot generic extraction with caller-provided schema."""
    extractor = create_generic_extractor(
        ollama_api_url=ollama_api_url,
        model_name=model_name,
        api_timeout=api_timeout,
    )
    return extractor.extract_structured(
        input_text=input_text,
        context_json=context_json,
        output_schema=output_schema,
        instructions=instructions,
    )


def extract_with_schema_files(
    input_text: str,
    context_json_path: str,
    output_schema_path: str,
    instructions: Optional[str] = None,
    ollama_api_url: Optional[str] = None,
    model_name: Optional[str] = None,
    api_timeout: int = DEFAULT_API_TIMEOUT,
) -> tuple[dict, str]:
    """One-shot generic extraction loading context and schema from JSON files."""
    context_json = _load_json_file(context_json_path)
    output_schema = _load_json_file(output_schema_path)
    return extract_with_schema(
        input_text=input_text,
        context_json=context_json,
        output_schema=output_schema,
        instructions=instructions,
        ollama_api_url=ollama_api_url,
        model_name=model_name,
        api_timeout=api_timeout,
    )
