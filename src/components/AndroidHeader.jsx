import React from 'react';
import { ShieldAlert, Wifi, WifiOff, User, Smartphone, Monitor } from 'lucide-react';

export default function AndroidHeader({ 
  isOnline, 
  activeEmp, 
  onSelectEmp, 
  alertLevel, 
  viewMode, 
  onToggleViewMode 
}) {
  const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <>
      {/* Android Top System Bar */}
      <div className="android-status-bar">
        <span>{currentTime}</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {isOnline ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#34d399' }}>
              <Wifi size={12} /> REST API Connected
            </span>
          ) : (
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#fbbf24' }}>
              <WifiOff size={12} /> Local Offline Mode
            </span>
          )}
          <button 
            onClick={onToggleViewMode}
            title={viewMode === 'frame' ? "Switch to Wide Mode" : "Switch to Mobile Phone View"}
            style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '2px' }}
          >
            {viewMode === 'frame' ? <Monitor size={13} /> : <Smartphone size={13} />}
          </button>
        </div>
      </div>

      {/* Main Android App Top Bar */}
      <div className="android-header">
        <div className="header-top">
          <div className="app-title-group">
            <div className="app-icon">
              <ShieldAlert size={22} color="#ffffff" />
            </div>
            <div>
              <h1>H₂S Monitor</h1>
              <div className="app-subtitle">Exposure Monitoring OS</div>
            </div>
          </div>

          <div className={`status-badge ${alertLevel.toLowerCase() === 'normal' ? 'online' : 'offline'}`}>
            <span style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              backgroundColor: alertLevel === 'CRITICAL' ? '#ef4444' : alertLevel === 'WARNING' ? '#f59e0b' : '#10b981'
            }} />
            {alertLevel}
          </div>
        </div>

        {/* Employee Switcher Strip */}
        <div className="employee-strip">
          <div className="emp-info">
            <div className="emp-avatar">
              {activeEmp.name.split(' ').map(n => n[0]).join('')}
            </div>
            <div className="emp-details">
              <span className="emp-name">{activeEmp.name} ({activeEmp.id})</span>
              <span className="emp-meta">Band: {activeEmp.bandId} | {activeEmp.shift} ({activeEmp.durationHours}h)</span>
            </div>
          </div>
          <button className="btn-secondary" style={{ padding: '4px 10px', fontSize: '0.72rem' }} onClick={onSelectEmp}>
            <User size={12} /> Switch
          </button>
        </div>
      </div>
    </>
  );
}
