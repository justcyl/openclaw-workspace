# API Reference

Complete parameter reference for Qwen ASR OpenAI-compatible API.

## Endpoints

### China (Beijing)
- Base URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- HTTP: `POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`

### International (Singapore)
- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- HTTP: `POST https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions`

## Request Parameters

### model (required)
- Type: `string`
- Value: `"qwen3-asr-flash"`
- Description: Model name for transcription

### messages (required)
- Type: `array`
- Description: Message list containing audio input

Structure:
```json
[
  {
    "role": "user",
    "content": [
      {
        "type": "input_audio",
        "input_audio": {
          "data": "<URL or Base64 data URI>"
        }
      }
    ]
  }
]
```

**Audio input formats:**
1. **Public URL**: `"https://example.com/audio.mp3"`
2. **Base64 Data URI**: `"data:audio/mpeg;base64,<base64_string>"`

**Supported audio formats:**
- MP3, WAV, M4A, OGG, FLAC
- Max size: 10MB (for Base64, ensure original file < 10MB)

### asr_options (optional)
- Type: `object`
- Description: ASR-specific configuration
- Note: Pass via `extra_body` when using OpenAI SDK

**Properties:**

#### language
- Type: `string`
- Default: None (auto-detect)
- Description: Specify audio language for better accuracy
- Values: See [languages.md](languages.md) for full list
- Examples: `"zh"`, `"en"`, `"ja"`

#### enable_itn
- Type: `boolean`
- Default: `false`
- Description: Enable Inverse Text Normalization
- Applies to: Chinese and English only
- Effect: Converts spoken numbers/dates to standard format

### stream (optional)
- Type: `boolean`
- Default: `false`
- Description: Enable streaming output
- Values:
  - `false`: Return complete result at once
  - `true`: Stream results as generated

### stream_options (optional)
- Type: `object`
- Description: Streaming configuration
- Only effective when `stream=true`

**Properties:**

#### include_usage
- Type: `boolean`
- Default: `false`
- Description: Include token usage in final chunk

## Response Format

### Non-streaming Response

```json
{
  "choices": [{
    "finish_reason": "stop",
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Transcribed text",
      "annotations": [{
        "type": "audio_info",
        "language": "zh",
        "emotion": "neutral"
      }]
    }
  }],
  "usage": {
    "prompt_tokens": 42,
    "completion_tokens": 12,
    "total_tokens": 54,
    "seconds": 1,
    "prompt_tokens_details": {
      "audio_tokens": 42,
      "text_tokens": 0
    },
    "completion_tokens_details": {
      "text_tokens": 12
    }
  }
}
```

### Streaming Response

Each chunk:
```json
{
  "choices": [{
    "delta": {
      "content": "word",
      "role": "assistant",
      "annotations": [{
        "type": "audio_info",
        "language": "zh",
        "emotion": "neutral"
      }]
    }
  }]
}
```

Final chunk: `data: [DONE]`

## Response Fields

### annotations
- **language**: Detected or specified language code
- **emotion**: Detected emotion
  - Values: `neutral`, `happy`, `sad`, `angry`, `surprised`, `disgusted`, `fearful`
- **type**: Always `"audio_info"`

### usage
- **seconds**: Audio duration in seconds
- **audio_tokens**: Audio length in tokens (25 tokens/second)
- **text_tokens**: Output text length in tokens
- **total_tokens**: Sum of input and output tokens

## Error Handling

Common errors:
- **401 Unauthorized**: Invalid API key
- **400 Bad Request**: Invalid parameters or audio format
- **413 Payload Too Large**: Audio file exceeds 10MB
- **429 Too Many Requests**: Rate limit exceeded

## Examples

### Python with URL
```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

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
            "language": "zh",
            "enable_itn": False
        }
    }
)

print(completion.choices[0].message.content)
```

### Python with Local File
```python
import base64
import pathlib

# Encode file
file_path = pathlib.Path("audio.mp3")
base64_str = base64.b64encode(file_path.read_bytes()).decode()
data_uri = f"data:audio/mpeg;base64,{base64_str}"

# Use in API call
completion = client.chat.completions.create(
    model="qwen3-asr-flash",
    messages=[{
        "role": "user",
        "content": [{
            "type": "input_audio",
            "input_audio": {"data": data_uri}
        }]
    }]
)
```

### Streaming Example
```python
completion = client.chat.completions.create(
    model="qwen3-asr-flash",
    messages=[...],
    stream=True,
    stream_options={"include_usage": True}
)

for chunk in completion:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```
