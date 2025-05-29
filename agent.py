import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

from livekit import agents, api
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    noise_cancellation,
)
from openai.types.beta.realtime.session import TurnDetection, InputAudioTranscription

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

    # Set up recording
    req = api.RoomCompositeEgressRequest(
        room_name=ctx.room.name,
        audio_only=True,
        file_outputs=[api.EncodedFileOutput(
            file_type=api.EncodedFileType.OGG,
            filepath="my-room-test.ogg",
            s3=api.S3Upload(
                bucket="recordings",
                region="eu-west-2",
                endpoint=os.getenv("S3_SUPABASE_ENDPOINT"),
                access_key=os.getenv("S3_ACCESS_KEY_ID"),
                secret=os.getenv("S3_SECRET_ACCESS_KEY"),
                force_path_style=True
            ),
        )],
    )

    lkapi = api.LiveKitAPI()
    await lkapi.egress.start_room_composite_egress(req)

    async def write_transcript():
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")

        # This example writes to the temporary directory, but you can save to any location
        filename = f"transcripts/transcript_{ctx.room.name}_{current_date}.json"

        with open(filename, 'w') as f:
            json.dump(session.history.to_dict(), f, indent=2)

        print(f"Transcript for {ctx.room.name} saved to {filename}")

    ctx.add_shutdown_callback(write_transcript)

    await lkapi.aclose()
    session = AgentSession(
        llm=openai.realtime.RealtimeModel.with_azure(
            voice="shimmer",
            azure_deployment="gpt-4o-realtime-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            turn_detection=TurnDetection(
                type="semantic_vad",
                interrupt_response=True
            ),
            input_audio_transcription=InputAudioTranscription(
                model="gpt-4o-transcribe"
            )
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
