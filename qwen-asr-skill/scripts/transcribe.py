#!/usr/bin/env python3
"""
Qwen ASR Transcription Script
Transcribes audio files using Qwen ASR models via OpenAI-compatible API.
"""

import os
import sys
import argparse
import base64
import pathlib
from openai import OpenAI


def encode_audio_file(file_path):
    """Encode local audio file to base64 data URI."""
    file_path_obj = pathlib.Path(file_path)
    if not file_path_obj.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    # Determine MIME type based on file extension
    mime_types = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac"
    }
    ext = file_path_obj.suffix.lower()
    mime_type = mime_types.get(ext, "audio/mpeg")

    base64_str = base64.b64encode(file_path_obj.read_bytes()).decode()
    return f"data:{mime_type};base64,{base64_str}"


def transcribe(
    audio_input,
    api_key=None,
    region="cn",
    model="qwen3-asr-flash",
    language=None,
    enable_itn=False,
    stream=False
):
    """
    Transcribe audio using Qwen ASR.

    Args:
        audio_input: Audio file path or URL
        api_key: DashScope API key (defaults to DASHSCOPE_API_KEY env var)
        region: "cn" for China or "intl" for International
        model: Model name (default: qwen3-asr-flash)
        language: Language code (e.g., "zh", "en") or None for auto-detect
        enable_itn: Enable Inverse Text Normalization
        stream: Enable streaming output

    Returns:
        dict: Transcription result with text and metadata
    """
    # Configure base URL based on region
    base_urls = {
        "cn": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "intl": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    }

    # Initialize OpenAI client
    client = OpenAI(
        api_key=api_key or os.getenv("DASHSCOPE_API_KEY"),
        base_url=base_urls.get(region, base_urls["cn"])
    )

    # Determine if input is URL or local file
    if audio_input.startswith(("http://", "https://")):
        audio_data = audio_input
    else:
        audio_data = encode_audio_file(audio_input)

    # Build messages
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_audio",
                    "input_audio": {"data": audio_data}
                }
            ]
        }
    ]

    # Build asr_options
    asr_options = {"enable_itn": enable_itn}
    if language:
        asr_options["language"] = language

    # Call API
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream,
            extra_body={"asr_options": asr_options}
        )

        if stream:
            # Handle streaming response
            full_content = ""
            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    print(content, end="", flush=True)
            print()  # New line after streaming
            return {"text": full_content, "streaming": True}
        else:
            # Handle non-streaming response
            result = {
                "text": completion.choices[0].message.content,
                "streaming": False
            }

            # Extract metadata if available
            if hasattr(completion.choices[0].message, "annotations"):
                annotations = completion.choices[0].message.annotations
                if annotations:
                    result["language"] = annotations[0].get("language")
                    result["emotion"] = annotations[0].get("emotion")

            # Extract usage info
            if hasattr(completion, "usage"):
                result["usage"] = {
                    "audio_tokens": completion.usage.prompt_tokens_details.audio_tokens,
                    "text_tokens": completion.usage.completion_tokens_details.text_tokens,
                    "seconds": completion.usage.seconds,
                    "total_tokens": completion.usage.total_tokens
                }

            return result

    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio using Qwen ASR"
    )
    parser.add_argument(
        "audio",
        help="Audio file path or URL"
    )
    parser.add_argument(
        "--api-key",
        help="DashScope API key (or set DASHSCOPE_API_KEY env var)"
    )
    parser.add_argument(
        "--region",
        choices=["cn", "intl"],
        default="cn",
        help="Region: cn (China) or intl (International)"
    )
    parser.add_argument(
        "--model",
        default="qwen3-asr-flash",
        help="Model name"
    )
    parser.add_argument(
        "--language",
        help="Language code (e.g., zh, en, ja)"
    )
    parser.add_argument(
        "--enable-itn",
        action="store_true",
        help="Enable Inverse Text Normalization"
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Enable streaming output"
    )

    args = parser.parse_args()

    result = transcribe(
        audio_input=args.audio,
        api_key=args.api_key,
        region=args.region,
        model=args.model,
        language=args.language,
        enable_itn=args.enable_itn,
        stream=args.stream
    )

    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if not args.stream:
        print(f"\nTranscription: {result['text']}")
        if "language" in result:
            print(f"Language: {result['language']}")
        if "emotion" in result:
            print(f"Emotion: {result['emotion']}")
        if "usage" in result:
            print(f"Audio duration: {result['usage']['seconds']}s")
            print(f"Total tokens: {result['usage']['total_tokens']}")


if __name__ == "__main__":
    main()
