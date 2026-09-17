# -*- coding: utf-8 -*-
import logging
import random
from flask import Flask, jsonify, request
import yt_dlp

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

letzte_suche = "Charts"
aktueller_token = ""
aktuelle_audio_url = ""
pausen_zeitpunkt = 0
aktuell_gespielte_id = ""

def youtube_search_without_api(query):
    global letzte_suche, aktuell_gespielte_id
    if query:
        letzte_suche = query
        
    suchbegriff = letzte_suche.lower().replace("playlist", "").replace("album", "").strip()
    
    ydl_opts = {
        # HIER IST DER COU: Wir fordern exakt m4a (Format 140), das Alexa nativ abspielen kann!
        'format': '140/bestaudio[ext=m4a]/best', 
        'noplaylist': True,
        'extract_flat': False,
        'quiet': True,
        'default_search': 'ytsearch3',
        'nocheckcertificate': True,
        # Wir tarnen uns als Apple Safari Browser, um den m4a-Stream unblockiert zu erzwingen!
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Accept': '*/*',
        }
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            zusatz = random.choice([" audio", " lyrics", " live"])
            search_query = f"ytsearch3:{suchbegriff}{zusatz}"
            
            info = ydl.extract_info(search_query, download=False)
            
            if 'entries' in info and len(info['entries']) > 0:
                eintraege = [v for v in info['entries'] if v]
                
                # Wechselsperre anwenden
                pool = [v for v in eintraege if v.get('id') != aktuell_gespielte_id]
                if not pool:
                    pool = eintraege
                
                video = random.choice(pool)
                video_id = video.get('id')
                aktuell_gespielte_id = video_id
                    
                return video_id, video.get('title'), video.get('url')
    except Exception as e:
        logging.error(f"Fehler bei der YouTube-Direktsuche: {e}")
    return None, None, None

@app.route("/", methods=["POST"])
def alexa_endpoint():
    global aktueller_token, aktuelle_audio_url, pausen_zeitpunkt
    alexa_request = request.get_json()
    request_type = alexa_request["request"]["type"]
    
    if "context" in alexa_request and "AudioPlayer" in alexa_request["context"]:
        player_state = alexa_request["context"]["AudioPlayer"]
        if player_state.get("playerActivity") == "PLAYING":
            pausen_zeitpunkt = player_state.get("offsetInMilliseconds", 0)

    if request_type == "LaunchRequest":
        return jsonify({"version": "1.0", "response": {"outputSpeech": {"type": "PlainText", "text": "YouTube Cloud Server ist bereit. Was möchtest du hören?"}, "shouldEndSession": False}})
        
    elif request_type == "IntentRequest":
        intent_name = alexa_request["request"]["intent"]["name"]
        
        if intent_name in ["SearchImmediatelyIntent", "AMAZON.NextIntent"]:
            slots = alexa_request["request"]["intent"].get("slots", {})
            
            query = None
            for slot_name in slots:
                if slots[slot_name].get("value"):
                    query = slots[slot_name]["value"]
                    break
            
            if intent_name == "AMAZON.NextIntent":
                query = letzte_suche
                
            video_id, title, audio_url = youtube_search_without_api(query)
            if not video_id or not audio_url:
                return jsonify({"version": "1.0", "response": {"outputSpeech": {"type": "PlainText", "text": "Ich konnte leider keine Musik auf YouTube finden."}}})
                
            aktueller_token = video_id
            aktuelle_audio_url = audio_url
            pausen_zeitpunkt = 0 
            
            return jsonify({
                "version": "1.0",
                "response": {
                    "outputSpeech": {"type": "PlainText", "text": f"Ich spiele {title}"},
                    "directives": [{
                        "type": "AudioPlayer.Play",
                        "playBehavior": "REPLACE_ALL",
                        "audioItem": {
                            "stream": {"token": video_id, "url": audio_url, "offsetInMilliseconds": 0}
                        }
                    }]
                }
            })
            
        elif intent_name in ["AMAZON.PauseIntent", "AMAZON.StopIntent"]:
            return jsonify({"version": "1.0", "response": {"directives": [{"type": "AudioPlayer.Stop"}]}})
            
        elif intent_name == "AMAZON.ResumeIntent":
            if aktuelle_audio_url:
                return jsonify({
                    "version": "1.0",
                    "response": {
                        "directives": [{
                            "type": "AudioPlayer.Play",
                            "playBehavior": "REPLACE_ALL",
                            "audioItem": {
                                "stream": {
                                    "token": aktueller_token,
                                    "url": aktuelle_audio_url,
                                    "offsetInMilliseconds": pausen_zeitpunkt
                                }
                            }
                        }]
                    }
                })
            
    return jsonify({"version": "1.0", "response": {"shouldEndSession": True}})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
# -*- coding: utf-8 -*-
import logging
import random
from flask import Flask, jsonify, request
import yt_dlp

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

letzte_suche = "Charts"
aktueller_token = ""
aktuelle_audio_url = ""
pausen_zeitpunkt = 0
aktuell_gespielte_id = ""

def youtube_search_without_api(query):
    global letzte_suche, aktuell_gespielte_id
    if query:
        letzte_suche = query
        
    suchbegriff = letzte_suche.lower().replace("playlist", "").replace("album", "").strip()
    
    ydl_opts = {
        'format': 'worstaudio/bestaudio', 
        'noplaylist': True,
        'extract_flat': False,
        'quiet': True,
        'default_search': 'ytsearch3', # 3 Ergebnisse laden = blitzschnell!
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
        }
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Wir würfeln Zusätze für maximale Abwechslung bei "Weiter"
            zusatz = random.choice([" audio", " lyrics", " live"])
            search_query = f"ytsearch3:{suchbegriff}{zusatz}"
            
            info = ydl.extract_info(search_query, download=False)
            
            if 'entries' in info and len(info['entries']) > 0:
                eintraege = [v for v in info['entries'] if v]
                
                # Wechselsperre anwenden
                pool = [v for v in eintraege if v.get('id') != aktuell_gespielte_id]
                if not pool:
                    pool = eintraege
                
                video = random.choice(pool)
                video_id = video.get('id')
                aktuell_gespielte_id = video_id
                    
                return video_id, video.get('title'), video.get('url')
    except Exception as e:
        logging.error(f"Fehler bei der YouTube-Direktsuche: {e}")
    return None, None, None

@app.route("/", methods=["POST"])
def alexa_endpoint():
    global aktueller_token, aktuelle_audio_url, pausen_zeitpunkt
    alexa_request = request.get_json()
    request_type = alexa_request["request"]["type"]
    
    if "context" in alexa_request and "AudioPlayer" in alexa_request["context"]:
        player_state = alexa_request["context"]["AudioPlayer"]
        if player_state.get("playerActivity") == "PLAYING":
            pausen_zeitpunkt = player_state.get("offsetInMilliseconds", 0)

    if request_type == "LaunchRequest":
        return jsonify({"version": "1.0", "response": {"outputSpeech": {"type": "PlainText", "text": "YouTube Cloud Server ist bereit. Was möchtest du hören?"}, "shouldEndSession": False}})
        
    elif request_type == "IntentRequest":
        intent_name = alexa_request["request"]["intent"]["name"]
        
        if intent_name in ["SearchImmediatelyIntent", "AMAZON.NextIntent"]:
            slots = alexa_request["request"]["intent"].get("slots", {})
            
            query = None
            for slot_name in slots:
                if slots[slot_name].get("value"):
                    query = slots[slot_name]["value"]
                    break
            
            if intent_name == "AMAZON.NextIntent":
                query = letzte_suche
                
            video_id, title, audio_url = youtube_search_without_api(query)
            if not video_id or not audio_url:
                return jsonify({"version": "1.0", "response": {"outputSpeech": {"type": "PlainText", "text": "Ich konnte leider keine Musik auf YouTube finden."}}})
                
            aktueller_token = video_id
            aktuelle_audio_url = audio_url
            pausen_zeitpunkt = 0 
            
            return jsonify({
                "version": "1.0",
                "response": {
                    "outputSpeech": {"type": "PlainText", "text": f"Ich spiele {title}"},
                    "directives": [{
                        "type": "AudioPlayer.Play",
                        "playBehavior": "REPLACE_ALL",
                        "audioItem": {
                            "stream": {"token": video_id, "url": audio_url, "offsetInMilliseconds": 0}
                        }
                    }]
                }
            })
            
        elif intent_name in ["AMAZON.PauseIntent", "AMAZON.StopIntent"]:
            return jsonify({"version": "1.0", "response": {"directives": [{"type": "AudioPlayer.Stop"}]}})
            
        elif intent_name == "AMAZON.ResumeIntent":
            if aktuelle_audio_url:
                return jsonify({
                    "version": "1.0",
                    "response": {
                        "directives": [{
                            "type": "AudioPlayer.Play",
                            "playBehavior": "REPLACE_ALL",
                            "audioItem": {
                                "stream": {
                                    "token": aktueller_token,
                                    "url": aktuelle_audio_url,
                                    "offsetInMilliseconds": pausen_zeitpunkt
                                }
                            }
                        }]
                    }
                })
            
    return jsonify({"version": "1.0", "response": {"shouldEndSession": True}})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
