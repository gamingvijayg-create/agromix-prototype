"""
Agromix Backend Server
Flask API: Live weather, geocoding, multi-crop agronomic recommendation engine, and Twilio WhatsApp webhook.
"""

import os
import math
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend on localhost:3000

WEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")

if not WEATHER_API_KEY:
    print("⚠️ WARNING: OPENWEATHER_API_KEY not found in backend/.env")

# --------------------------------------------------------------------------
# Crop Dataset for Agronomic Match Scoring & Detailed Advice
# --------------------------------------------------------------------------
CROP_DATA = [
    {
        "crop": "Rice",
        "tamil": "அரிசி / நெல் (Nel)",
        "icon": "🌾",
        "optimal": {"n": 90, "p": 42, "k": 43, "ph": 6.5, "temp": 24, "humidity": 82, "rainfall": 236},
        "duration": "110 - 140 days",
        "type": "Cereal",
        "description": "High-water crop requiring flooded fields or well-drained loamy soil with warm humid climate.",
        "tips": "Maintain 2-5 cm water level during tillering phase. Apply Nitrogen in 3 splits (Basal, Tillering, Panicle initiation)."
    },
    {
        "crop": "Maize (Corn)",
        "tamil": "மக்காச்சோளம் (Makkacholam)",
        "icon": "🌽",
        "optimal": {"n": 80, "p": 48, "k": 40, "ph": 6.3, "temp": 23, "humidity": 65, "rainfall": 85},
        "duration": "90 - 110 days",
        "type": "Cereal",
        "description": "Versatile cereal crop requiring well-drained soil rich in organic matter and moderate rainfall.",
        "tips": "Sensitive to waterlogging. Ensure proper field drainage and earthing-up at 30 days post sowing."
    },
    {
        "crop": "Cotton",
        "tamil": "பருத்தி (Paruthi)",
        "icon": "☁️",
        "optimal": {"n": 120, "p": 46, "k": 20, "ph": 6.8, "temp": 24, "humidity": 80, "rainfall": 70},
        "duration": "150 - 180 days",
        "type": "Fiber",
        "description": "Black cotton soil (vertisols) or deep fertile loam with warm temperature during vegetative stage.",
        "tips": "Requires bright sunny days during boll ripening. Monitor for bollworm infestation during flowering."
    },
    {
        "crop": "Groundnut (Peanut)",
        "tamil": "நிலக்கடலை (Nilakkadalai)",
        "icon": "🥜",
        "optimal": {"n": 22, "p": 48, "k": 24, "ph": 6.4, "temp": 28, "humidity": 55, "rainfall": 55},
        "duration": "100 - 120 days",
        "type": "Oilseed / Legume",
        "description": "Nitrogen-fixing legume. Prefers loose sandy loam soil allowing easy peg penetration.",
        "tips": "Apply Gypsum at 400 kg/ha during flowering stage for proper pod development and calcium enrichment."
    },
    {
        "crop": "Sugarcane",
        "tamil": "கரும்பு (Karumbu)",
        "icon": "🎋",
        "optimal": {"n": 150, "p": 50, "k": 50, "ph": 7.0, "temp": 27, "humidity": 75, "rainfall": 150},
        "duration": "10 - 12 months",
        "type": "Cash Crop",
        "description": "Heavy feeder crop thriving in tropical climate with high humidity and abundant water.",
        "tips": "Trash mulching retains soil moisture. Top-dress Nitrogen fertilizer at 45, 90, and 120 days."
    },
    {
        "crop": "Chickpea (Gram)",
        "tamil": "கொண்டைக்கடலை (Kondaikkadalai)",
        "icon": "🧆",
        "optimal": {"n": 40, "p": 68, "k": 79, "ph": 7.3, "temp": 19, "humidity": 17, "rainfall": 80},
        "duration": "90 - 110 days",
        "type": "Pulse",
        "description": "Rabi cool-season crop. Highly drought-tolerant pulse requiring neutral to alkaline soil.",
        "tips": "Avoid waterlogged soils. Seed treatment with Rhizobium inoculant enhances nitrogen fixation."
    },
    {
        "crop": "Pigeonpeas (Arhar / Red Gram)",
        "tamil": "துவரை (Thuvarai)",
        "icon": "🫘",
        "optimal": {"n": 20, "p": 68, "k": 20, "ph": 5.7, "temp": 28, "humidity": 48, "rainfall": 150},
        "duration": "150 - 180 days",
        "type": "Pulse",
        "description": "Deep-rooted leguminous crop suitable for intercropping with sorghum, maize, or groundnut.",
        "tips": "Nipping apical buds at 60 days promotes secondary branching and increases pod yield."
    },
    {
        "crop": "Banana",
        "tamil": "வாழை (Vaazhai)",
        "icon": "🍌",
        "optimal": {"n": 100, "p": 82, "k": 50, "ph": 6.5, "temp": 27, "humidity": 80, "rainfall": 100},
        "duration": "11 - 14 months",
        "type": "Fruit",
        "description": "Tropical fruit tree needing rich organic soil, heavy potassium fertilizer, and high moisture.",
        "tips": "Desuckering (removing side shoots) is essential to direct nutrients to the primary fruiting mother plant."
    },
    {
        "crop": "Watermelon",
        "tamil": "தர்பூசணி (Tharpoosani)",
        "icon": "🍉",
        "optimal": {"n": 100, "p": 17, "k": 50, "ph": 6.5, "temp": 25, "humidity": 50, "rainfall": 50},
        "duration": "80 - 95 days",
        "type": "Horticulture",
        "description": "Warm-season vine crop thriving in sandy loam soils with warm days and cool nights.",
        "tips": "Drip irrigation with fertigation maximizes sweetness and fruit diameter."
    },
    {
        "crop": "Mango",
        "tamil": "மாம்பழம் (Maambazham)",
        "icon": "🥭",
        "optimal": {"n": 20, "p": 27, "k": 30, "ph": 6.0, "temp": 31, "humidity": 50, "rainfall": 95},
        "duration": "Perennial",
        "type": "Fruit",
        "description": "King of fruits. Dry period before flowering triggers prolific blossom development.",
        "tips": "Prune interior crowded branches to allow sunlight penetration and prevent powdery mildew."
    },
    {
        "crop": "Coconut",
        "tamil": "தென்னை (Thennai)",
        "icon": "🥥",
        "optimal": {"n": 22, "p": 18, "k": 31, "ph": 6.0, "temp": 27, "humidity": 72, "rainfall": 175},
        "duration": "Perennial",
        "type": "Plantation",
        "description": "Coastal and tropical palm requiring sandy loam, high humidity, and consistent groundwater.",
        "tips": "Apply 1 kg Urea, 1.5 kg Single Super Phosphate, and 2 kg Muriate of Potash per palm annually."
    },
    {
        "crop": "Blackgram (Urad)",
        "tamil": "உளுந்து (Ulundhu)",
        "icon": "🖤",
        "optimal": {"n": 40, "p": 67, "k": 19, "ph": 7.1, "temp": 30, "humidity": 65, "rainfall": 65},
        "duration": "70 - 85 days",
        "type": "Pulse",
        "description": "Short duration pulse crop excellent for crop rotation and paddy fallow cultivation.",
        "tips": "Foliar spray of 2% DAP at flowering and 15 days later significantly boosts pod formation."
    }
]

