from flask import Flask, request, render_template, send_file, url_for
import tempfile, os, pathlib, time
from gtts import gTTS
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)
TMP = pathlib.Path(tempfile.gettempdir()) / "urdu_the_play"
TMP.mkdir(exist_ok=True)

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url","").strip()
        if not url:
            return render_template("index.html", message="براہِ کرم یوٹیوب لنک دیں۔")
        vid = None
        if "v=" in url:
            vid = url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            vid = url.split("youtu.be/")[1].split("?")[0]
        else:
            return render_template("index.html", message="یوٹیوب لنک درست نہیں۔")
        transcript = None
        try:
            transcript = YouTubeTranscriptApi.get_transcript(vid, languages=['ur','en'])
        except Exception:
            transcript = None
        if transcript:
            lines = []
            for item in transcript:
                text = item.get("text","").strip()
                if text:
                    lines.append(f"اس نے کہا: {text}")
            voice_text = "۔ ".join(lines)[:18000]
        else:
            voice_text = "معذرت — اس ویڈیو کے لیے سب ٹائٹل دستیاب نہیں ہیں۔"
        sid = str(int(time.time()*1000))
        out_mp3 = TMP / f"{sid}.mp3"
        try:
            tts = gTTS(voice_text or "کوئی متن نہیں ملا", lang="ur")
            tts.save(str(out_mp3))
        except Exception as e:
            return render_template("index.html", message=f"آواز بنانے میں مسئلہ: {e}")
        return render_template("player.html", video_id=vid, voice_url=url_for("serve_audio",fn=out_mp3.name))
    return render_template("index.html", message="")

@app.route("/audio/<fn>")
def serve_audio(fn):
    p = TMP / fn
    if p.exists():
        return send_file(str(p))
    return "Not found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
