# Examples

Three-stage output from a real (anonymized) research interview 
processed through the full pipeline. Participant identifying 
details have been removed.

**`01_raw_whisperx_output.txt`** — Raw WhisperX output without 
diarization. Speaker labels manually coded, fragmented per 
breath, not suitable for qualitative coding.

**`02_diarized_whisperx_output.txt`** — WhisperX output with 
diarization enabled. Automatic speaker detection works but 
fragmentation is severe — single turns split into dozens of 
entries.

**`03_srt2txt_v2_processed.txt`** — Final output after running 
`srt2txt_v2.py`. Continuous speaker turns, merged timestamps, 
named speakers. Ready for MAXQDA import.

The progression from 01 → 03 shows the full problem this 
pipeline was built to solve.
