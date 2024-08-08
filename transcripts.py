# -*- coding: utf-8 -*-
import re

def parse_timeline(timeline_file):
  """Parses the timeline.txt file into a dictionary."""
  timeline = {}
  with open(timeline_file, 'r') as f:
    last_stop = 0.0
    for line in f:
      start = last_stop
      start_, stop, speaker = re.findall(r'start=(.*)s stop=(.*)s (.*)', line)[0]
      last_stop = stop
      timeline[int(float(start))] = (int(float(stop)), speaker)
  return timeline

def parse_srt(srt_file):
  """Parses the srt file into a list of subtitles."""
  subtitles = []
  with open(srt_file, 'r') as f:
    lines = f.readlines()
    for i in range(0, len(lines), 4):
      start_time = lines[i + 1].strip().split(' --> ')[0]
      text = lines[i + 2].strip()
      subtitles.append((start_time, text))
  return subtitles

def generate_transcript(timeline, subtitles):
  """Generates the transcript, only outputting speaker name once per turn."""
  transcript = []
  current_speaker = None
  for start_time, text in subtitles:
    # Convert SRT time format to seconds
    h, m, s, ms = map(int, re.split(r'[:,]', start_time))
    seconds = h * 3600 + m * 60 + s + ms / 1000
    
    # Find corresponding speaker in timeline
    speaker_changed = False
    for timeline_start in sorted(timeline.keys()):
      timeline_stop, speaker = timeline[timeline_start]
      if timeline_start <= seconds < timeline_stop:
        speaker = speaker.replace("speaker_", "").replace("_", " ")
        if speaker != current_speaker:
          current_speaker = speaker
          speaker_changed = True
        break

    # Format the transcript line
    if current_speaker:
      if speaker_changed:
        transcript.append(f"😊{current_speaker}({start_time}):\n{text}")
      else:
        transcript.append(f"{text}")
  return transcript

if __name__ == "__main__":
  timeline_file = "timeline.txt"
  srt_file = "bluehat-Forshaw.srt"

  timeline = parse_timeline(timeline_file)
  subtitles = parse_srt(srt_file)
  transcript = generate_transcript(timeline, subtitles)

  with open("transcript1.txt", 'w', encoding="utf8") as f:
    for line in transcript:
      f.write(line + '\n')
      