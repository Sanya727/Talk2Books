import requests
from bs4 import BeautifulSoup
import yt_dlp


def get_youtube_transcript(url):

    try:

        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en", "hi", "pa"],
            "quiet": True
        }

        transcript_text = ""

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=False)

            subtitles = info.get("subtitles") or info.get("automatic_captions")

            if not subtitles:
                return ""

            for lang in ["en", "hi", "pa"]:

                if lang in subtitles:

                    subtitle_url = subtitles[lang][0]["url"]

                    r = requests.get(subtitle_url)

                    lines = r.text.split("\n")

                    lang_text = ""

                    for line in lines:

                        if "-->" not in line and line.strip() != "":
                            lang_text += line + " "

                    transcript_text += f"\n\n[{lang}]\n{lang_text}"

        print("YouTube transcript extracted")

        return transcript_text

    except Exception as e:

        print("YouTube transcript failed:", e)

        return ""


def get_website_text(url):

    try:

        headers = {"User-Agent": "Mozilla/5.0"}

        r = requests.get(url, headers=headers)

        soup = BeautifulSoup(r.text, "html.parser")

        paragraphs = soup.find_all("p")

        text = ""

        for p in paragraphs:
            text += p.get_text() + "\n"

        print("Website text extracted")

        return text

    except Exception as e:

        print("Website extraction failed:", e)

        return ""