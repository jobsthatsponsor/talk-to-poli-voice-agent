import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

from google.genai.types import AudioTranscriptionConfig
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    # openai,
    google,
    noise_cancellation,
)

# from openai.types.beta.realtime.session import TurnDetection, InputAudioTranscription
from supabase import create_client, Client


load_dotenv()


def read_instructions():
    """Read instructions from instructions.md file."""
    instructions_path = Path(__file__).parent / "instructions.md"

    if not instructions_path.exists():
        print(f"Warning: instructions.md not found at {instructions_path}")
        return "You are a helpful voice AI assistant."

    try:
        with open(instructions_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading instructions.md: {e}")
        return "You are a helpful voice AI assistant."


class Assistant(Agent):
    def __init__(self) -> None:
        instructions = read_instructions()
        super().__init__(instructions=instructions)


async def entrypoint(ctx: agents.JobContext):

    async def write_transcript():
        # Initialise Supabase client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")

        supabase: Client = create_client(url, key)

        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcript_{ctx.room.name}_{current_date}.json"

        # Convert transcript to JSON bytes
        transcript_data = json.dumps(session.history.to_dict(), indent=2).encode('utf-8')

        # Upload to Supabase storage
        try:
            supabase.storage.from_("transcripts").upload(
                file=transcript_data,
                path=filename,
                file_options={"content-type": "application/json", "upsert": "false"}
            )
            print(f"Transcript for {ctx.room.name} saved to Supabase: {filename}")
        except Exception as e:
            print(f"Error uploading transcript: {e}")
            raise Exception(f"Failed to upload transcript: {e}")

    ctx.add_shutdown_callback(write_transcript)

    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel.with_azure(
    #         voice="shimmer",
    #         azure_deployment="gpt-4o-realtime-preview",
    #         azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    #         api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    #         api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    #         turn_detection=TurnDetection(
    #             type="server_vad",
    #             threshold=0.5,
    #             silence_duration_ms=1000,
    #             interrupt_response=True
    #         ),
    #         input_audio_transcription=InputAudioTranscription(
    #             model="gpt-4o-transcribe"
    #         )
    #     )
    # )

    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            api_key=str(os.getenv("GOOGLE_API_KEY")),
            model="gemini-2.5-flash-preview-native-audio-dialog",
            voice="Erinome",
            input_audio_transcription=AudioTranscriptionConfig(),
            output_audio_transcription=AudioTranscriptionConfig(),

            # These are still not working despite being available in the plugin (keeping for future use)
            # enable_affective_dialog=True,
            # proactivity=True
        )
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions="Greet the user warmly as Poli, introduce yourself briefly as a recruiter helping people find visa-sponsored jobs in the UK, and ask how you can help them with their job search today. Keep it concise and conversational."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
