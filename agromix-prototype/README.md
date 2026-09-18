# Agromix — Prototype (Flask + React + Twilio)

## 🔑 Where does the API key go?

`backend/.env.example` → copy pannunga → rename to `backend/.env` → adhula unga
OpenWeatherMap key paste pannunga.

```
backend/.env          ← REAL key inga irukkanum (this file is git-ignored)
backend/.env.example  ← template only, git ku push aagalam
```

`backend/.env` file content:
```
OPENWEATHER_API_KEY=your_actual_key_here
```

Idha thavira vera engayume (App.jsx, index.js) key podathinga — frontend code la key vecha, browser la anybody ku andha key theriyum (security risk).

## Folder structure

```
agromix-prototype/
├── backend/
│   ├── app.py              ← Flask API (weather, crop recommend, Twilio webhook)
│   ├── .env.example        ← copy this to .env and add your key
│   ├── .gitignore
│   └── requirements.txt
└── frontend/
    ├── public/index.html
    ├── src/
    │   ├── App.jsx          ← main UI (form + result panel)
    │   ├── App.css
    │   ├── index.js
    │   └── index.css
    └── package.json
```

## How to run

### 1. Backend (Flask)
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env and paste your real key
python app.py
```
Backend runs at `http://localhost:5000`.

### 2. Frontend (React)
```bash
cd frontend
npm install
npm start
```
Frontend runs at `http://localhost:3000` and calls the backend automatically.

### 3. Twilio (optional, for WhatsApp/SMS)
1. console.twilio.com → WhatsApp Sandbox
2. Set the webhook URL to `https://<your-ngrok-or-deployed-url>/whatsapp`
3. Test locally with `ngrok http 5000`

## Notes
- `suggest_crop()` in `app.py` is a placeholder rule. Swap it for your trained
  `crop_model.pkl` (scikit-learn) once ready — just `joblib.load()` it and
  call `.predict()` instead.
- CORS is already enabled so the React dev server (port 3000) can call the
  Flask API (port 5000) without extra config.