# --------------------------------------------------------------------------
# Weather Fetcher
# --------------------------------------------------------------------------
def get_weather(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": WEATHER_API_KEY,
        "units": "metric",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            return {"error": f"OpenWeather API returned status code {r.status_code}. Verify API key."}
        data = r.json()
        
        # Calculate rainfall (check 1h or 3h)
        rain_1h = data.get("rain", {}).get("1h", 0)
        rain_3h = data.get("rain", {}).get("3h", 0) / 3.0 if "3h" in data.get("rain", {}) else 0
        total_rain = max(rain_1h, rain_3h)
        
        return {
            "temperature": round(data["main"]["temp"], 1),
            "feels_like": round(data["main"]["feels_like"], 1),
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "rainfall": round(total_rain, 1),
            "description": data["weather"][0]["description"].title(),
            "icon": data["weather"][0]["icon"],
            "city": data.get("name", "Unknown Location"),
            "country": data.get("sys", {}).get("country", "")
        }
    except Exception as e:
        return {"error": f"Failed to connect to weather service: {str(e)}"}

# --------------------------------------------------------------------------
# Geocoding Service (City Name to Lat/Lon)
# --------------------------------------------------------------------------
def geocode_city(city_query):
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": city_query,
        "limit": 5,
        "appid": WEATHER_API_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            results = r.json()
            locations = []
            for item in results:
                locations.append({
                    "name": item.get("name"),
                    "state": item.get("state", ""),
                    "country": item.get("country", ""),
                    "lat": item.get("lat"),
                    "lon": item.get("lon")
                })
            return locations
        return []
    except Exception:
        return []

# --------------------------------------------------------------------------
# Multi-Crop Agronomic Matching Algorithm
# --------------------------------------------------------------------------
def recommend_crop_algorithm(n, p, k, ph, temp, humidity, rainfall):
    """
    Calculates weighted normalized Euclidean distance across soil & weather metrics.
    Returns ranked crop recommendations with detailed fertilizer & management tips.
    """
    scores = []
    
    weights = {
        "n": 1.2,
        "p": 1.0,
        "k": 1.0,
        "ph": 1.5,
        "temp": 1.5,
        "humidity": 1.1,
        "rainfall": 1.3
    }
    
    max_norms = {
        "n": 140.0,
        "p": 145.0,
        "k": 205.0,
        "ph": 14.0,
        "temp": 50.0,
        "humidity": 100.0,
        "rainfall": 300.0
    }

    for crop_info in CROP_DATA:
        opt = crop_info["optimal"]
        diff_sq = 0.0
        
        diff_sq += weights["n"] * ((n - opt["n"]) / max_norms["n"]) ** 2
        diff_sq += weights["p"] * ((p - opt["p"]) / max_norms["p"]) ** 2
        diff_sq += weights["k"] * ((k - opt["k"]) / max_norms["k"]) ** 2
        diff_sq += weights["ph"] * ((ph - opt["ph"]) / max_norms["ph"]) ** 2
        diff_sq += weights["temp"] * ((temp - opt["temp"]) / max_norms["temp"]) ** 2
        diff_sq += weights["humidity"] * ((humidity - opt["humidity"]) / max_norms["humidity"]) ** 2
        
        rain_diff = abs(rainfall - opt["rainfall"])
        diff_sq += weights["rainfall"] * (rain_diff / max_norms["rainfall"]) ** 2

        distance = math.sqrt(diff_sq)
        match_score = max(50.0, round(100.0 - (distance * 40.0), 1))
        
        scores.append({
            "crop": crop_info["crop"],
            "tamil": crop_info["tamil"],
            "icon": crop_info["icon"],
            "score": match_score,
            "type": crop_info["type"],
            "duration": crop_info["duration"],
            "description": crop_info["description"],
            "tips": crop_info["tips"],
            "optimal": opt
        })

    # Sort descending by match score
    scores.sort(key=lambda x: x["score"], reverse=True)
    top_crop = scores[0]
    runner_ups = scores[1:4]

    # Generate Fertilizer & Soil Advisory
    fert_advice = []
    opt = top_crop["optimal"]
    
    # Nitrogen advice
    n_diff = n - opt["n"]
    if n_diff < -15:
        urea_needed = round(abs(n_diff) * 2.17, 1)
        fert_advice.append(f"🔴 Nitrogen Deficit ({n} vs recommended {opt['n']} kg/ha): Apply approx {urea_needed} kg/ha of Urea in split doses.")
    elif n_diff > 25:
        fert_advice.append(f"⚠️ High Nitrogen detected ({n} kg/ha): Reduce nitrogenous fertilizer to avoid excessive vegetative growth and pest vulnerability.")
    else:
        fert_advice.append(f"🟢 Nitrogen Level ({n} kg/ha) is well-balanced for {top_crop['crop']}.")

    # Phosphorus advice
    p_diff = p - opt["p"]
    if p_diff < -10:
        dap_needed = round(abs(p_diff) * 2.17, 1)
        fert_advice.append(f"🔴 Phosphorus Deficit ({p} vs recommended {opt['p']} kg/ha): Apply approx {dap_needed} kg/ha of DAP (Di-ammonium Phosphate) during land preparation.")
    else:
        fert_advice.append(f"🟢 Phosphorus Level ({p} kg/ha) is optimal.")

    # Potassium advice
    k_diff = k - opt["k"]
    if k_diff < -10:
        mop_needed = round(abs(k_diff) * 1.66, 1)
        fert_advice.append(f"🔴 Potassium Deficit ({k} vs recommended {opt['k']} kg/ha): Apply approx {mop_needed} kg/ha of MOP (Muriate of Potash) for root strength and drought resilience.")
    else:
        fert_advice.append(f"🟢 Potassium Level ({k} kg/ha) is optimal.")

    # Soil pH advisory
    if ph < 5.8:
        fert_advice.append(f"🧪 Strongly Acidic Soil (pH {ph}): Apply Agricultural Lime (calcium carbonate) at 2-3 tonnes/ha to raise soil pH.")
    elif ph > 7.8:
        fert_advice.append(f"🧪 Alkaline Soil (pH {ph}): Apply Gypsum or elemental sulfur to lower alkalinity and improve micronutrient availability.")
    else:
        fert_advice.append(f"🧪 Ideal Soil pH ({ph}) for optimal nutrient absorption.")

    # Weather Risk & Pest Advisory
    weather_alerts = []
    if humidity > 78 and temp > 22:
        weather_alerts.append("🌧️ High relative humidity detected: High risk of fungal diseases (Blast/Rust). Apply preventive neem oil spray or bio-fungicide.")
    if temp > 36:
        weather_alerts.append("☀️ Extreme heat alert: Provide frequent light irrigation or drip fertigation to reduce heat stress.")
    if rainfall > 100:
        weather_alerts.append("🌊 High rainfall region: Ensure field drainage channels are cleared to prevent root rot.")

    return {
        "recommended_crop": top_crop["crop"],
        "tamil_name": top_crop["tamil"],
        "icon": top_crop["icon"],
        "match_score": top_crop["score"],
        "type": top_crop["type"],
        "duration": top_crop["duration"],
        "description": top_crop["description"],
        "tips": top_crop["tips"],
        "optimal_ranges": top_crop["optimal"],
        "fertilizer_advisory": fert_advice,
        "weather_alerts": weather_alerts,
        "runner_ups": [
            {"crop": c["crop"], "tamil": c["tamil"], "icon": c["icon"], "score": c["score"]} for c in runner_ups
        ]
    }

# --------------------------------------------------------------------------
# API Routes
# --------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "service": "Agromix AI Backend",
        "weather_api_configured": bool(WEATHER_API_KEY)
    })

