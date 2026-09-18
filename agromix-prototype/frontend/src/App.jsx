import React, { useState, useEffect, useRef } from "react";
import "./App.css";

const API_BASE = "http://localhost:5000";

// Preset soil profiles for quick 1-click testing
const SOIL_PRESETS = [
  { name: "Paddy Field (Clay Loam)", n: "90", p: "42", k: "43", ph: "6.5", icon: "🌾" },
  { name: "Black Cotton Soil", n: "120", p: "46", k: "20", ph: "7.2", icon: "☁️" },
  { name: "Red Sandy Loam", n: "22", p: "48", k: "24", ph: "6.4", icon: "🥜" },
  { name: "High N Fertile Soil", n: "150", p: "50", k: "50", ph: "7.0", icon: "🎋" },
];

// Preset Indian Agri Hub Cities
const POPULAR_CITIES = [
  { name: "Madurai", lat: "9.9252", lon: "78.1198" },
  { name: "Coimbatore", lat: "11.0168", lon: "76.9558" },
  { name: "Thanjavur", lat: "10.7870", lon: "79.1378" },
  { name: "Salem", lat: "11.6643", lon: "78.1460" },
  { name: "Chennai", lat: "13.0827", lon: "80.2707" },
  { name: "Nashik", lat: "20.0000", lon: "73.7800" },
];

