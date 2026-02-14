---
name: qwen-asr
description: Audio transcription using Qwen ASR models via OpenAI-compatible API. Use when Claude needs to transcribe audio files to text, convert speech to text, or recognize spoken content. Supports 30+ languages, streaming output, language detection, and emotion analysis. Works with audio URLs or local files (MP3, WAV, M4A, OGG, FLAC).
---

# Qwen ASR - Audio Transcription

Transcribe audio files to text using Qwen ASR models through OpenAI-compatible API.

## Quick Start

Use the provided `transcribe.py` script for reliable transcription:

```bash
# Transcribe from URL
python scripts/transcribe.py "https://example.com/audio.mp3"

# Transcribe local file
python scripts/transcribe.py "/path/to/audio.mp3"

# With language specification
python scripts/transcribe.py audio.mp3 --language zh

# With streaming output
python scripts/transcribe.py audio.mp3 --stream

# International region
python scripts/transcribe.py audio.mp3 --region intl
```

## Setup

### 1. Install Dependencies

```bash
pip install openai
```

### 2. Configure API Key

Set the `DASHSCOPE_API_KEY` environment variable:

```bash
export DASHSCOPE_API_KEY="sk-your-api-key"
```

Or pass via `--api-key` parameter.

### 3. Choose Region

- **China (default)**: Beijing region, data stored in mainland China
- **International**: Singapore region, global scheduling (excludes China)

## Core Workflow

### Step 1: Prepare Audio Input

**Option A: Use URL**
- Audio must be publicly accessible
- Supported: HTTP/HTTPS URLs
- Example: `https://example.com/recording.mp3`

**Option B: Use Local File**
- Script automatically encodes to Base64
- Max size: 10MB
- Formats: MP3, WAV, M4A, OGG, FLAC

### Step 2: Configure Options

**Language (optional)**
- Specify if audio language is known
- Improves accuracy for single-language audio
- See [references/languages.md](references/languages.md) for codes
- Omit for auto-detection or multi-language audio

**ITN - Inverse Text Normalization (optional)**
- Converts spoken numbers/dates to standard format
- Only works for Chinese and English
- Example: "二零二四年" → "2024年"
- Enable with `--enable-itn`

**Streaming (optional)**
- Real-time output as transcription progresses
- Better user experience for long audio
- Enable with `--stream`

### Step 3: Run Transcription

Use the script:

```bash
python scripts/transcribe.py <audio> [options]
```

### Step 4: Process Results

**Non-streaming output includes:**
- Transcribed text
- Detected language
- Detected emotion
- Audio duration and token usage

**Streaming output:**
- Text appears in real-time
- No metadata in streaming mode

## Implementation Guide

When implementing transcription in code:

### Python Implementation

```python
from openai import OpenAI
import os

# Initialize client
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# For URL input
completion = client.chat.completions.create(
    model="qwen3-asr-flash",
    messages=[{
        "role": "user",
        "content": [{
            "type": "input_audio",
            "input_audio": {
                "data": "https://example.com/audio.mp3"
            }
        }]
    }],
    extra_body={
        "asr_options": {
            "language": "zh",  # Optional
            "enable_itn": False  # Optional
        }
    }
)

text = completion.choices[0].message.content
```

### For Local Files

Encode to Base64 data URI:

```python
import base64
import pathlib

file_path = pathlib.Path("audio.mp3")
base64_str = base64.b64encode(file_path.read_bytes()).decode()

# Determine MIME type
mime_types = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4"
}
mime_type = mime_types.get(file_path.suffix.lower(), "audio/mpeg")

data_uri = f"data:{mime_type};base64,{base64_str}"

# Use data_uri in API call
```

### Streaming Implementation

```python
completion = client.chat.completions.create(
    model="qwen3-asr-flash",
    messages=[...],
    stream=True
)

for chunk in completion:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## Common Patterns

### Pattern 1: Simple Transcription

User asks: "Transcribe this audio file"

```bash
python scripts/transcribe.py <audio_path_or_url>
```

### Pattern 2: Language-Specific Transcription

User asks: "Transcribe this Chinese audio"

```bash
python scripts/transcribe.py audio.mp3 --language zh
```

### Pattern 3: Real-time Transcription

User asks: "Show me the transcription as it processes"

```bash
python scripts/transcribe.py audio.mp3 --stream
```

### Pattern 4: Normalized Output

User asks: "Transcribe with proper number formatting"

```bash
python scripts/transcribe.py audio.mp3 --enable-itn
```

## Advanced Features

### Language Detection

When language is not specified, the model automatically detects it. Check the `language` field in response annotations.

### Emotion Analysis

The model detects speaker emotion:
- `neutral`, `happy`, `sad`, `angry`, `surprised`, `disgusted`, `fearful`

Access via response annotations.

### Token Usage

Monitor costs by checking usage information:
- Audio tokens: 25 tokens per second
- Text tokens: Output length
- Duration: Audio length in seconds

## Reference Documentation

For detailed parameter information:
- **API Reference**: See [references/api_reference.md](references/api_reference.md)
- **Language Codes**: See [references/languages.md](references/languages.md)

## Troubleshooting

**"Invalid API key"**
- Verify `DASHSCOPE_API_KEY` is set correctly
- China and International regions use different API keys

**"File too large"**
- Max size is 10MB
- Compress audio or use lower bitrate

**"Audio format not supported"**
- Use MP3, WAV, M4A, OGG, or FLAC
- Convert using ffmpeg if needed

**Poor accuracy**
- Specify language with `--language` if known
- Ensure audio quality is good (clear speech, low noise)
- Check if audio is in a supported language

## Model Information

**Model**: qwen3-asr-flash
- Fast, real-time transcription
- 30+ language support
- Automatic language detection
- Emotion analysis
- Streaming capable

**Limitations**:
- Max audio size: 10MB
- ITN only for Chinese and English
- Public URL or Base64 input only (no direct file upload)
