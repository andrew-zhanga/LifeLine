# FlareWise narrated three-minute video

Open **FlareWise-3-minute-demo.mp4**. 1920×1080, 30 fps, H.264/AAC; duration 2:59.97. Narration uses Microsoft Andrew Multilingual Neural TTS, replacing the original macOS Samantha voice. This is an edited pitch video combining actual interface screenshots, a 30-second live WebGL recording, and sourced problem/scale cards. It is not a continuous recording of every mouse click.

## Rubric-aligned sequence

- 0:00–0:40: economic waste, Eagle Ford health association and the investment problem.
- 0:40–1:25: real portfolios, stakeholder priorities and the Financial/Balanced/Community trade-off.
- 1:25–2:15: working transport footage, trained segmentation results and technical proof.
- 2:15–3:00: TotalEnergies relevance, proposed pilot, measurable outcomes and scale vision.

Final narration: `../three-minute-script.md`. Research and rubric mapping: `../rubric-and-sources.md`. Optional SRT uses approximate sentence timing; the spoken MP4 is the primary deliverable.

The guide was read in full, with pages 3 and 6 visually checked. Public statistics were verified against the World Bank 2026 report, the original Eagle Ford health study and TotalEnergies' published flaring commitments. The global statistics cover 2025; application inventory and weather retain their separately labeled historical periods.

## Production and verification

Native macOS screen recording was unavailable. The real application WebGL canvas was recorded through browser `captureStream(30)` and `MediaRecorder`, while transport playback and the capture toggle were operated through the UI. Raw `flarewise-scene.webm` is retained locally; no operating-system desktop recording or private tabs are included. Interface stills are from the verified browser walkthrough. Model outputs and numeric values were not altered for the video.

`verification.json` records the output hash and full decode validation. Sampled final frames at 5, 18, 64, 74, 99, 108, 122, 155 and 173 seconds were extracted; representative title, portfolio, moving-scene and closing frames were visually reviewed. Audio is stereo 48 kHz. The voice refresh preserves the encoded video stream exactly; the stream hash and chapter timing adjustments are recorded in verification.json.

## Rebuild locally

Install `scripts/video/requirements.txt` in the data environment. On macOS run `scripts/prepare_demo_narration.py`, then `scripts/make_demo_video.py`, followed by `scripts/refresh_demo_voice.py` to apply the final neural voice. The refresh uses Microsoft speech synthesis through edge-tts and preserves the video bitstream. Intermediate cards, narration and clips are ignored; final MP4/SRT and metadata are committed.

To recapture moving footage, temporarily serve `scripts/video/record-scene.html` from the demo's public directory. Open it in Chrome, enter Simulation workbench, play Transport, and click Record. Toggle capture about 21 seconds into recording. Download the WebM after 50 seconds and save it here as `flarewise-scene.webm`. Remove the temporary public utility after use. The build extracts seconds 5–35. The utility is kept outside the application deployment.
