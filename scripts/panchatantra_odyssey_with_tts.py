import asyncio
import os
import subprocess
from pathlib import Path

import aiohttp
from openai import OpenAI
from odyssey import Odyssey

from dotenv import load_dotenv


# --------- Config you can tweak ----------
VOICE = "coral"                 # e.g. alloy, coral, nova, verse... :contentReference[oaicite:2]{index=2}
TTS_MODEL = "gpt-4o-mini-tts"   # OpenAI TTS model :contentReference[oaicite:3]{index=3}
POLL_SECONDS = 5
# ----------------------------------------

load_dotenv()


def ensure_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"Missing {name}. Set it like: export {name}='...'")
    return val


async def download_file(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            with out_path.open("wb") as f:
                async for chunk in resp.content.iter_chunked(1024 * 256):
                    f.write(chunk)


def make_tts_mp3(text: str, out_path: Path) -> None:
    """
    Generate MP3 narration using OpenAI TTS.
    Uses the Audio Speech endpoint via the OpenAI Python SDK. :contentReference[oaicite:4]{index=4}
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    client = OpenAI()  # reads OPENAI_API_KEY from env
    # Streaming-to-file style shown in OpenAI docs :contentReference[oaicite:5]{index=5}
    with client.audio.speech.with_streaming_response.create(
        model=TTS_MODEL,
        voice=VOICE,
        input=text,
        instructions="Narrate like a warm storyteller. Clear, expressive, child-friendly pacing.",
    ) as response:
        response.stream_to_file(out_path)


def mux_video_audio(video_path: Path, audio_path: Path, out_path: Path) -> None:
    """
    Merge audio into the mp4. Requires ffmpeg installed.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(out_path),
    ]
    subprocess.run(cmd, check=True)


