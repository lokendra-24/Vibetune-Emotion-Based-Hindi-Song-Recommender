from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from deepface import DeepFace
from pydantic import BaseModel
from typing import List
import tempfile, shutil, os

app = FastAPI(title="VibeTune API")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Song database
SONG_DB = {
    "happy": [
        {"title": "Dil Chahta Hai", "artist": "Shankar‑Ehsaan‑Loy", "url": "https://youtu.be/_I9q0O5gMbQ"},
        {"title": "Ude Dil Befikre", "artist": "Vishal‑Shekhar", "url": "https://youtu.be/FEWGE6wQHjw"},
        {"title": "Nashe Si Chadh Gayi", "artist": "Arijit Singh", "url": "https://youtu.be/sQp6B0zzBY8"},
        {"title": "Badtameez Dil", "artist": "Benny Dayal", "url": "https://youtu.be/3Q0qjJ6pQWI"},
        {"title": "Cutiepie", "artist": "Pritam", "url": "https://youtu.be/gK3FHN5z1HA"},
        {"title": "Gal Mitthi Mitthi", "artist": "Tochi Raina", "url": "https://youtu.be/FtSbD2bVjjs"},
        {"title": "Kar Gayi Chull", "artist": "Badshah", "url": "https://youtu.be/x3P9O3R2mYQ"},
        {"title": "The Breakup Song", "artist": "Arijit Singh", "url": "https://youtu.be/9xkLuYfE2Po"},
        {"title": "Tareefan", "artist": "Badshah", "url": "https://youtu.be/B8I-7Wk_Vbc"},
        {"title": "Gallan Goodiyan", "artist": "Various", "url": "https://youtu.be/uY8xovb6m2k"}
    ],
    "sad": [
        {"title": "Channa Mereya", "artist": "Arijit Singh", "url": "https://youtu.be/284Ov7ysmfA"},
        {"title": "Agar Tum Saath Ho", "artist": "Alka/Arijit", "url": "https://youtu.be/gvyUuxdRdR4"},
        {"title": "Hamari Adhuri Kahani", "artist": "Arijit Singh", "url": "https://youtu.be/0G2VxhV_gXM"},
        {"title": "Kabira", "artist": "Tochi Raina", "url": "https://youtu.be/jHNNMj5bNQw"},
        {"title": "Tadap Tadap", "artist": "KK", "url": "https://youtu.be/vI7uK8x5Q5c"},
        {"title": "Phir Le Aya Dil", "artist": "Rekha Bhardwaj", "url": "https://youtu.be/wKHyD6S7C6o"},
        {"title": "Bhula Dena", "artist": "Mustafa Zahid", "url": "https://youtu.be/7E-Rfv0T6gY"},
        {"title": "Main Dhoondhne Ko Zamaane Mein", "artist": "Arijit Singh", "url": "https://youtu.be/T_NTk9FZvak"},
        {"title": "Raabta (Agent Vinod)", "artist": "Arijit Singh", "url": "https://youtu.be/V2Y2cLkP2Do"},
        {"title": "Tujhe Bhula Diya", "artist": "Mohit Chauhan", "url": "https://youtu.be/5J1c8aG-5PY"}
    ],
    "angry": [
        {"title": "Zinda", "artist": "Siddharth Mahadevan", "url": "https://youtu.be/rjq5ImYdw1k"},
        {"title": "Malang Title", "artist": "Ved Sharma", "url": "https://youtu.be/Dh-ULbQmmF8"},
        {"title": "Sher Aaya Sher", "artist": "Divine", "url": "https://youtu.be/klY9Do0XvKo"},
        {"title": "Apna Time Aayega", "artist": "Ranveer Singh", "url": "https://youtu.be/jzYxbnHHrwM"},
        {"title": "Khoon Choos Le", "artist": "Arjun Kanungo", "url": "https://youtu.be/O-fyNgHdmLI"},
        {"title": "Sultan Title Track", "artist": "Sukhwinder Singh", "url": "https://youtu.be/3x4FjpsazZ8"},
        {"title": "Brothers Anthem", "artist": "Vishal Dadlani", "url": "https://youtu.be/K0nU_lhQfG4"},
        {"title": "Jee Karda", "artist": "Divya Kumar", "url": "https://youtu.be/GQuX8uJdo8M"},
        {"title": "Jai Jai Shivshankar", "artist": "Vishal‑Shekhar", "url": "https://youtu.be/4zHaOb2PLaI"},
        {"title": "Get Ready To Fight", "artist": "Benny Dayal", "url": "https://youtu.be/bbZKcTgobdU"}
    ],
    "neutral": [
        {"title": "Ilahi", "artist": "Arijit Singh", "url": "https://youtu.be/Yj5T15-cBgw"},
        {"title": "Tera Yaar Hoon Main", "artist": "Arijit Singh", "url": "https://youtu.be/hHdKfKbx4rE"},
        {"title": "Phir Se Ud Chala", "artist": "Mohit Chauhan", "url": "https://youtu.be/QOj0zAWDqkk"},
        {"title": "Safarnama", "artist": "Lucky Ali", "url": "https://youtu.be/g0eO74UmRBs"},
        {"title": "Patakha Guddi", "artist": "Nooran Sisters", "url": "https://youtu.be/YR12Z8f1Dh8"},
        {"title": "Yun Hi", "artist": "Mohit Chauhan", "url": "https://youtu.be/DUtNvuAXvcc"},
        {"title": "Hairat", "artist": "Lucky Ali", "url": "https://youtu.be/3IHDtCcv0aY"},
        {"title": "Aazaadiyan", "artist": "Neeti Mohan", "url": "https://youtu.be/B2SffbGpq1g"},
        {"title": "Dil Dhadakne Do", "artist": "Priyanka Chopra", "url": "https://youtu.be/6pzYxu1Tr2E"},
        {"title": "Rock On!!", "artist": "Farhan Akhtar", "url": "https://youtu.be/vsIq_ZI8SeA"}
    ]
}

# Response schema
class Song(BaseModel):
    title: str
    artist: str
    url: str

class AnalyzeResponse(BaseModel):
    emotion: str
    songs: List[Song]

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_emotion(file: UploadFile = File(...)):
    if file.content_type.split("/")[0] != "image":
        raise HTTPException(400, "Only image files allowed.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
        shutil.copyfileobj(file.file, temp)
        path = temp.name

    try:
        result = DeepFace.analyze(img_path=path, actions=["emotion"])
        emotion = result[0]["dominant_emotion"]  # ✅ THIS LINE FIXED
    except Exception as e:
        raise HTTPException(500, f"Emotion detection failed: {e}")
    finally:
        os.remove(path)

    songs = SONG_DB.get(emotion.lower(), SONG_DB["neutral"])
    return {"emotion": emotion, "songs": songs}