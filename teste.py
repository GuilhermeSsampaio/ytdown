import sys
import tempfile
from pathlib import Path
import subprocess
import shutil

from pytubefix import YouTube

url = 'https://www.youtube.com/watch?v=vx2u5uUu3DE'

print(f"[*] Inicializando YouTube para a URL: {url}")
try:
    yt = YouTube(url, client='WEB')
    print(f"[*] Vídeo encontrado: {yt.title}")
    
    print("[*] Buscando stream de vídeo (melhor resolução mp4)...")
    video_stream = yt.streams.filter(only_video=True, file_extension="mp4").order_by("resolution").desc().first()
    
    if not video_stream:
        print("[!] Erro: Nenhum stream de vídeo encontrado.")
        sys.exit(1)
        
    print(f"[*] Stream de vídeo selecionado: itag={video_stream.itag}, resolução={video_stream.resolution}, includes_video_track={getattr(video_stream, 'includes_video_track', 'N/A')}")
    
    # Simulate the check from app.py
    if not getattr(video_stream, 'includes_video_track', False):
        print("[!] Erro simulado: video_stream não possui includes_video_track = True")
        # Trying is_video just in case
        print(f"[*] fallback check is_video: {getattr(video_stream, 'is_video', 'N/A')}")
    
    print("[*] Buscando stream de áudio (melhor bitrate)...")
    audio_stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
    
    if not audio_stream:
        print("[!] Erro: Nenhum stream de áudio encontrado.")
        sys.exit(1)
        
    print(f"[*] Stream de áudio selecionado: itag={audio_stream.itag}, abr={audio_stream.abr}")
    
    work_dir = Path(tempfile.mkdtemp(prefix="ytdown-test-"))
    print(f"[*] Diretório temporário criado: {work_dir}")
    
    try:
        print("[*] Iniciando download do vídeo...")
        video_path = Path(video_stream.download(output_path=str(work_dir), filename="video.mp4"))
        print(f"[*] Download do vídeo concluído: {video_path}")
        
        print("[*] Iniciando download do áudio...")
        audio_path = Path(audio_stream.download(output_path=str(work_dir), filename="audio.mp4"))
        print(f"[*] Download do áudio concluído: {audio_path}")
        
        output_path = Path(work_dir) / "output.mp4"
        
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"[*] Executável do FFmpeg: {ffmpeg}")
        
        command = [
            ffmpeg, "-y", "-i", str(video_path), "-i", str(audio_path),
            "-c:v", "copy", "-c:a", "aac", "-movflags", "+faststart", str(output_path),
        ]
        
        print("[*] Juntando áudio e vídeo...")
        result = subprocess.run(command, capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        
        if result.returncode != 0:
            print("[!] Erro ao juntar com o ffmpeg:")
            print(result.stderr)
        else:
            print(f"[*] Sucesso! Arquivo gerado: {output_path}")
            
    finally:
        print("[*] Limpando diretório temporário...")
        shutil.rmtree(work_dir, ignore_errors=True)
        print("[*] Fim.")

except Exception as exc:
    print(f"[!] Exceção não tratada: {exc}")
    import traceback
    traceback.print_exc()