async def run_odyssey_story() -> str:
    """
    Runs the Panchatantra-style simulation and returns the recording video_url.
    """
    ody_key = ensure_env("ODYSSEY_API_KEY")
    client = Odyssey(api_key=ody_key)

    # Short narration that matches the visuals.
    # You can expand/adjust this to match your script timing.
    story_narration = (
        # "In an old village, a man bought a goat at the market and carried it home proudly. "
        # "On the road, a sly stranger laughed and said, 'Why are you carrying a dog?' "
        # "Soon another man said the same, and then a third—each mocking him. "
        # "The man began to doubt his own eyes. Embarrassed and afraid, he dropped the goat and ran away. "
        # "The tricksters laughed together, took the goat, and prepared a feast. "
        # "The moral: trust your own judgment, and be careful of repeated deception."

        "In an old village, a man bought a goat and carried it home proudly. "
        "On the road, a stranger laughed and said, 'Why are you carrying a dog?' "
        "Soon another man said the same, and then a third joined in. "
        "Hearing the same lie again and again, the man began to doubt his own eyes. "
        "Embarrassed and afraid, he dropped the goat and ran away. "
        "As the man disappeared, the tricksters burst into laughter behind his back. "
        "Delighted by their deception, they took the goat for themselves. " 
        "That evening, they gathered around a fire, cooked the goat, and celebrated with a feast. "

        "The moral is clear: "
        "Never abandon your own judgment just because many people repeat the same lie. "
    )

    try:
        job = await client.simulate(
            # script=[
            #     {"timestamp_ms": 0, "start": {"prompt": "Ancient Indian village market. A humble man buys a healthy white goat and carries it on his shoulders. Warm sunlight, rural setting, cinematic realism."}},
            #     {"timestamp_ms": 3500, "interact": {"prompt": "A cunning man approaches, pointing and laughing, insisting the man is carrying a dog, not a goat. The carrier looks briefly confused but keeps walking."}},
            #     {"timestamp_ms": 7000, "interact": {"prompt": "A second trickster blocks the path, mocking loudly: 'That’s a dog!' The man’s confidence wavers; he looks down at the animal, uncertain."}},
            #     {"timestamp_ms": 10500, "interact": {"prompt": "A third trickster joins in, shaming the man for carrying a dog. The man grows anxious and embarrassed, sweating, looking around."}},
            #     {"timestamp_ms": 14000, "interact": {"prompt": "Overwhelmed, the man drops the goat and runs away down the dusty road."}},
            #     {"timestamp_ms": 17500, "interact": {"prompt": "The three tricksters grin, seize the goat, and celebrate around a cooking fire, preparing a feast, laughing together."}},
            #     {"timestamp_ms": 21000, "end": {}},
            # ],
            script=[
                # Scene 1 — Market
                {
                    "timestamp_ms": 0,
                    "start": {
                        "prompt": (
                            "Ancient Indian village market. "
                            "A humble villager buys a healthy white goat "
                            "and carries it proudly on his shoulders."
                        )
                    }
                },

                # Scene 2 — First deception
                {
                    "timestamp_ms": 3500,
                    "interact": {
                        "prompt": (
                            "A cunning man approaches, laughing and saying "
                            "the villager is carrying a dog, not a goat."
                        )
                    }
                },

                # Scene 3 — Second deception
                {
                    "timestamp_ms": 7000,
                    "interact": {
                        "prompt": (
                            "Another man mocks the villager, loudly insisting "
                            "that the animal is clearly a dog."
                        )
                    }
                },

                # Scene 4 — Third deception
                {
                    "timestamp_ms": 10500,
                    "interact": {
                        "prompt": (
                            "A third trickster shames the villager publicly, "
                            "making him doubt himself."
                        )
                    }
                },

                # Scene 5 — Man abandons goat
                {
                    "timestamp_ms": 14000,
                    "interact": {
                        "prompt": (
                            "Confused, embarrassed, and afraid, "
                            "the villager drops the goat and runs away."
                        )
                    }
                },

                # NEW Scene 6 — Tricksters laugh
                {
                    "timestamp_ms": 17500,
                    "interact": {
                        "prompt": (
                            "The three tricksters burst into laughter behind the man's back, "
                            "pointing and celebrating their success."
                        )
                    }
                },

                # NEW Scene 7 — Feast
                {
                    "timestamp_ms": 21000,
                    "interact": {
                        "prompt": (
                            "Later that evening, the tricksters sit together around a fire, "
                            "roasting the goat and enjoying a feast under the night sky."
                        )
                    }
                },

                # End
                {
                    "timestamp_ms": 25000,
                    "end": {}
                }
            ],
            portrait=False,
        )

        print(f"Simulation started: {job.job_id}")

        # Poll for completion
        while True:
            status = await client.get_simulate_status(job.job_id)

            if status.status == "completed":
                # Take the first stream’s recording
                stream_id = status.streams[0].stream_id
                recording = await client.get_recording(stream_id)
                print("Odyssey video URL:", recording.video_url)

                # Also return narration so we can TTS it
                return recording.video_url, story_narration

            if status.status == "failed":
                raise RuntimeError(f"Simulation failed: {status.error_message}")

            if status.status == "cancelled":
                raise RuntimeError("Simulation cancelled")

            await asyncio.sleep(POLL_SECONDS)
    finally:
        # Prevent aiohttp unclosed-session warnings (as you saw earlier)
        if hasattr(client, "disconnect"):
            await client.disconnect()
        elif hasattr(client, "close"):
            await client.close()


async def main():
    ensure_env("OPENAI_API_KEY")  # OpenAI key location guidance: API Keys page :contentReference[oaicite:6]{index=6}

    video_url, narration_text = await run_odyssey_story()

    out_dir = Path("outputs")
    raw_video = out_dir / "odyssey.mp4"
    narration_mp3 = out_dir / "narration.mp3"
    final_video = out_dir / "final_with_audio.mp4"

    print("\nDownloading video...")
    await download_file(video_url, raw_video)
    print(f"Saved: {raw_video}")

    print("\nGenerating narration (OpenAI TTS)...")
    make_tts_mp3(narration_text, narration_mp3)
    print(f"Saved: {narration_mp3}")

    print("\nMuxing audio + video with ffmpeg...")
    mux_video_audio(raw_video, narration_mp3, final_video)
    print(f"\n✅ Done! Final video: {final_video.resolve()}")


if __name__ == "__main__":
    asyncio.run(main())
