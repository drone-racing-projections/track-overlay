"""Spectator POV relay on the race box (ground station).

Pilot video for flying NEVER goes through this path. This is a delayed
secondary stream for TV / LAN / internet.

Pipeline (ffmpeg):
  source (RTMP push from phone, pull URL, or demo pattern)
    → optional restream to external RTMP (Twitch / YouTube / custom)
    → HLS segments under race_box/static/stream/ for LAN players & director UI

Typical phone publish URL (when MSDK / encoder ready):
  rtmp://<race-box-lan-ip>:1935/live/pilot
"""
from __future__ import annotations

import os
import shutil
import signal
import subprocess
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
HLS_DIR = ROOT / "static" / "stream"
DEFAULT_INGEST_PORT = int(os.environ.get("GATERACE_RTMP_PORT", "1935"))
DEFAULT_STREAM_KEY = os.environ.get("GATERACE_STREAM_KEY", "pilot")


def ffmpeg_bin() -> str | None:
    return shutil.which("ffmpeg")


@dataclass
class SpectatorConfig:
    """How the race box obtains and redistributes spectator video."""
    # ingest | pull | demo
    mode: str = "ingest"
    # RTMP listen port when mode=ingest
    ingest_port: int = DEFAULT_INGEST_PORT
    stream_key: str = DEFAULT_STREAM_KEY
    # When mode=pull: rtmp/rtsp/http URL of an existing stream
    pull_url: str = ""
    # Optional secondary publish (internet / another encoder)
    egress_rtmp_url: str = ""
    # HLS packaging
    hls_time: float = 2.0
    hls_list_size: int = 8
    # Transcode for compatibility (copy if already H264/AAC when possible)
    video_bitrate: str = "2500k"
    max_width: int = 1280


@dataclass
class SpectatorStatus:
    running: bool = False
    mode: str = "ingest"
    ffmpeg: bool = False
    pid: int | None = None
    started_at: float | None = None
    error: str | None = None
    ingest_url: str = ""
    hls_path: str = "/stream/index.m3u8"
    hls_ready: bool = False
    egress_rtmp_url: str = ""
    note: str = (
        "Spectator only — multi-second delay OK. Pilot AR stays on the phone."
    )


class SpectatorRelay:
    def __init__(self) -> None:
        self.config = SpectatorConfig()
        self._proc: subprocess.Popen | None = None
        self._started_at: float | None = None
        self._error: str | None = None

    def status(self) -> dict[str, Any]:
        running = self._proc is not None and self._proc.poll() is None
        if self._proc is not None and self._proc.poll() is not None:
            # died
            code = self._proc.returncode
            if code not in (0, None) and not self._error:
                self._error = f"ffmpeg exited with code {code}"
            self._proc = None
            running = False
        hls_index = HLS_DIR / "index.m3u8"
        host_hint = "<race-box-lan-ip>"
        ingest = (
            f"rtmp://{host_hint}:{self.config.ingest_port}/live/{self.config.stream_key}"
            if self.config.mode == "ingest"
            else self.config.pull_url
        )
        st = SpectatorStatus(
            running=running,
            mode=self.config.mode,
            ffmpeg=ffmpeg_bin() is not None,
            pid=self._proc.pid if running and self._proc else None,
            started_at=self._started_at if running else None,
            error=self._error,
            ingest_url=ingest,
            hls_path="/stream/index.m3u8",
            hls_ready=hls_index.exists(),
            egress_rtmp_url=self.config.egress_rtmp_url,
        )
        return asdict(st)

    def configure(self, data: dict[str, Any]) -> SpectatorConfig:
        c = self.config
        if "mode" in data and data["mode"] in ("ingest", "pull", "demo"):
            c.mode = str(data["mode"])
        if "ingest_port" in data:
            c.ingest_port = int(data["ingest_port"])
        if "stream_key" in data and data["stream_key"]:
            c.stream_key = str(data["stream_key"]).strip().replace("/", "")
        if "pull_url" in data:
            c.pull_url = str(data["pull_url"] or "")
        if "egress_rtmp_url" in data:
            c.egress_rtmp_url = str(data["egress_rtmp_url"] or "").strip()
        if "video_bitrate" in data:
            c.video_bitrate = str(data["video_bitrate"])
        if "max_width" in data:
            c.max_width = int(data["max_width"])
        self.config = c
        return c

    def stop(self) -> None:
        if self._proc is None:
            return
        proc = self._proc
        self._proc = None
        try:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        self._started_at = None

    def start(self, data: dict[str, Any] | None = None) -> dict[str, Any]:
        if data:
            self.configure(data)
        ff = ffmpeg_bin()
        if not ff:
            self._error = "ffmpeg not found — install ffmpeg on the race box host"
            return self.status()

        if self._proc is not None and self._proc.poll() is None:
            self._error = "already running — stop first"
            return self.status()

        HLS_DIR.mkdir(parents=True, exist_ok=True)
        # clear old segments
        for p in HLS_DIR.glob("*"):
            try:
                p.unlink()
            except OSError:
                pass

        c = self.config
        hls_out = str(HLS_DIR / "index.m3u8")
        # Common encode + HLS (+ optional egress tee)
        vscale = f"scale='min({c.max_width},iw)':-2"
        encode = [
            "-c:v", "libx264", "-preset", "veryfast", "-tune", "zerolatency",
            "-b:v", c.video_bitrate, "-maxrate", c.video_bitrate, "-bufsize", "4M",
            "-g", "60", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac",  "2",
        ]

        cmd: list[str] = [ff, "-hide_banner", "-loglevel", "warning", "-y"]

        if c.mode == "demo":
            # Colored test pattern with timestamp — proves TV / director path without a phone
            cmd += [
                "-re", "-f", "lavfi",
                "-i", "testsrc=size=1280x720:rate=30,format=yuv420p",
                "-f", "lavfi", "-i", "sine=frequency=880:sample_rate=44100",
                "-vf", f"{vscale},drawtext=text='GateRace spectator DEMO':x=24:y=24:fontsize=28:fontcolor=white",
                "-shortest",
            ] + encode
        elif c.mode == "pull":
            if not c.pull_url:
                self._error = "pull_url required when mode=pull"
                return self.status()
            cmd += ["-i", c.pull_url, "-vf", vscale] + encode
        else:
            # ingest: wait for phone/encoder to publish
            listen_url = f"rtmp://0.0.0.0:{c.ingest_port}/live/{c.stream_key}"
            cmd += [
                "-f", "flv", "-listen", "1", "-timeout", "30000000",
                "-i", listen_url,
                "-vf", vscale,
            ] + encode

        # Outputs: HLS always; optional second RTMP via tee muxer
        if c.egress_rtmp_url:
            # ffmpeg tee: [f=hls]path|[f=flv]rtmp://...
            tee = (
                f"[f=hls:hls_time={c.hls_time}:hls_list_size={c.hls_list_size}:"
                f"hls_flags=delete_segments+append_list]{hls_out}|"
                f"[f=flv]{c.egress_rtmp_url}"
            )
            cmd += ["-f", "tee", tee]
        else:
            cmd += [
                "-f", "hls",
                "-hls_time", str(c.hls_time),
                "-hls_list_size", str(c.hls_list_size),
                "-hls_flags", "delete_segments+append_list",
                hls_out,
            ]

        try:
            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            self._started_at = time.time()
            self._error = None
        except Exception as e:
            self._error = str(e)
            self._proc = None
        return self.status()


# Singleton used by server
relay = SpectatorRelay()
