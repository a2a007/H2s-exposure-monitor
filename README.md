# H2S Exposure Monitoring System 🛡️⚡

An industrial-grade Hydrogen Sulfide ($H_2S$) wearable band optical scanner, exposure calculator, and workplace safety management dashboard. This application combines **Computer Vision (OpenCV)**, **Machine Learning (Random Forest Regressor)**, and a **Mobile-First React Dashboard** to measure worker gas exposure in real time, enforce workplace safety thresholds, and track historical cumulative doses.

---

## 🌟 Key Features

- 📸 **Computer Vision Alignment & Color Calibration**:
  - **ArUco Marker Verification**: Automatically detects 4 corner $4\times 4$ ArUco reference markers to perform perspective transformation and crop/align the exposure band image ($1200\times 300\text{ px}$).
  - **Homography Color Correction**: Uses 5 reference color swatches (purple, amber, yellow, white, gray) to generate a homography matrix for dynamic lighting and camera calibration.
  - **CIELAB $\Delta E$ Feature Extraction**: Extracts HSV color properties, color gradients, and $\Delta E$ color differences across 3 distinct sensor regions (S1, S2, S3).

- 🤖 **Machine Learning $H_2S$ Concentration Quantitation**:
  - Utilizes a pre-trained **Random Forest Regressor** model (`H2S_total_exposure_random_forest_datasetNew.joblib`) taking sensor color metrics ($\text{Hue}$, $\text{Saturation}$, $\text{Value}$, $\Delta E$, $\text{Gradient}$) along with ambient conditions ($\text{Temperature }^\circ\text{C}$, $\text{Humidity }\%$) to predict $H_2S$ concentration (ppm).

- 🚨 **Real-Time Safety Thresholds & OSHA/NIOSH Alerts**:
  - **IDLH Alert**: $\ge 100\text{ ppm}$ (Immediately Dangerous to Life or Health).
  - **Peak Alert**: $> 50\text{ ppm}$.
  - **Ceiling Alert**: $> 20\text{ ppm}$.
  - **8-Hour TWA Warning**: Accumulated 8-hr Time-Weighted Average $> 10\text{ ppm}$.

- 📊 **Interactive Mobile & Web Dashboard**:
  - **Scanner Tab**: Real-time camera scan simulation / image upload, lighting & blur quality score checks, ambient environment inputs, and band/employee selection.
  - **Dashboard Tab**: Immediate status indicators, concentration gauges, 8-hour TWA calculations, and active safety alerts.
  - **Feature Extraction Tab**: Deep dive into color channels (HSV, $\Delta E$, gradient) and view raw vs. color-calibrated region-of-interest (ROI) output images.
  - **History & Analytics Tabs**: Exposure log tracking, cumulative weekly dose, 30-day weighted TWA, 84-hour rotation dosage, and trends via Recharts.
  - **PDF & CSV Export**: Download complete exposure history as CSV or export formatted worker safety PDF reports.

---

## 🏗️ System Architecture

```
                               ┌────────────────────────────────────────┐
                               │       React Frontend (Vite)            │
                               │  (Mobile Android UI & Web Dashboard)   │
                               └───────────────────┬────────────────────┘
                                                   │
                                            HTTP / REST API
                                                   │
                               ┌───────────────────▼────────────────────┐
                               │      Python Backend API (server.py)     │
                               └─────────┬────────────────────┬─────────┘
                                         │                    │
                        ┌────────────────┴───────┐   ┌────────┴──────────────┐
                        │    OpenCV Pipeline     │   │   Random Forest ML    │
                        │ • ArUco Alignment      │   │ • 17 Input Features   │
                        │ • Color Swatch Homogr. │   │ • H2S (ppm) Predict   │
                        │ • CIELAB ΔE Extraction │   └───────────────────────┘
                        └────────────────────────┘
```

---

## 📁 Directory Structure

```
.
├── server.py                                  # Python HTTP API Server (OpenCV + ML + Data Storage)
├── H2S_total_exposure_random_forest_datasetNew.joblib  # Pre-trained Random Forest ML Model
├── sample.png                                 # Default sample exposure band test image
├── package.json                               # Node.js dependencies & scripts
├── vite.config.js                             # Vite configuration
├── index.html                                 # Web entry point
├── src/
│   ├── App.jsx                                # Main application container & tab routing
│   ├── main.jsx                               # React DOM root entry
│   ├── index.css                              # Custom CSS styling (Android Mobile layout)
│   ├── components/
│   │   ├── AndroidHeader.jsx                  # Top Android-style app bar with status indicators
│   │   ├── BottomNav.jsx                      # Navigation tabs bar
│   │   ├── DashboardTab.jsx                   # Overview dashboard & alert gauges
│   │   ├── ScannerTab.jsx                     # Image scanner, quality checks, & parameters
│   │   ├── FeatureExtractionTab.jsx           # Sensor color analysis & ROI debugging
│   │   ├── HistoryTab.jsx                     # Exposure log table & CSV export
│   │   ├── LongTermTab.jsx                    # Cumulative dosage analytics & Recharts
│   │   ├── EmployeeModal.jsx                  # Worker profile switcher
│   │   └── ReportModal.jsx                    # PDF worker safety report viewer
│   └── utils/
│       └── storage.js                         # Local storage persistent state management
└── output/
    └── history/
        └── exposure_history.csv               # Historical scan records database
```

---

## 🛠️ Prerequisites & Installation

### Requirements
- **Python**: `3.8+`
- **Node.js**: `18.x` or higher
- **npm**: `9.x` or higher

### 1. Python Backend Setup

Install the required Python dependencies:

```bash
pip install opencv-python pandas numpy joblib
```

### 2. Frontend Setup

Install Node modules:

```bash
npm install
```

---

## 🚀 Running the Application

### Step 1: Start the Python API Server

Run the backend server on port `5000` (default):

```bash
python server.py
```

*Or specify a custom port:*
```bash
python server.py 5000
```

The server will print startup status and listen for incoming HTTP API requests at `http://localhost:5000`.

### Step 2: Start the Development UI

In a separate terminal window, launch the Vite dev server:

```bash
npm run dev
```

Open your browser at `http://localhost:5173` (or the URL provided by Vite).

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/status` | Returns system online status, OpenCV version, and ML model loaded flag |
| `POST` | `/api/scan` | Processes base64 band image, runs ArUco alignment, calculates HSV/$\Delta E$, runs ML prediction, returns alerts & debug images |
| `GET` | `/api/history` | Fetches historical scan logs and calculated dosage analytics (weekly dose, monthly TWA, rotation dose) |
| `POST` | `/api/history/add` | Manually appends an exposure log record |
| `GET` | `/api/history/download` | Downloads `exposure_history.csv` |

---

## ⚠️ Safety Threshold Reference

| Level | Concentration / TWA | Action / Description |
| :--- | :--- | :--- |
| **NORMAL** | $< 10\text{ ppm}$ | Safe operational levels. |
| **WARNING** | $> 20\text{ ppm}$ (Ceiling) or $> 10\text{ ppm}$ (8-hr TWA) | Ceiling exceeded or accumulated shift dosage high. Evacuate or wear respiratory protection. |
| **CRITICAL** | $> 50\text{ ppm}$ (Peak) or $\ge 100\text{ ppm}$ (IDLH) | Immediate life-threatening hazard. Mandatory emergency evacuation protocol. |

---

## 📜 License

This project is licensed for industrial workplace safety & exposure monitoring research.
