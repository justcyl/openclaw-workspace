# Supported Languages

Qwen ASR supports 30+ languages. Specify the language code to improve accuracy when the audio language is known.

## Language Codes

| Code | Language | Notes |
|------|----------|-------|
| zh | Chinese | Mandarin, Sichuan dialect, Min Nan, Wu dialect |
| yue | Cantonese | |
| en | English | |
| ja | Japanese | |
| de | German | |
| ko | Korean | |
| ru | Russian | |
| fr | French | |
| pt | Portuguese | |
| ar | Arabic | |
| it | Italian | |
| es | Spanish | |
| hi | Hindi | |
| id | Indonesian | |
| th | Thai | |
| tr | Turkish | |
| uk | Ukrainian | |
| vi | Vietnamese | |
| cs | Czech | |
| da | Danish | |
| fil | Filipino | |
| fi | Finnish | |
| is | Icelandic | |
| ms | Malay | |
| no | Norwegian | |
| pl | Polish | |
| sv | Swedish | |

## Usage

**When to specify language:**
- Audio contains a single known language
- Want to improve recognition accuracy

**When NOT to specify language:**
- Audio language is uncertain
- Audio contains multiple languages (e.g., Chinese-English-Japanese mix)
- Want automatic language detection

## Example

```python
# Specify Chinese for better accuracy
result = transcribe(audio, language="zh")

# Auto-detect language (don't specify)
result = transcribe(audio)
```
