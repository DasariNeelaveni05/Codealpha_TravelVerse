## NYC Background Videos for TravelVerse

Place 4–6 cinematic NYC MP4 files in this folder and name them:
- `nyc-1.mp4`
- `nyc-2.mp4`
- `nyc-3.mp4`
- `nyc-4.mp4`

Where to get free cinematic NYC clips
- Pexels (videos): https://www.pexels.com/search/videos/new%20york%20city/ — Best for editorial, skyline, timelapse.
- Coverr: https://coverr.co/ — Loop-ready scenic city clips.
- Mixkit: https://mixkit.co/free-stock-video/new-york/ — Adventure and drone shots.
- Pixabay (videos): https://pixabay.com/videos/search/new%20york/ — Aerial and street footage.

Recommended search terms
- "New York City aerial"
- "NYC timelapse"
- "Manhattan skyline night"
- "New York adventure"
- "Times Square crowd"

Notes & usage
- Files should be MP4 (H.264) for broad browser support. Keep each clip < 15–20MB for faster loading in demos.
- The landing hero reads `data-video-sources` in the DOM and will rotate these files every 7s with a soft fade.
- If you don't add files, the hero will fall back to the `data-hero-slides` images.

Quick PowerShell download example (run in project root):
```powershell
# Example: download and save as static/videos/nyc-1.mp4
Invoke-WebRequest -Uri "<paste-pexels-or-coverr-direct-mp4-url>" -OutFile "static/videos/nyc-1.mp4"
```

License
- Confirm the clip's license on the source page (Pexels/Mixkit/Coverr clips are usually free for commercial and personal use, but verify attribution requirements if any).

If you'd like, I can download a small set of sample clips for you (requires your approval). Otherwise, tell me which option next: I'll download samples, or run a local preview server for you to inspect the changes.
