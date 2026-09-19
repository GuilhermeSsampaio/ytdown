"""Servidor local para baixar vídeos permitidos pelo usuário."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from pytubefix import YouTube


def resource_path(relative_path: str) -> Path:
    """Localiza arquivos tanto no código-fonte como no executável PyInstaller."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative_path


app = Flask(
    __name__,
    template_folder=str(resource_path("templates")),
    static_folder=str(resource_path("static")),
)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def safe_filename(value: str) -> str:
    value = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", value).strip(". ")
    return (value or "video")[:140]


def get_video(url: str) -> YouTube:
    if not url or not url.startswith(("https://", "http://")):
        raise ValueError("Informe uma URL válida começando com http:// ou https://.")
    return YouTube(url, client='WEB')


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/info")
def info():
    data = request.get_json(silent=True) or {}
    try:
        yt = get_video(str(data.get("url", "")).strip())
        streams = []
        # Streams adaptativos preservam a qualidade original; o áudio é unido no download.
        for stream in yt.streams.filter(only_video=True, file_extension="mp4").order_by("resolution").desc():
            if stream.resolution:
                streams.append({
                    "itag": stream.itag,
                    "label": f"{stream.resolution} · MP4",
                    "resolution": stream.resolution,
                    "fps": stream.fps,
                })
        if not streams:
            raise ValueError("Não encontrei formatos MP4 para este vídeo.")
        return jsonify({
            "title": yt.title,
            "author": yt.author,
            "thumbnail": yt.thumbnail_url,
            "streams": streams,
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/download")
def download():
    data = request.get_json(silent=True) or {}
    try:
        yt = get_video(str(data.get("url", "")).strip())
        itag = data.get("itag")
        if str(itag).lower() == "best":
            video_stream = yt.streams.filter(only_video=True, file_extension="mp4").order_by("resolution").desc().first()
        else:
            video_stream = yt.streams.get_by_itag(int(itag))
        if not video_stream or not video_stream.includes_video_track:
            raise ValueError("A qualidade selecionada não está disponível. Consulte o vídeo novamente.")
        audio_stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
        if not audio_stream:
            raise ValueError("Não foi possível encontrar a faixa de áudio.")

        # O diretório permanece até a resposta ser totalmente enviada ao navegador.
        work_dir = Path(tempfile.mkdtemp(prefix="ytdown-"))
        try:
            video_path = Path(video_stream.download(output_path=str(work_dir), filename="video.mp4"))
            audio_path = Path(audio_stream.download(output_path=str(work_dir), filename="audio.mp4"))
            output_path = Path(work_dir) / f"{safe_filename(yt.title)}.mp4"

            import imageio_ffmpeg

            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            command = [
                ffmpeg, "-y", "-i", str(video_path), "-i", str(audio_path),
                "-c:v", "copy", "-c:a", "aac", "-movflags", "+faststart", str(output_path),
            ]
            result = subprocess.run(command, capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            if result.returncode != 0 or not output_path.exists():
                raise RuntimeError("Não foi possível unir vídeo e áudio. Tente outra qualidade.")

            # A limpeza ocorre ao fechar a resposta, depois de o navegador recebê-la.
            response = send_file(
                output_path,
                as_attachment=True,
                download_name=output_path.name,
                mimetype="video/mp4",
            )
            response.call_on_close(lambda: shutil.rmtree(work_dir, ignore_errors=True))
            return response
        except Exception:
            shutil.rmtree(work_dir, ignore_errors=True)
            raise
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


if __name__ == "__main__":
    # Abrir o navegador somente quando o executável/app é iniciado diretamente.
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        threading.Timer(0.8, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
