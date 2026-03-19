from flask import Flask, render_template, request
import os, subprocess, threading, time, shutil
from werkzeug.utils import secure_filename
from pytube import YouTube

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def delete_clips_after_delay(folder_path, delay=1800):
    time.sleep(delay)
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

@app.route("/", methods=["GET", "POST"])
def index():
    clips = []
    if request.method == "POST":
        youtube_url = request.form.get("youtube_url")
        if youtube_url:
            yt = YouTube(youtube_url)
            stream = yt.streams.get_highest_resolution()

            filename = secure_filename(yt.title + ".mp4")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            stream.download(output_path=app.config['UPLOAD_FOLDER'], filename=filename)

            clip_folder = os.path.join(app.config['UPLOAD_FOLDER'], "clips")
            os.makedirs(clip_folder, exist_ok=True)

            cmd = f'ffmpeg -i "{filepath}" -c copy -map 0 -segment_time 30 -f segment "{clip_folder}/clip%03d.mp4"'
            subprocess.call(cmd, shell=True)

            # حذف الفيديو الأصلي
            os.remove(filepath)

            clips = os.listdir(clip_folder)
            clips = [f"uploads/clips/{c}" for c in clips]

            # حذف المقاطع بعد 30 دقيقة
            threading.Thread(target=delete_clips_after_delay, args=(clip_folder,)).start()

    return render_template("index.html", clips=clips)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
