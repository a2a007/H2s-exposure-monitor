import React, { useState, useEffect } from 'react';
import AndroidHeader from './components/AndroidHeader';
import BottomNav from './components/BottomNav';
import DashboardTab from './components/DashboardTab';
import ScannerTab from './components/ScannerTab';
import FeatureExtractionTab from './components/FeatureExtractionTab';
import LongTermTab from './components/LongTermTab';
import HistoryTab from './components/HistoryTab';
import ReportModal from './components/ReportModal';
import EmployeeModal from './components/EmployeeModal';
import { getActiveEmployee, setActiveEmployee, getLocalHistory, saveLocalHistoryRecord } from './utils/storage';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [viewMode, setViewMode] = useState('frame');
  const [isOnline, setIsOnline] = useState(false);
  const [activeEmp, setActiveEmp] = useState(getActiveEmployee());
  
  const [temp, setTemp] = useState(32.0);
  const [humidity, setHumidity] = useState(65.0);
  const [scanning, setScanning] = useState(false);
  
  const [lastResult, setLastResult] = useState({
    h2s_ppm: 8.45,
    exposure_hours: 8.0,
    shift_exposure_ppm_hr: 67.6,
    twa_8hr_ppm: 8.45,
    alert_level: 'NORMAL',
    alerts: [],
    sensor_details: {
      S1: { hue: 42.5, saturation: 68.4, value: 85.1, delta_e: 14.8, gradient: 2.5 },
      S2: { hue: 44.1, saturation: 58.2, value: 88.0, delta_e: 11.2, gradient: 0.9 },
      S3: { hue: 45.0, saturation: 51.5, value: 89.6, delta_e: 5.4, gradient: 0.0 }
    },
    features: {
      "S1_Hue": 42.5, "S1_Saturation": 68.4, "S1_Value": 85.1, "S1_DeltaE": 14.8, "S1_Gradient": 2.5,
      "S2_Hue": 44.1, "S2_Saturation": 58.2, "S2_Value": 88.0, "S2_DeltaE": 11.2, "S2_Gradient": 0.9,
      "S3_Hue": 45.0, "S3_Saturation": 51.5, "S3_Value": 89.6, "S3_DeltaE": 5.4, "S3_Gradient": 0.0,
      "Temperature_C": 32.0, "Humidity_Percent": 65.0
    },
    quality: {
      blur_pass: true, blur_score: 184.2, lighting_pass: true, brightness: 125.0, all_markers_found: true, markers_count: 4
    }
  });

  const [historyAnalytics, setHistoryAnalytics] = useState({
    records: getLocalHistory(),
    weekly_dose: 14.5,
    monthly_twa: 0.38,
    rotation_dose: 32.0
  });

  const [isReportOpen, setIsReportOpen] = useState(false);
  const [isEmpModalOpen, setIsEmpModalOpen] = useState(false);

  const checkStatus = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/status');
      if (res.ok) {
        setIsOnline(true);
        fetchHistory();
      } else {
        setIsOnline(false);
      }
    } catch (e) {
      setIsOnline(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/history');
      if (res.ok) {
        const data = await res.json();
        setHistoryAnalytics(data);
      }
    } catch (e) {
      console.log("History fetch fallback:", e);
    }
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectEmployee = (emp) => {
    setActiveEmp(emp);
    setActiveEmployee(emp);
  };

  const handleRunScan = async (imageB64) => {
    setScanning(true);
    try {
      // Always attempt to send request to Python backend model server first
      try {
        const res = await fetch('http://localhost:5000/api/scan', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image: imageB64 || '',
            temperature: parseFloat(temp),
            humidity: parseFloat(humidity),
            exposure_hours: parseFloat(activeEmp.durationHours),
            employee_id: activeEmp.id,
            band_id: activeEmp.bandId,
            shift_info: activeEmp.shift
          })
        });

        const result = await res.json().catch(() => null);

        if (res.ok && result && result.success !== false) {
          setIsOnline(true);
          setLastResult(result);
          await fetchHistory();
          setActiveTab('dashboard');
          return;
        } else if (result && result.success === false) {
          setIsOnline(true);
          setLastResult(result);
          alert(`⚠️ ArUco Marker Verification Failed!\n\n${result.error_message || 'Only ' + (result.quality?.markers_count || 0) + '/4 reference markers detected. Image processing stopped for safety.'}`);
          return;
        } else {
          console.warn("API returned non-200 status:", res.status);
        }
      } catch (netErr) {
        setIsOnline(false);
        alert("❌ Python Backend Disconnected!\n\nPlease start the Python server in your terminal:\n   python -u server.py 5000\n\nImage scan analysis requires the live OpenCV + Random Forest ML server.");
      }
    } catch (err) {
      console.error("Scan error:", err);
      alert("Error processing image scan: " + err.message);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className={`android-device-shell mode-${viewMode}`}>
      {/* Top Header */}
      <AndroidHeader
        isOnline={isOnline}
        activeEmp={activeEmp}
        onSelectEmp={() => setIsEmpModalOpen(true)}
        alertLevel={lastResult?.alert_level || 'NORMAL'}
        viewMode={viewMode}
        onToggleViewMode={() => setViewMode(v => v === 'frame' ? 'desktop' : 'frame')}
      />

      {/* Main App Content Viewport */}
      <div className="main-content">
        {activeTab === 'dashboard' && (
          <DashboardTab
            lastResult={lastResult}
            temp={temp}
            humidity={humidity}
            onTempChange={setTemp}
            onHumidityChange={setHumidity}
            onGoToScanner={() => setActiveTab('scanner')}
          />
        )}

        {activeTab === 'scanner' && (
          <ScannerTab
            onRunScan={handleRunScan}
            scanning={scanning}
            lastResult={lastResult}
          />
        )}

        {activeTab === 'features' && (
          <FeatureExtractionTab
            lastResult={lastResult}
          />
        )}

        {activeTab === 'analytics' && (
          <LongTermTab
            historyAnalytics={historyAnalytics}
          />
        )}

        {activeTab === 'history' && (
          <HistoryTab
            historyAnalytics={historyAnalytics}
            onOpenReport={() => setIsReportOpen(true)}
          />
        )}
      </div>

      {/* Bottom Navigation */}
      <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Modals */}
      <ReportModal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        activeEmp={activeEmp}
        lastResult={lastResult}
        historyAnalytics={historyAnalytics}
      />

      <EmployeeModal
        isOpen={isEmpModalOpen}
        onClose={() => setIsEmpModalOpen(false)}
        activeEmp={activeEmp}
        onSelectEmp={handleSelectEmployee}
      />
    </div>
  );
}