@app.route("/api/geocode", methods=["GET"])
def geocode():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "Query param 'city' is required"}), 400
    locations = geocode_city(city)
    return jsonify(locations)

@app.route("/api/weather", methods=["GET"])
def weather_endpoint():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not lat or not lon:
        return jsonify({"error": "lat and lon query params required"}), 400
    weather = get_weather(lat, lon)
    if "error" in weather:
        return jsonify(weather), 400
    return jsonify(weather)

@app.route("/api/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json(force=True)
        required = ["n", "p", "k", "ph", "lat", "lon"]
        missing = [f for f in required if f not in data or data[f] == ""]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        n = float(data["n"])
        p = float(data["p"])
        k = float(data["k"])
        ph = float(data["ph"])
        lat = float(data["lat"])
        lon = float(data["lon"])

        # Fetch live weather data
        weather = get_weather(lat, lon)
        if "error" in weather:
            return jsonify({"error": weather["error"]}), 400

        # Perform recommendation calculation
        rec_data = recommend_crop_algorithm(
            n=n, p=p, k=k, ph=ph,
            temp=weather["temperature"],
            humidity=weather["humidity"],
            rainfall=weather["rainfall"]
        )

        return jsonify({
            "recommendation": rec_data,
            "weather_used": weather,
            "input_soil": {"n": n, "p": p, "k": k, "ph": ph}
        })
    except Exception as e:
        return jsonify({"error": f"Server processing error: {str(e)}"}), 500

# --------------------------------------------------------------------------
# Chatbot AI Assistant Engine
# --------------------------------------------------------------------------
def process_chat_query(user_msg, soil=None, weather=None, rec_crop=None):
    msg = user_msg.lower().strip()
    
    # Greetings
    if any(w in msg for w in ["hi", "hello", "hey", "vanakkam", "வணக்கம்", "வாழ்க"]):
        return (
            "🌾 *வணக்கம்! Welcome to Agromix Chatbot Assistant!*\n\n"
            "I can assist you with:\n"
            "• Fertilizer dosages (Urea, DAP, MOP)\n"
            "• Pest & disease control tips\n"
            "• Water & irrigation management\n"
            "• Soil pH & organic health improvement\n\n"
            "Ask me any question in English or Tamil!"
        )
    
    # Fertilizer
    if any(w in msg for w in ["fertilizer", "urea", "dap", "mop", "npk", "உரம்", "நைட்ரஜன்", "சத்து"]):
        crop_str = f"for *{rec_crop}*" if rec_crop else "for your crop"
        return (
            f"🧪 *Fertilizer Guidance {crop_str}*:\n\n"
            "1. **Nitrogen (N)**: Apply Urea (46% N) in 3 split doses (1/3 basal, 1/3 tillering, 1/3 flowering).\n"
            "2. **Phosphorus (P)**: Apply DAP or Single Super Phosphate during land preparation for root growth.\n"
            "3. **Potassium (K)**: Apply MOP (Muriate of Potash) for pest resistance and grain weight.\n"
            "4. **Bio-fertilizer**: Mix Azospirillum / Rhizobium with 50kg Farm Yard Manure (FYM)."
        )

    # Pest / Disease
    if any(w in msg for w in ["pest", "disease", "bug", "insect", "fungus", "leaf", "blast", "rust", "பூச்சி", "நோய்"]):
        return (
            "🐛 *Pest & Disease Management Advice*:\n\n"
            "• **Organic Spray**: Spray 5% Neem Seed Kernel Extract (NSKE) or Neem Oil (3 ml/L water) every 14 days.\n"
            "• **Fungal Infections**: High humidity triggers leaf blast/rust. Spray Copper Oxychloride (2.5 g/L) or Carbendazim.\n"
            "• **Sucking Pests**: Install Yellow & Blue Sticky Traps (10-12 per acre) in your field.\n"
            "• **Tip**: Avoid excessive Nitrogen fertilizer as it increases succulent leaf growth attracting pests!"
        )

    # Water / Irrigation
    if any(w in msg for w in ["water", "irrigation", "rain", "drought", "நீர்ப்பாசனம்", "மழை"]):
        w_temp = weather.get("temperature", 28) if weather else 28
        w_rain = weather.get("rainfall", 0) if weather else 0
        return (
            f"🌧️ *Irrigation & Moisture Advice*:\n\n"
            f"• Current Field Weather: {w_temp}°C with {w_rain} mm rainfall.\n"
            "• **Drip Irrigation**: Saves 40-50% water while delivering precise root fertigation.\n"
            "• **Critical Stages**: Ensure adequate moisture during flowering and grain filling stages.\n"
            "• **Mulching**: Spread paddy straw mulch to conserve soil moisture in summer."
        )

    # Soil & pH
    if any(w in msg for w in ["soil", "ph", "acid", "alkaline", "மண்"]):
        ph_val = soil.get("ph", 6.5) if soil else 6.5
        return (
            f"🧪 *Soil Health & pH Advice (Current pH: {ph_val})*:\n\n"
            "• **Acidic Soil (pH < 6.0)**: Apply Agricultural Lime (CaCO3) @ 2 tonnes/ha during plowing.\n"
            "• **Alkaline Soil (pH > 7.5)**: Apply Gypsum (CaSO4) @ 1-2 tonnes/ha and grow green manure crops.\n"
            "• **Organic Carbon**: Incorporate 10-12 tonnes of compost or FYM per hectare annually."
        )

    # Default general response
    crop_info = f" (Context: Recommended Crop *{rec_crop}*)" if rec_crop else ""
    return (
        f"🌿 *Agromix Agronomist AI Assistant*{crop_info}\n\n"
        f"Regarding your query *\"{user_msg}\"*:\n"
        "• Conduct soil test every 2 years before sowing season.\n"
        "• Balance N-P-K chemical inputs with organic bio-fertilizers.\n"
        "• Feel free to ask about fertilizers, pest management, irrigation, or soil health!"
    )

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        user_msg = data.get("message", "").strip()
        if not user_msg:
            return jsonify({"error": "Message body is empty"}), 400
            
        soil = data.get("soil", {})
        weather = data.get("weather", {})
        rec_crop = data.get("recommended_crop", "")

        reply = process_chat_query(user_msg, soil=soil, weather=weather, rec_crop=rec_crop)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": f"Chatbot processing error: {str(e)}"}), 500

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    from twilio.twiml.messaging_response import MessagingResponse
    incoming_msg = request.values.get("Body", "").strip()
    resp = MessagingResponse()
    msg = resp.message()

    if "crop" in incoming_msg.lower():
        msg.body("🌿 *Agromix Smart Assistant*\n\nSend your Soil test (N, P, K, pH) and Location on our web app for an instant multi-parameter recommendation!\n\nWebsite: http://localhost:3000")
    else:
        msg.body(
            "🌾 *Welcome to Agromix Agriculture AI!*\n\n"
            "Commands:\n"
            "• Type *CROP* for crop recommendation info\n"
            "• Open http://localhost:3000 for live soil testing & weather dashboard."
        )

    return str(resp)

if __name__ == "__main__":
    print("Agromix Backend starting on port 5000...")
    app.run(host="0.0.0.0", debug=True, port=5000)
