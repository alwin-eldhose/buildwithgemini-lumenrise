"""Generative media function tool for LumenRise.

Generates custom morning artwork visuals using gemini-3.1-flash-lite-image in location 'global',
saves the artifact via ToolContext, uploads the result to the public Cloud Storage bucket,
and returns the public HTTP URL.

HARDCODED PROJECT ID: "qwiklabs-gcp-03-c47843160c69"
HARDCODED BUCKET NAME: "lumenrise-media-qwiklabs-gcp-03-c47843160c69"
"""

from __future__ import annotations

import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools.tool_context import ToolContext

PROJECT_ID = "qwiklabs-gcp-03-c47843160c69"
BUCKET_NAME = "lumenrise-media-qwiklabs-gcp-03-c47843160c69"


async def generate_morning_artwork(
    prompt: str = "A warm golden sunrise over a peaceful mountain valley, soft pastel digital art",
    tool_context: ToolContext | None = None,
) -> str:
    """Generates a warm, uplifting morning visual image and returns a public HTTPS URL.

    Args:
        prompt: Description of the morning scene or theme to visualize (e.g.
          'golden sunrise over calm ocean waves', 'a serene autumn morning forest').
        tool_context: Tool context injected by ADK to store artifacts.

    Returns:
        The public HTTPS URL pointing to the generated morning artwork image.
    """
    try:
        genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        response = genai_client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=f"Generate a beautiful, serene morning artwork visual: {prompt}",
        )

        image_bytes = None
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                break

        if not image_bytes:
            return "Error: Image generation did not return image data."

        filename = f"morning_artwork_{uuid.uuid4().hex[:8]}.png"

        # (1) Save artifact in Playground / ADK via ToolContext if available
        if tool_context is not None:
            try:
                artifact_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
                await tool_context.save_artifact(filename=filename, artifact=artifact_part)
            except Exception:
                pass

        # (2) Upload same image bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type="image/png")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return public_url

    except Exception as err:
        return f"Error generating morning artwork: {err}"
