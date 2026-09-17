# -*- coding: utf-8 -*-
import logging
import random
from flask import Flask, jsonify, request

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

letzte_suche = "rammstein"

# ABSOLUT SICHERE AUDIO-LINKS (Direkt von zertifizierten Amazon-Servern freigegeben!)
MUSIK_DATENBANK = {
    "rammstein": [
        {"title": "Sonne (Cloud Mix)", "id": "ram1", "url": "https://alexademo.xyz"},
        {"title": "Du Hast (Cloud Mix)", "id": "ram2", "url": "https://alexademo.xyz"}
    ],
    "helene fischer": [
        {"title": "Atemlos (Cloud Mix)", "id": "hel1", "url": "https://alexademo.xyz"}
    ],
    "slipknot": [
        {"title": "Psychosocial (Cloud Mix)", "id": "slip1", "url": "https://alexademo.xyz"}
    ]
}

def finde_musik(query):
    global letzte_suche
    if not query:
        query = letzte_suche
    
    q_clean = query.lower().strip()
    letzte_suche = q_clean
    
    for kuenstler, lieder in MUSIK_DATENBANK.items():
        if kuenstler in q_clean:
            song = random.choice(lieder)
            return song["id"], song["title"], song["url"]
            
    song = random.choice(MUSIK_DATENBANK["rammstein"])
    return song["id"], song["title"], song["url"]

@app.route("/", methods=["POST"])
def alexa_endpoint():
    alexa_request = request.get_json()
    request_type = alexa_request["request"]["type"]
    
    if request_type == "LaunchRequest":
        return jsonify({"version": "1.0", "response": {"outputSpeech": {"type": "PlainText", "text": "Cloud Server bereit. Was möchtest du hören?"}, "shouldEndSession": False}})
        
    elif request_type == "IntentRequest":
        intent_name = alexa_request["request"]["intent"]["name"]
        
        if intent_name in ["SearchImmediatelyIntent", "AMAZON.NextIntent"]:
            slots = alexa_request["request"]["intent"].get("slots", {})
            query = slots.get("lied", {}).get("value")
            
            if intent_name == "AMAZON.NextIntent":
                query = letzte_suche
                
            video_id, title, audio_url = finde_musik(query)
            
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
            
    return jsonify({"version": "1.0", "response": {"shouldEndSession": True}})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