export default function App() {
  const [form, setForm] = useState({
    n: "90",
    p: "42",
    k: "43",
    ph: "6.5",
    lat: "9.9252",
    lon: "78.1198",
  });

  const [citySearch, setCitySearch] = useState("Madurai");
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [liveWeather, setLiveWeather] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("overview");

  // Fetch weather preview when lat/lon changes
  useEffect(() => {
    fetchWeatherPreview(form.lat, form.lon);
  }, [form.lat, form.lon]);

  const fetchWeatherPreview = async (lat, lon) => {
    setWeatherLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/weather?lat=${lat}&lon=${lon}`);
      const data = await res.json();
      if (res.ok && !data.error) {
        setLiveWeather(data);
        if (data.city && data.city !== "Unknown Location") {
          setCitySearch(data.city);
        }
      }
    } catch (e) {
      console.error("Weather fetch failed", e);
    } finally {
      setWeatherLoading(false);
    }
  };

  const handleCitySearch = async (query) => {
    setCitySearch(query);
    if (!query || query.trim().length < 2) {
      setSearchResults([]);
      return;
    }
    setSearchLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/geocode?city=${encodeURIComponent(query)}`);
      const data = await res.json();
      if (Array.isArray(data)) {
        setSearchResults(data);
      }
    } catch (e) {
      console.error("Geocoding failed", e);
    } finally {
      setSearchLoading(false);
    }
  };

  const selectCity = (loc) => {
    setForm({
      ...form,
      lat: String(loc.lat.toFixed(4)),
      lon: String(loc.lon.toFixed(4)),
    });
    setCitySearch(`${loc.name}${loc.state ? ", " + loc.state : ""}`);
    setSearchResults([]);
  };

  const useGPSLocation = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude.toFixed(4);
        const lon = pos.coords.longitude.toFixed(4);
        setForm({ ...form, lat: String(lat), lon: String(lon) });
      },
      (err) => {
        alert("Unable to fetch location: " + err.message);
      }
    );
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const applyPreset = (preset) => {
    setForm({
      ...form,
      n: preset.n,
      p: preset.p,
      k: preset.k,
      ph: preset.ph,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Recommendation failed");
      setResult(data);
      setActiveTab("overview");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="agromix-app">
      {/* Top Navbar */}
      <header className="agromix-header">
        <div className="brand-container">
          <div className="logo-icon">🌿</div>
          <div>
            <h1 className="brand-title">Agromix AI</h1>
            <p className="brand-subtitle">Smart Agronomy & Precision Farming</p>
          </div>
        </div>

        <div className="header-status">
          <span className="live-badge">
            <span className="pulse-dot"></span> OpenWeather Live API
          </span>
          <span className="local-host-badge">Backend Port: 5000</span>
        </div>
      </header>

      {/* Main Grid */}
      <main className="agromix-grid">
        {/* Left Side: Inputs */}
        <section className="input-card">
          <div className="card-header">
            <h2>🌱 Field & Soil Data Input</h2>
            <p>Enter soil test parameters or select a preset profile.</p>
          </div>

          {/* Preset Buttons */}
          <div className="preset-section">
            <label className="section-label">Quick Soil Presets:</label>
            <div className="preset-grid">
              {SOIL_PRESETS.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  className="preset-chip"
                  onClick={() => applyPreset(p)}
                >
                  <span>{p.icon}</span> {p.name}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="agromix-form">
            {/* Location Search Bar */}
            <div className="location-box">
              <label className="section-label">📍 Field Location / City</label>
              <div className="search-input-wrapper">
                <input
                  type="text"
                  placeholder="Search city e.g. Madurai, Tanjore..."
                  value={citySearch}
                  onChange={(e) => handleCitySearch(e.target.value)}
                  className="city-input"
                />
                <button
                  type="button"
                  className="gps-btn"
                  onClick={useGPSLocation}
                  title="Detect GPS Location"
                >
                  🎯 Use GPS
                </button>
              </div>

              {/* Geocoding Dropdown */}
              {searchResults.length > 0 && (
                <ul className="geocode-dropdown">
                  {searchResults.map((loc, i) => (
                    <li key={i} onClick={() => selectCity(loc)}>
                      📍 <strong>{loc.name}</strong> {loc.state ? `(${loc.state}, ${loc.country})` : `(${loc.country})`}
                    </li>
                  ))}
                </ul>
              )}

              {/* Popular City Pills */}
              <div className="city-pills">
                {POPULAR_CITIES.map((c, i) => (
                  <button
                    key={i}
                    type="button"
                    className={`city-pill ${form.lat === c.lat ? "active" : ""}`}
                    onClick={() => {
                      setForm({ ...form, lat: c.lat, lon: c.lon });
                      setCitySearch(c.name);
                    }}
                  >
                    {c.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Lat / Lon Display */}
            <div className="latlon-row">
              <label className="mini-field">
                <span>Latitude</span>
                <input
                  type="number"
                  name="lat"
                  value={form.lat}
                  onChange={handleChange}
                  step="0.0001"
                  required
                />
              </label>
              <label className="mini-field">
                <span>Longitude</span>
                <input
                  type="number"
                  name="lon"
                  value={form.lon}
                  onChange={handleChange}
                  step="0.0001"
                  required
                />
              </label>
            </div>

            {/* Soil NPK Sliders + Input */}
            <div className="soil-inputs-grid">
              <SoilInputRow
                label="Nitrogen (N)"
                sub="kg/ha"
                name="n"
                value={form.n}
                onChange={handleChange}
                min={0}
                max={140}
                color="#4E9F3D"
              />
              <SoilInputRow
                label="Phosphorus (P)"
                sub="kg/ha"
                name="p"
                value={form.p}
                onChange={handleChange}
                min={0}
                max={145}
                color="#D80032"
              />
              <SoilInputRow
                label="Potassium (K)"
                sub="kg/ha"
                name="k"
                value={form.k}
                onChange={handleChange}
                min={0}
                max={205}
                color="#F0A500"
              />
              <SoilInputRow
                label="Soil pH Level"
                sub="pH Scale"
                name="ph"
                value={form.ph}
                onChange={handleChange}
                min={3.5}
                max={10.0}
                step={0.1}
                color="#00ADB5"
              />
            </div>

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner"></span> Analyzing Soil & Live Weather…
                </>
              ) : (
                "✨ Recommend Optimal Crop"
              )}
            </button>
          </form>

          {error && <div className="error-banner">⚠️ {error}</div>}
        </section>

        {/* Right Side: Results & Weather */}
        <section className="result-card">
          {/* Live Weather Widget */}
          <div className="weather-widget">
            <div className="weather-header">
              <div>
                <span className="weather-location">
                  📍 {liveWeather ? `${liveWeather.city}, ${liveWeather.country}` : "Live Location Weather"}
                </span>
                <p className="weather-sub">Real-time OpenWeather Data</p>
              </div>
              {liveWeather && liveWeather.icon && (
                <img
                  src={`https://openweathermap.org/img/wn/${liveWeather.icon}@2x.png`}
                  alt={liveWeather.description}
                  className="weather-icon-img"
                />
              )}
            </div>

            {weatherLoading ? (
              <p className="loading-text">Fetching current weather data...</p>
            ) : liveWeather ? (
              <div className="weather-grid">
                <div className="w-stat">
                  <span className="w-val">{liveWeather.temperature}°C</span>
                  <span className="w-lbl">Temperature</span>
                </div>
                <div className="w-stat">
                  <span className="w-val">{liveWeather.humidity}%</span>
                  <span className="w-lbl">Humidity</span>
                </div>
                <div className="w-stat">
                  <span className="w-val">{liveWeather.rainfall} mm</span>
                  <span className="w-lbl">Rainfall (1h)</span>
                </div>
                <div className="w-stat">
                  <span className="w-val">{liveWeather.description}</span>
                  <span className="w-lbl">Condition</span>
                </div>
              </div>
            ) : (
              <p className="empty-text">Weather preview loading...</p>
            )}
          </div>

          {/* Recommendation Output */}
          {!result && !loading && (
            <div className="placeholder-state">
              <div className="placeholder-icon">🌾</div>
              <h3>Ready for Agronomic Analysis</h3>
              <p>
                Fill in your soil parameters on the left and click "Recommend Optimal Crop" to view real-time recommendations, fertilizer dosages, and risk warnings.
              </p>
            </div>
          )}

          {result && (
            <div className="recommendation-content">
              {/* Primary Crop Match Banner */}
              <div className="hero-crop-banner">
                <div className="crop-badge">{result.recommendation.type}</div>
                <div className="crop-title-row">
                  <span className="crop-emoji">{result.recommendation.icon}</span>
                  <div>
                    <h2 className="crop-main-name">{result.recommendation.recommended_crop}</h2>
                    <p className="crop-tamil-name">{result.recommendation.tamil_name}</p>
                  </div>
                </div>

                <div className="match-score-badge">
                  <div className="score-num">{result.recommendation.match_score}%</div>
                  <div className="score-lbl">Agronomic Match</div>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="tabs-nav">
                <button
                  className={`tab-btn ${activeTab === "overview" ? "active" : ""}`}
                  onClick={() => setActiveTab("overview")}
                >
                  📋 Overview
                </button>
                <button
                  className={`tab-btn ${activeTab === "fertilizer" ? "active" : ""}`}
                  onClick={() => setActiveTab("fertilizer")}
                >
                  🧪 Fertilizer & Soil Guide
                </button>
                <button
                  className={`tab-btn ${activeTab === "alerts" ? "active" : ""}`}
                  onClick={() => setActiveTab("alerts")}
                >
                  ⚠️ Weather & Risk Alerts
                </button>
                <button
                  className={`tab-btn ${activeTab === "alternatives" ? "active" : ""}`}
                  onClick={() => setActiveTab("alternatives")}
                >
                  🥈 Alternatives
                </button>
              </div>

              {/* Tab 1: Overview */}
              {activeTab === "overview" && (
                <div className="tab-panel animate-fade">
                  <p className="crop-desc">{result.recommendation.description}</p>

                  <div className="info-grid">
                    <div className="info-card">
                      <span className="info-icon">⏱️</span>
                      <div>
                        <strong>Growth Duration</strong>
                        <p>{result.recommendation.duration}</p>
                      </div>
                    </div>

                    <div className="info-card">
                      <span className="info-icon">💡</span>
                      <div>
                        <strong>Key Agronomic Tip</strong>
                        <p>{result.recommendation.tips}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Fertilizer & Soil Guide */}
              {activeTab === "fertilizer" && (
                <div className="tab-panel animate-fade">
                  <h3>Fertilizer & Soil Amendment Plan</h3>
                  <p className="subtext">Customized dosage calculated for your field's exact nutrient profile:</p>

                  <ul className="advisory-list">
                    {result.recommendation.fertilizer_advisory.map((item, i) => (
                      <li key={i} className="advisory-item">
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Tab 3: Weather & Risk Alerts */}
              {activeTab === "alerts" && (
                <div className="tab-panel animate-fade">
                  <h3>Real-Time Weather Risk Assessment</h3>
                  {result.recommendation.weather_alerts.length === 0 ? (
                    <div className="alert-box alert-success">
                      🟢 <strong>Optimal Climate Conditions:</strong> Temperature ({result.weather_used.temperature}°C) and Humidity ({result.weather_used.humidity}%) are within safe bounds for your crop.
                    </div>
                  ) : (
                    result.recommendation.weather_alerts.map((alert, i) => (
                      <div key={i} className="alert-box alert-warning">
                        {alert}
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Tab 4: Alternatives */}
              {activeTab === "alternatives" && (
                <div className="tab-panel animate-fade">
                  <h3>Runner-Up Crop Recommendations</h3>
                  <div className="runner-ups-grid">
                    {result.recommendation.runner_ups.map((c, i) => (
                      <div key={i} className="runner-card">
                        <span className="runner-icon">{c.icon}</span>
                        <div className="runner-info">
                          <strong>{c.crop}</strong>
                          <span className="runner-tamil">{c.tamil}</span>
                        </div>
                        <span className="runner-score">{c.score}% Match</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>
      </main>

      {/* Floating Chatbot Assistant Widget */}
      <ChatbotWidget soil={form} weather={liveWeather} result={result} />

      <footer className="agromix-footer">
        <p>🌾 Agromix AI — Empowering Farmers with Precision Weather & Soil Intelligence</p>
      </footer>
    </div>
  );
}

// Reusable Soil Slider + Number Input Row Component
function SoilInputRow({ label, sub, name, value, onChange, min, max, step = 1, color }) {
  return (
    <div className="soil-field-group">
      <div className="field-header">
        <label>
          {label} <span className="field-sub">({sub})</span>
        </label>
        <input
          type="number"
          name={name}
          value={value}
          onChange={onChange}
          min={min}
          max={max}
          step={step}
          className="number-input"
          required
        />
      </div>

      <input
        type="range"
        name={name}
        value={value || min}
        onChange={onChange}
        min={min}
        max={max}
        step={step}
        className="soil-slider"
        style={{ accentColor: color }}
      />
    </div>
  );
}

// AgriChat Floating AI Chatbot Widget Component
function ChatbotWidget({ soil, weather, result }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "🌾 *வணக்கம்! Welcome to Agromix Chatbot Assistant!*\nAsk me any question about fertilizers, pest control, soil pH, or crop management!",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen]);

  const sendMessage = async (textToSend) => {
    const query = textToSend || input;
    if (!query || query.trim() === "") return;

    const newMessages = [...messages, { sender: "user", text: query }];
    setMessages(newMessages);
    if (!textToSend) setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: query,
          soil: soil,
          weather: weather,
          recommended_crop: result?.recommendation?.recommended_crop || "",
        }),
      });

      const data = await res.json();
      if (res.ok && data.reply) {
        setMessages([...newMessages, { sender: "bot", text: data.reply }]);
      } else {
        setMessages([
          ...newMessages,
          { sender: "bot", text: "⚠️ Chatbot server error. Please try again." },
        ]);
      }
    } catch (e) {
      setMessages([
        ...newMessages,
        { sender: "bot", text: "⚠️ Unable to connect to backend chatbot server." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chatbot-wrapper">
      {/* Floating Toggle Button */}
      {!isOpen && (
        <button className="chat-launcher-btn" onClick={() => setIsOpen(true)}>
          <span className="chat-icon">💬</span>
          <span className="chat-label">AgriChat AI</span>
          <span className="online-dot"></span>
        </button>
      )}

      {/* Chatbot Window */}
      {isOpen && (
        <div className="chatbot-window animate-slide-up">
          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-title">
              <span className="bot-avatar">🤖</span>
              <div>
                <h4>Agromix AgriChat Assistant</h4>
                <span className="chat-status">🟢 Online • Bilingual AI</span>
              </div>
            </div>
            <button className="close-btn" onClick={() => setIsOpen(false)}>
              ✕
            </button>
          </div>

          {/* Quick Prompts */}
          <div className="quick-prompts">
            <button onClick={() => sendMessage("What fertilizer should I use?")}>
              🧪 Fertilizer Guide
            </button>
            <button onClick={() => sendMessage("How to control pests naturally?")}>
              🐛 Pest Control
            </button>
            <button onClick={() => sendMessage("Irrigation and rainfall tips?")}>
              🌧️ Irrigation
            </button>
            <button onClick={() => sendMessage("How to fix soil pH?")}>
              🌱 Soil pH
            </button>
          </div>

          {/* Message List */}
          <div className="chat-messages">
            {messages.map((m, idx) => (
              <div key={idx} className={`chat-bubble-row ${m.sender}`}>
                {m.sender === "bot" && <span className="bubble-avatar">🌾</span>}
                <div className={`chat-bubble ${m.sender}`}>
                  <div
                    className="chat-text"
                    dangerouslySetInnerHTML={{
                      __html: formatMarkdown(m.text),
                    }}
                  />
                </div>
              </div>
            ))}

            {loading && (
              <div className="chat-bubble-row bot">
                <span className="bubble-avatar">🌾</span>
                <div className="chat-bubble bot typing">
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="dot"></span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input Box */}
          <div className="chat-input-area">
            <textarea
              placeholder="Ask an agronomy question (e.g. fertilizer for rice)..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
            />
            <button
              className="send-btn"
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
            >
              🚀
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// Simple helper to format basic bold Markdown text and newlines into HTML safely
function formatMarkdown(text) {
  if (!text) return "";
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/\n/g, "<br/>");
  return html;
}
