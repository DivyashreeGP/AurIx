# OpenAI Setup Guide

## Getting Your OpenAI API Key

1. **Visit OpenAI**: https://platform.openai.com/account/api-keys
2. **Sign in** with your OpenAI account
3. **Create a new API key** or use an existing one
4. **Copy the API key** (keep it secure!)

## Setting Up the API Key

### Option 1: Environment Variable (Recommended)
```bash
# Linux/macOS
export OPENAI_API_KEY="your-api-key-here"

# Windows PowerShell
$env:OPENAI_API_KEY = "your-api-key-here"

# Windows Command Prompt
set OPENAI_API_KEY=your-api-key-here
```

### Option 2: .env File
1. Copy `.env.example` to `.env`
2. Edit `.env` and replace `your-api-key-here` with your actual API key

## Backward Compatibility
The code also supports `GEMINI_API_KEY` if you have an older environment setup.

## Testing the Setup

After setting up your API key, run:

```bash
# Test Docker setup
./docker-test.sh

# Or manually test
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello, World!\")"}'
```

## Troubleshooting

- **API Key Invalid**: Double-check your API key from Google AI Studio
- **Quota Exceeded**: Check your Google Cloud billing/quota
- **Network Issues**: Ensure your firewall allows HTTPS connections to Google APIs

## Security Best Practices

- ✅ **Never commit** API keys to version control
- ✅ **Use environment variables** or secure credential management
- ✅ **Rotate keys regularly** for security
- ✅ **Monitor usage** in Google Cloud Console