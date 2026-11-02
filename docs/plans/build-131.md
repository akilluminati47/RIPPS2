# Build 131: Pass A, the video player (plan, 2026-11-02)

The user's notes (11/02):
- "Watching movie test noticed pause has the old in game menu audio stutter make it mute and freeze on the same
  frame for resume"
- "Also end of videos need a stutter fix"

## What the code does now (elf/libsmslite/src/smslite.c)

- **Pause.** `smsLitePause(1)` sets `s_smsLitePaused`. The picture side is right: `smsLitePlaybackShowFrame` holds the
  last frame and redraws it under the overlays. The sound side is two problems:
  1. `smsLiteAudioRenderThread` checks the flag only between calls to `smsLiteAudioDrain`, and one call empties the
     whole decoded ring (256 KB, about 1.4 s at 48 kHz stereo). Sound carries on after the press.
  2. Then nothing more is sent, and audsrv, run dry, keeps repeating what it holds: the stutter. sound.c already
     says so for the menu music (the "audio stutters when a game launches" note above `bgmMute`), and build 102
     fixed the music's version by feeding silence (`bgmFeedSilence`).
- **End of a video.** The same dry run happens after the last piece of sound: the render thread finishes, the threads
  are deleted, and audsrv repeats its tail until `smsLitePlaybackClose` calls `audsrv_stop_audio`. A Back or Select
  stop drops the queued sound and leaves the same repeat.
- **End of a video, the picture.** Frames wait on the sound clock (`audioTimeMs`) while a frame is more than 80 ms
  ahead of it, up to 200 vsyncs each. When the sound ends a little before the picture, the clock stops and every
  last frame waits the full 200 vsyncs (3.3 s on NTSC): the end steps instead of playing.

## The change

1. **Pause goes silent on the held frame.**
   - `smsLiteAudioDrain` sends one piece at a time and stops between pieces when paused.
   - On pause the render thread (the only thread that talks to audsrv, so no competing RPC, the race behind the
     old exit hang) fades the piece it is sending to 0 with the existing gain ramp (`smsLiteApplyGain`, about a
     tenth of a second), then keeps audsrv fed with silence while paused, as the menu music does. Silence is not
     counted in `audioBytesOut`, so the sound clock and the picture stay where they stopped.
   - On resume the gain ramps up from 0 (no click), and the picture goes on from the held frame.
2. **A clean end.** After the last piece (and on Back / Select) the render thread fades the tail to 0 and sends
   about 150 ms of silence, so audsrv plays out into zeros before `audsrv_stop_audio`.
3. **The last frames play at their own pace.** Once the sound has ended (`audioRenderDone`), frames stop waiting on
   its clock and fall back to the frame-time pacing the player already has for files with no sound.
4. **L1 / R1 skips** go through `smsLiteRestartAt`, which drops the sound too: check in the lab whether a skip
   repeats a tail; if it does, the same silence goes there.

Nothing on the RIPPS2 side changes (ripps2media.c's pad thread already calls `smsLitePause`).

## Lab, then CI, then push

PCSX2 takes with the capture on (`rec`, then `wait:8` before the end, see memory), NTSC, the lab disk's MEDIA:
- Betty Boop: pause at about 20 s for 4 s, resume. Measure the captured sound: during the pause near zero and no
  repeated block (the repeat shows as a strong self-match at the block's length); no click at resume; the picture
  is one frame through the pause.
- Betty Boop to its end, and a Media Studio phone clip to its end: no repeat after the last sound, the last frames
  step at the film's rate, the display goes back.
- Back in the middle of a film: silence until the browser is back.
- L1 / R1 in the 2 h 41 film (item 4).
- Then CI (build + host tests), push to main. Release and Discord only on the user's word.

## Lab results (11/02, PCSX2, NTSC, CI run 41501662858 for 0bae410; build 130 = the v1.3.0-beta ELF)

Captures in `B:\Videos - Projects\.montages\hyperframes\ripps2-recap\clips\p13?_*.mp4`, sound measured per 100 ms:
- **Pause, Betty Boop** (Cross at 5 s, again at 10 s): 130 plays on to 6.5 s, then a flat -31 dB repeat to 10.7 s.
  131: sound to silence (-180 dB) by 5.7 s, the frame held from 5.5 s, sound back at 10.8 s with the picture.
- **End, AVI00011** (sound 0.14 s shorter than the picture): 130 repeats a block at -33 dB for 4 s and the last
  frames jump in at 6.5 s. 131: silence at 2.7 s, the last frames on time.
- **End, AVI00000**: 130 cut the last 0.15 s of sound (the camera's stop click); 131 plays it, then silence.
- **Back mid-film**: silence on both (131 0.4 s sooner). **L1 / R1**: no repeat, at most a 0.1 s gap.
