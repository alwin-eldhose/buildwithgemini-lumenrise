import math
import os
import struct
import uuid
import wave
from google.cloud import storage

BUCKET_NAME = os.environ.get(
    "MEDIA_BUCKET_NAME", "lumenrise-media-qwiklabs-gcp-03-c47843160c69"
)


def generate_morning_audio(theme: str = "peaceful sunrise") -> str:
    """Generates ambient acoustic morning chimes audio and uploads it to Google Cloud Storage.

    Args:
        theme: Theme or mood for the audio chimes (e.g., 'peaceful sunrise', 'gentle rain', 'energizing dawn').

    Returns:
        A public HTTPS URL pointing to the uploaded WAV audio file.
    """
    sample_rate = 22050
    duration_sec = 4.5
    num_samples = int(sample_rate * duration_sec)

    # Peaceful pentatonic chime frequencies (C4, E4, G4, B4, D5)
    freqs = [261.63, 329.63, 392.00, 493.88, 587.33]
    chime_starts = [0.0, 0.6, 1.2, 1.8, 2.4]

    samples = [0.0] * num_samples

    for start_t, f in zip(chime_starts, freqs):
        start_idx = int(start_t * sample_rate)
        for i in range(start_idx, num_samples):
            t = (i - start_idx) / sample_rate
            envelope = math.exp(-2.5 * t)
            val = (
                math.sin(2 * math.pi * f * t)
                + 0.3 * math.sin(2 * math.pi * f * 2 * t)
            ) * envelope
            samples[i] += val * 0.25

    max_val = max(abs(s) for s in samples) or 1.0
    packed = bytearray()
    for s in samples:
        norm = int((s / max_val) * 28000)
        norm = max(-32768, min(32767, norm))
        packed.extend(struct.pack("<h", norm))

    filename = f"morning_chimes_{uuid.uuid4().hex[:8]}.wav"
    local_path = f"/tmp/{filename}"

    with wave.open(local_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(packed)

    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_filename(local_path, content_type="audio/wav")
        if os.path.exists(local_path):
            os.remove(local_path)
        return f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    except Exception as e:
        if os.path.exists(local_path):
            os.remove(local_path)
        raise RuntimeError(f"Failed to upload audio to Cloud Storage: {e}")
