import React from 'react';
import { Activity, AlertTriangle, ShieldCheck, Thermometer, Droplets, Clock, ArrowRight } from 'lucide-react';

export default function DashboardTab({ 
  lastResult, 
  temp, 
  humidity, 
  onTempChange, 
  onHumidityChange, 
  onGoToScanner 
}) {
  const h2sPpm = lastResult?.h2s_ppm ?? 0.0;
  const twa8hr = lastResult?.twa_8hr_ppm ?? 0.0;
  const alertLevel = lastResult?.alert_level || 'NORMAL';
  const alertsList = lastResult?.alerts || [];

  // Gauge bar calculation (0-100 ppm scale)
  const ppmPercent = Math.min(100, (h2sPpm / 100) * 100);
  const twaPercent = Math.min(100, (twa8hr / 20) * 100);

  return (
    <>
      {/* Alert Banner */}
      <div className={`status-banner ${alertLevel.toLowerCase()}`}>
        {alertLevel === 'CRITICAL' ? (
          <>
            <AlertTriangle size={20} />
            CRITICAL EXPOSURE ALERT DETECTED
          </>
        ) : alertLevel === 'WARNING' ? (
          <>
            <AlertTriangle size={20} />
            WARNING: SHIFT EXPOSURE ELEVATED
          </>
        ) : (
          <>
            <ShieldCheck size={20} />
            SAFE CONDITIONS — NORMAL MONITORING
          </>
        )}
      </div>

      {/* Main H2S Concentration Gauge Card */}
      <div className="card gauge-card">
        <div className="card-title-row">
          <span className="card-title">
            <Activity size={18} color="#38bdf8" /> Real-Time H₂S Concentration
          </span>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Random Forest ML</span>
        </div>

        <div className="ppm-value-big">
          {h2sPpm.toFixed(2)}
        </div>
        <div className="ppm-unit">Parts Per Million (ppm)</div>

        {/* Circular / Linear Progress Bar */}
        <div style={{ marginTop: '16px', background: 'rgba(30, 41, 59, 0.6)', borderRadius: '10px', padding: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#94a3b8', marginBottom: '6px' }}>
            <span>0 ppm</span>
            <span>Ceiling: 20 ppm</span>
            <span>Peak: 50 ppm</span>
            <span>100 ppm</span>
          </div>
          <div style={{ width: '100%', height: '10px', background: '#1e293b', borderRadius: '6px', overflow: 'hidden', position: 'relative' }}>
            <div style={{
              width: `${ppmPercent}%`,
              height: '100%',
              background: h2sPpm >= 50 ? 'linear-gradient(90deg, #f59e0b, #ef4444)' : h2sPpm >= 20 ? 'linear-gradient(90deg, #10b981, #f59e0b)' : 'linear-gradient(90deg, #3b82f6, #10b981)',
              borderRadius: '6px',
              transition: 'width 0.6s ease'
            }} />
          </div>
        </div>

        {alertsList.length > 0 && (
          <div style={{ marginTop: '12px', textAlign: 'left', background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '10px', borderRadius: '10px' }}>
            <div style={{ fontSize: '0.78rem', fontWeight: '700', color: '#f87171', marginBottom: '4px' }}>Active Threshold Triggers:</div>
            <ul style={{ paddingLeft: '18px', fontSize: '0.75rem', color: '#fca5a5' }}>
              {alertsList.map((a, idx) => <li key={idx}>{a}</li>)}
            </ul>
          </div>
        )}
      </div>

      {/* Grid Metrics (8-hr TWA) */}
      <div className="metrics-grid" style={{ gridTemplateColumns: '1fr' }}>
        <div className="metric-box">
          <div className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Clock size={16} color="#38bdf8" /> 8-Hour TWA Equivalent
          </div>
          <div className="metric-value" style={{ color: twa8hr >= 10 ? '#f87171' : '#38bdf8', fontSize: '1.5rem' }}>
            {twa8hr.toFixed(2)} <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>ppm</span>
          </div>
          <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '2px' }}>OSHA / ACGIH Standard Limit: 10.00 ppm 8-hr TWA</div>
        </div>
      </div>

      {/* Environmental Controls Card */}
      <div className="card">
        <span className="card-title">Ambient Environmental Parameters</span>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Thermometer size={14} color="#ef4444" /> Temperature (°C)
            </label>
            <input 
              type="number" 
              className="form-input" 
              value={temp} 
              onChange={(e) => onTempChange(e.target.value)} 
            />
          </div>

          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Droplets size={14} color="#06b6d4" /> Humidity (%)
            </label>
            <input 
              type="number" 
              className="form-input" 
              value={humidity} 
              onChange={(e) => onHumidityChange(e.target.value)} 
            />
          </div>
        </div>
      </div>

      {/* Action Button */}
      <button className="btn-primary" onClick={onGoToScanner}>
        <Activity size={18} /> Perform New Band Scan <ArrowRight size={16} />
      </button>
    </>
  );
}
