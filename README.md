# Talk to Poli Voice Agent

A real-time speech-to-speech AI agent built with LiveKit and Azure OpenAI, part of the Talk to Poli ecosystem.

## Overview

This voice agent provides natural conversation capabilities using:
- **LiveKit** for real-time audio streaming and room management
- **Azure OpenAI GPT-4o Realtime** for speech-to-speech AI interactions
- **Enhanced noise cancellation** for clear audio quality
- **Coral voice model** for natural-sounding responses

## Features

- Real-time speech-to-speech conversations
- Azure OpenAI integration with GPT-4o Realtime Preview
- LiveKit Cloud enhanced noise cancellation
- Automatic greeting and assistance offering
- Scalable agent architecture

## Prerequisites

- Python 3.8+
- Azure OpenAI account with GPT-4o Realtime Preview access
- LiveKit Cloud account (or self-hosted LiveKit server)

## Environment Variables

Create a `.env` file with the following variables:

```env
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_API_VERSION=your_api_version
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jobsthatsponsor/talk-to-poli-voice-agent.git
cd talk-to-poli-voice-agent
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install livekit-agents livekit-plugins-openai python-dotenv
```

## Usage

Run the voice agent:

```bash
python agent.py
```

The agent will:
1. Connect to your LiveKit room
2. Initialize the Azure OpenAI realtime model
3. Greet users and offer assistance
4. Engage in real-time voice conversations

## Configuration

### Voice Model
Currently configured to use the "coral" voice. You can modify this in `agent.py`:

```python
llm=openai.realtime.RealtimeModel.with_azure(
    voice="coral",  # Change to: alloy, echo, fable, onyx, nova, shimmer
    # ... other config
)
```

### Noise Cancellation
For self-hosted deployments, remove the noise cancellation parameter:

```python
room_input_options=RoomInputOptions()  # Remove noise_cancellation parameter
```

For telephony applications, use:
```python
noise_cancellation=noise_cancellation.BVCTelephony()
```

## Development

### Project Structure
```
talk-to-poli-voice-agent/
├── agent.py              # Main agent implementation
├── .env                  # Environment variables (not tracked)
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Commit using conventional commits: `git commit -m "feat: add new feature"`
5. Push to your branch: `git push origin feature/your-feature-name`
6. Create a Pull Request

## Talk to Poli Ecosystem

This voice agent is part of the broader Talk to Poli product suite. For more information about the complete platform, visit the main Talk to Poli repository.

## License

This project is part of the Talk to Poli ecosystem. Please refer to the main project licence for terms and conditions.

## Support

For issues and questions:
- Create an issue in this repository
- Contact the Talk to Poli development team
- Check the LiveKit documentation for platform-specific issues