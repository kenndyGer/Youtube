# -*- coding: utf-8 -*-
import logging
import random
from flask import Flask, jsonify, request

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

letzte_suche = "rammstein"

MUSIK_DATENBANK = {
    "rammstein": [
        {"title": "Sonne", "id": "ram1", "url": "https://r2.dev"},
        {"title": "Du Hast", "id": "ram2", "url": "https://r2.dev"}
    ],
    "helene fischer": [
        {"title": "Atemlos durch die Nacht", "id": "hel1", "url": "https://r2.dev"}
    ],
    "slipknot": [
        {"title": "Psychosocial", "id": "slip1", "url": "https://r2.dev"}
    ]
}

@app.route("/", methods=["POST"])
def alexa_endpoint():
    global letzte_suche
    alexa_request = request.get_json()
    request_type = alexa_request["request"]["type"]
    
    if request_type == "LaunchRequest":
        return jsonify({"version": "1.0", "response": {"outputSpeech": {"type": "PlainText", "text": "Cloud bereit. Was möchtest du hören?"}, "shouldEndSession": False}})
        
    elif request_type == "IntentRequest":
        intent_name = alexa_request["request"]["intent"]["name"]
        
        if intent_name in ["SearchImmediatelyIntent", "AMAZON.NextIntent"]:
            slots = alexa_request["request"]["intent"].get("slots", {})
            
            # Wir suchen in allen möglichen Boxen nach dem Wort!
            query = None
            for slot_name in slots:
                if slots[slot_name].get("value"):
                    query = slots[slot_name]["value"]
                    break
            
            if intent_name == "AMAZON.NextIntent" or not query:
                query = letzte_suche
                
            q_clean = query.lower().strip()
            letzte_suche = q_clean
            
            # DIAGNOSE: Wir prüfen, ob der Künstler in unserer Liste existiert
            gefundenes_video = None
            for kuenstler, lieder in MUSIK_DATENBANK.items():
                if kuenstler in q_clean:
                    gefundenes_video = random.choice(lieder)
                    break
            
            # WENN GEFUNDEN: Normal abspielen
            if gefundenes_video:
                return jsonify({
                    "version": "1.0",
                    "response": {
                        "outputSpeech": {"type": "PlainText", "text": f"Ich spiele {gefundenes_video['title']}"},
                        "directives": [{
                            "type": "AudioPlayer.Play",
                            "playBehavior": "REPLACE_ALL",
                            "audioItem": {
                                "stream": {"token": gefundenes_video['id'], "url": gefundenes_video['url'], "offsetInMilliseconds": 0}
                            }
                        }]
                    }
                })
            # WENN NICHT GEFUNDEN: Alexa sagt uns haargenau, welches falsche Wort sie verstanden hat!
            else:
                return jsonify({
                    "version": "1.0",
                    "response": {
                        "outputSpeech": {"type": "PlainText", "text": f"Der Server hat das Wort {query} empfangen, aber dieser Künstler steht nicht in der Liste."}
                    }
                })
            
        elif intent_name in ["AMAZON.PauseIntent", "AMAZON.StopIntent"]:
            return jsonify({"version": "1.0", "response": {"directives": [{"type": "AudioPlayer.Stop"}]}})
            
    return jsonify({"version": "1.0", "response": {"shouldEndSession": True}})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
