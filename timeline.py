# !pip install -q git+https://github.com/openai/whisper.git > /dev/null
# !pip install -q git+https://github.com/pyannote/pyannote-audio > /dev/null

from pyannote.audio import Pipeline
import os
token = os.getenv("HF_TOKEN", "")
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=token)

# send pipeline to GPU (when available)
import torch
pipeline.to(torch.device("cuda"))

# apply pretrained pipeline
diarization = pipeline("audio.wav")

# print the result
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
