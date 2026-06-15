# whisperx-research-transcription-pipeline

An end-to-end transcription and speaker diarization pipeline built 
for qualitative researchers working with interview audio. Developed 
and maintained at the **Scrolling Society Lab (sLab)** at McGill 
University as part of a multidisciplinary research program studying 
digital media behavior on TikTok and Instagram Reels, funded by the 
Social Sciences and Humanities Research Council of Canada (SSHRC).

This pipeline takes raw interview audio files and produces clean, 
speaker-labeled transcripts ready for qualitative coding in MAXQDA 
or similar software — with no manual transcription required.

---

## Why This Exists

The lab had accumulated a large archive of interview audio across 
dozens of research sessions, and our transcription process hadn't 
kept pace. Commercial transcription services were expensive and sent 
audio to external servers — a non-starter under our Research Ethics 
Board (REB) protocols for a program working with sensitive participant 
interviews. We needed something fast, accurate, locally run, and free.

After evaluating available options against our data safety 
constraints, I landed on WhisperX — an open-source, locally run LLM 
transcription and diarization tool that processes everything on-device, 
never sending audio to external servers.

Getting it working in a research environment required significant 
iteration: configuring diarization separately for Windows and Mac, 
optimizing compute settings for CPU-only lab hardware (the default 
float16 compute type assumes GPU access we didn't have), selecting 
the right model size by repeatedly weighing transcription accuracy 
against processing time, and building a post-processing step to 
convert the raw diarized output into something actually usable for 
qualitative coding. The three-stage output comparison below shows 
what that iteration produced.

---

## What It Does

**Stage 1 → Stage 2: WhisperX** transcribes and diarizes audio 
files (`.m4a`, `.mp3`, `.wav`, etc.), producing timestamped `.srt` 
subtitle files with automatic speaker labels (`[SPEAKER_00]`, 
`[SPEAKER_01]`, etc.)

**Stage 2 → Stage 3: `srt2txt_v2.py`** converts the raw diarized 
`.srt` output into a clean, readable transcript by:
- Merging consecutive subtitle entries from the same speaker into 
  continuous turns
- Collapsing fragmented breath-by-breath entries into full 
  speaker turns with single timestamps
- Outputting either plain `.txt` or formatted Markdown 
  (via `--md` flag)

---

## Pipeline Overview

```
Audio file (.m4a / .mp3 / .wav)
        ↓
   [WhisperX — no diarization]        ← Stage 1
   Raw transcription, manual 
   speaker labels, fragmented
        ↓
   [WhisperX — with diarization]      ← Stage 2
   Automatic speaker detection,
   still fragmented per breath
        ↓
   Raw .srt file
        ↓
   [srt2txt_v2.py]                    ← Stage 3
   Merges speaker turns
   Cleans formatting
        ↓
   Readable transcript (.txt or .md)
        ↓
   Ready for MAXQDA / qualitative coding
```

---

## Pipeline Stages & Output Comparison

The pipeline went through three stages of development, each solving 
a specific problem with the previous output.

---

### Stage 1 — Raw WhisperX (no diarization)

The initial WhisperX output without diarization requires manual 
speaker labeling and produces fragmented entries — one per breath, 
not usable for qualitative coding without significant cleanup:

```
[00:00:00.000 --> 00:00:07.680]   Yeah, that's great. That's a 
great idea. So usually, I'm going to tell you a little bit more

[00:00:07.680 --> 00:00:14.800]   of what we're going to do 
today soon, but usually I start these interviews kind of like 
by asking,

[00:00:14.800 --> 00:00:20.000]   what do you think this research 
is about? Like, what do you think we're doing here?

[00:00:20.000 --> 00:00:27.760]   So what I understood from 
like the email I got and like what I understood like online 
when I registered was it was to focus on like what are we 
focusing on when we're looking at TikTok videos?
```

**Problems:** Speaker labels must be added manually after the fact. 
Every breath is a separate entry. A single speaker turn spanning 
30 seconds becomes 6+ separate lines. Not usable for MAXQDA import.

---

### Stage 2 — WhisperX with Diarization

Adding `--diarize` enables automatic speaker identification — but 
the fragmentation is severe, splitting individual sentences into 
multiple entries:

```
00:00.650 --> 00:01.330
[SPEAKER_01]: Yeah, that's great.

00:01.370 --> 00:02.231
[SPEAKER_01]: That's a great idea.

00:02.772 --> 00:09.879
[SPEAKER_01]: So usually, I'm going to tell you a little bit 
more of what we're going to do today soon.

00:10.280 --> 00:18.328
[SPEAKER_01]: But usually, I started these interviews kind of 
like by asking, what do you think this research is about?

00:18.608 --> 00:20.110
[SPEAKER_01]: Like, what do you think we're doing here?

00:21.833 --> 00:35.179
[SPEAKER_00]: um so what i understood from like the the email 
i got and like what i understood like online when i registered 
was it was to um focus on like what are what the i move what

00:35.646 --> 00:38.527
[SPEAKER_00]: wait, what are we focusing on when we're looking 
at TikTok videos?

00:38.967 --> 00:41.328
[SPEAKER_00]: Like are we staring at the captions?
```

**Problems:** Automatic speaker detection works, but a single 
speaker turn spanning 20 seconds is split into 8+ separate 
entries. A full interview produces hundreds of fragments. 
Completely unusable for turn-by-turn qualitative coding.

Getting diarization running on Mac required additional 
configuration beyond the standard Windows setup — separate 
environment dependencies and execution paths that had to be 
worked out independently.

---

### Stage 3 — After srt2txt_v2.py Post-Processing

Running the diarized `.srt` through `srt2txt_v2.py` merges all 
consecutive entries from the same speaker into a single continuous 
turn, producing a clean, researcher-readable transcript:

```
00:00.650 --> 00:20.110
[SPEAKER]: Yeah, that's great. That's a great idea. So usually, 
I'm going to tell you a little bit more of what we're going to 
do today soon. But usually, I started these interviews kind of 
like by asking, what do you think this research is about? Like, 
what do you think we're doing here?

00:21.833 --> 00:53.432
[P]: So what I understood from the email I got and online 
when I registered was it was to focus on what are we focusing 
on when we're looking at TikTok videos? Like are we staring at 
the captions? Are we staring at people's faces? And probably 
how long it takes before we scroll to another video, depending 
on what we see, I guess.

01:46.992 --> 02:28.102
[P]: So I actually struggle with social media a lot, 
especially during the pandemic. I would argue I had an 
addiction to a point where I would stay up until like 6am 
watching TikToks and then I would nap and then I would go to 
school or go to work or whatever. I would delete it because it 
was a problem and then I would reinstall it when I was like, 
oh, I can control the problem. But then obviously I couldn't.
```

**Result:** Full speaker turns, merged timestamps, named speakers, 
ready for MAXQDA qualitative coding import. What was hundreds of 
fragments becomes a clean, turn-by-turn transcript.

See [`examples/`](./examples/) for complete anonymized before/after 
files from a real research session showing all three stages.

---

## Files

| File | Description |
|------|-------------|
| `srt2txt_v2.py` | Python script: converts diarized `.srt` to readable transcript |
| `transcribe-queue.ps1` | PowerShell script: batch-transcribes all files in AUDIOS folder |
| `examples/` | Anonymized three-stage output from a real research session |
| `docs/TRANSCRIPTION_GUIDE.pdf` | Full step-by-step tutorial for non-technical users |

---

## Requirements

### WhisperX
Install WhisperX following the 
[official instructions](https://github.com/m-bain/whisperX).

You will need:
- Python 3.8+
- A Hugging Face account and access token (required for speaker 
  diarization — create one at [huggingface.co](https://huggingface.co))
- A CUDA-compatible GPU is recommended but not required — see 
  Configuration Notes below for CPU optimization

### srt2txt_v2.py
```bash
pip install attrbox
```

---

## Setup

### 1. Organize your folders

Create two folders on your Desktop:
- **`AUDIOS`** — place audio files to transcribe here. Make sure 
  only the files you want to process in the current session are 
  in this folder.
- **`TRANSCRIPTION`** — keep this script, `srt2txt_v2.py`, 
  `transcribe-queue.ps1`, and your WhisperX setup here.

### 2. Open terminal in the TRANSCRIPTION folder

Right-click the `TRANSCRIPTION` folder → **Open in Terminal**

### 3. Build the virtual environment

```powershell
python -m venv whisperx-env
```

### 4. Activate the virtual environment

```powershell
.\whisperx-env\Scripts\activate
```

> **If you get a permissions error on activation:**
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
> ```
> Respond `Y` when prompted, then retry:
> ```powershell
> .\whisperx-env\Scripts\activate
> ```
> 
> **If the error persists after the bypass command:**
> 1. Exit the terminal
> 2. Search for **PowerShell** in the Windows start menu
> 3. **Right-click → Run as Administrator**
> 4. Navigate back to the TRANSCRIPTION folder and retry 
>    steps 3–4

When activation succeeds, you will see `(whisperx-env)` at the 
start of your terminal prompt.

---

## Running the Pipeline

### Stage 1 & 2: Transcribe with WhisperX

**Option A — Auto-transcribe all files in AUDIOS folder 
(recommended):**
```powershell
.\transcribe-queue.ps1
```
The script loops through every audio file in your AUDIOS folder 
and runs the full WhisperX diarization pipeline on each one.

**Option B — Transcribe a single file manually:**
```powershell
whisperx --diarize "C:\path\to\your\audiofile.m4a" `
  --model medium.en `
  --output_dir "C:\Users\YourName\Desktop\TRANSCRIPTION" `
  --language en `
  --hf YOUR_HUGGINGFACE_TOKEN `
  --compute_type int8 `
  --print_progress True `
  --min_speakers 1 `
  --max_speakers 8
```

Replace:
- `"C:\path\to\your\audiofile.m4a"` with the actual file path
- `YOUR_HUGGINGFACE_TOKEN` with your token from huggingface.co
- `C:\Users\YourName\Desktop\TRANSCRIPTION` with your actual 
  TRANSCRIPTION folder path
- `--min_speakers` and `--max_speakers` to match your interview 
  format (use `--max_speakers 2` for standard 1-on-1 interviews)

---

### Stage 3: Convert .srt to readable transcript

Once WhisperX finishes, it produces a `.srt` file in your 
TRANSCRIPTION folder. Run `srt2txt_v2.py` on it:

```powershell
python srt2txt_v2.py -i "filepath.srt" -o newfilename.txt
```

**Full command example:**
```powershell
python srt2txt_v2.py -i "C:\Users\YourName\Desktop\TRANSCRIPTION\P_INTERVIEW.srt" -o P_transcript.txt
```

**Options:**
| Flag | Description |
|------|-------------|
| `-i FILE` | Input `.srt` file path (required) |
| `-o FILE` | Output filename (default: `output.txt`) |
| `--md` | Output as Markdown with bold speaker labels |

Open the resulting `.txt` file, copy the content, and paste into 
a new Word document on OneDrive for archiving and coding.

---

## Configuration Notes

### Compute type
The default WhisperX compute type is `float16`, which requires a 
CUDA-compatible GPU. On CPU-only machines, this will either fail 
or run prohibitively slowly. Use `int8` instead:

```
--compute_type int8
```

This significantly reduces processing time on standard lab 
hardware with minimal impact on transcription accuracy for 
spoken interview audio. Shifting from `float16` to `int8` was 
the single most impactful optimization for making this pipeline 
usable on the lab's computers.

### Model selection
WhisperX offers several model sizes. For research interview 
audio in English, `medium.en` provides the best balance of 
accuracy and processing speed on CPU hardware. Testing 
progression:

| Model | Accuracy | CPU Speed | Verdict |
|-------|----------|-----------|---------|
| `small.en` | Lower | Fast | Missed too much |
| `medium.en` | Good | Manageable | ✓ Best for CPU |
| `large-v2` | Best | Very slow | Impractical without GPU |

### Speaker count
Set `--min_speakers` and `--max_speakers` to match your 
interview format:
- Standard 1-on-1 interview: `--min_speakers 1 --max_speakers 2`
- Group interview or focus group: adjust `--max_speakers` 
  accordingly

Getting these values wrong degrades diarization quality — if 
the model is told to expect 8 speakers but there are only 2, 
it will hallucinate speaker splits within single turns.

### Mac setup
Diarization configuration on Mac requires different environment 
setup than Windows. 
See [`docs/TRANSCRIPTION_GUIDE.pdf`](./docs/TRANSCRIPTION_GUIDE.pdf)
 Mac Workflow OR visit https://github.com/ggml-org/whisper.cpp to download a
Mac-compatible whisper


---

## Research Context

This pipeline was built for the **Scrolling Society Lab (sLab)** 
at McGill University (PI: Samuele Collu), as part of a 
multidisciplinary research program on binge-scrolling behavior 
on TikTok and Instagram Reels. 

Interview data processed through this pipeline contributed to 
qualitative coding across 50+ research sessions and supported 
a peer-reviewed publication:

> Collu Samuele, Neal Lonergan, Lauren Frasca, Livia Ion, 
> Elliot Durkee, Mina Mahdi, Zahara Mustin, Hadrien Velde. 
> "No Life, No Death, No End, No Nothing: Just Feed." 
> *Lo Squaderno. Explorations in Space and Society*, 
> no. 71 (July 2025).

---

## Attribution & Adaptation

`srt2txt_v2.py` is adapted from a GitHub Gist by 
[metaist](https://gist.github.com/metaist/b10433ccc6795d4ed82ef42e0b70a209), 
which converts WhisperX-compatible `.srt` subtitle files into 
readable transcripts with speaker-turn merging.

The original script was already well-suited to the core task. 
The modification made for this pipeline was in the `__iadd__` 
method, which controls how consecutive subtitle entries from the 
same speaker are joined when merging turns. The original joins 
them with a newline character (`"\n"`); this version joins them 
with `". "` instead, producing cleaner sentence-level flow in 
the output transcript and reducing manual cleanup before 
qualitative coding in MAXQDA.

This change was identified as necessary after comparing raw 
merged output against what researchers actually needed for 
coding — a small but deliberate modification to fit a specific 
research workflow.

---

## Full Tutorial

See [`docs/TRANSCRIPTION_GUIDE.pdf`](./docs/TRANSCRIPTION_GUIDE.pdf) 
for the complete step-by-step walkthrough written for non-technical research assistants.

---

## Author

**Neal Lonergan**  
Mixed-Methods Research, Scrolling Society Lab, McGill University  
NealLonergan@gmail.com  
[GitHub](https://github.com/neallonergan)
