import React from 'react';
import { Cpu, Grid, Sliders, Layers } from 'lucide-react';

export default function FeatureExtractionTab({ lastResult }) {
  const sensors = lastResult?.sensor_details || {
    S1: { hue: 42.5, saturation: 68.4, value: 85.1, delta_e: 14.8, gradient: 2.5 },
    S2: { hue: 44.1, saturation: 58.2, value: 88.0, delta_e: 11.2, gradient: 0.9 },
    S3: { hue: 45.0, saturation: 51.5, value: 89.6, delta_e: 5.4, gradient: 0.0 }
  };

  const features = lastResult?.features || {};

  return (
    <>
      {/* ROI Debug Bounding Boxes Card */}
      <div className="card">
        <div className="card-title-row">
          <span className="card-title">
            <Grid size={18} color="#06b6d4" /> Fixed ROI Coordinates Visualizer
          </span>
          <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>10 Standard ROIs</span>
        </div>

        {lastResult?.roi_debug_image ? (
          <img 
            src={lastResult.roi_debug_image} 
            alt="ROI Debug Bounding Boxes" 
            style={{ width: '100%', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.1)' }} 
          />
        ) : (
          <div style={{ background: '#0f172a', padding: '20px', borderRadius: '10px', textTransform: 'center', fontSize: '0.8rem', color: '#64748b' }}>
            Run a scan to generate the visual ROI detection overlay.
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', marginTop: '8px' }}>
          <div style={{ padding: '6px 8px', background: 'rgba(168, 85, 247, 0.15)', border: '1px solid rgba(168, 85, 247, 0.3)', borderRadius: '6px', fontSize: '0.68rem', color: '#c084fc', textAlign: 'center' }}>
            5 Printed Ref Colors
          </div>
          <div style={{ padding: '6px 8px', background: 'rgba(56, 189, 248, 0.15)', border: '1px solid rgba(56, 189, 248, 0.3)', borderRadius: '6px', fontSize: '0.68rem', color: '#38bdf8', textAlign: 'center' }}>
            S1/S2/S3 Cu-PAN
          </div>
          <div style={{ padding: '6px 8px', background: 'rgba(236, 72, 153, 0.15)', border: '1px solid rgba(236, 72, 153, 0.3)', borderRadius: '6px', fontSize: '0.68rem', color: '#f472b6', textAlign: 'center' }}>
            Expiry & Band ID
          </div>
        </div>
      </div>

      {/* Sensor Segments Breakdown Cards (S1, S2, S3) */}
      <div className="card">
        <span className="card-title">
          <Layers size={18} color="#3b82f6" /> Cu-PAN Sensing Segments Extraction
        </span>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {/* Segment 1 */}
          <div style={{ background: 'rgba(30, 41, 59, 0.6)', padding: '12px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: '700', color: '#38bdf8' }}>Segment 1 (S1) — Open Membrane</span>
              <span style={{ fontSize: '0.78rem', fontWeight: '700', color: '#34d399' }}>ΔE = {sensors.S1.delta_e}</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '6px', fontSize: '0.72rem', color: '#94a3b8' }}>
              <div>Hue: <span style={{ color: '#fff', fontWeight: '600' }}>{sensors.S1.hue}°</span></div>
              <div>Sat: <span style={{ color: '#fff', fontWeight: '600' }}>{sensors.S1.saturation}%</span></div>
              <div>Val: <span style={{ color: '#fff', fontWeight: '600' }}>{sensors.S1.value}%</span></div>
              <div>Grad: <span style={{ color: '#fff', fontWeight: '600' }}>{sensors.S1.gradient}</span></div>
            </div>
          </div>

          {/* Segment 2 */}
          <div style={{ background: 'rgba(30, 41, 59, 0.6)', padding: '12px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: '700', color: '#38bdf8' }}>Segment 2 (S2) — 0.22 µm PTFE</span>
              <span style={{ fontSize: '0.78rem', fontWeight: '700', color: '#34d399' }}>ΔE = {sensors.S2.delta_e}</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '6px', fontSize: '0.72rem', color: '#94a3b8' }}>
              <div>Hue: <span style={{ color: '#fff', fontWeight: '600' }}>{sensors.S2.hue}°</span></div>
              <div>Sat: <span style={{ color: '#fff', fontWeight: '600' }}>{sensors.S2.saturation}%</span></div>
              <div>Val: <span style={{ color: '#fff', fontWeight: '600' }}>{sensors.S2.value}%</span></div>
              <div>Grad: <span style={{ color: '#fff', fontWeight: '600' }}>{sensors.S2.gradient}</span></div>
            </div>
          </div>

          {/* Segment 3 */}
          <div style={{ background: 'rgba(30, 41, 59, 0.6)', padding: '12px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: '700', color: '#38bdf8' }}>Segment 3 (S3) — 0.10 µm PTFE</span>
              <span style={{ fontSize: '0.78rem', fontWeight: '700', color: '#34d399' }}>ΔE = {sensors.S3.delta_e}</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '6px', fontSize: '0.72rem', color: '#94a3b8' }}>
              <div>Hue: <span style={{ color: '#fff', fontWeight: '600' }}>{sensors.S3.hue}°</span></div>
              <div>Sat: <span style={{ color: '#fff', fontWeight: '600' }}>{sensors.S3.saturation}%</span></div>
              <div>Val: <span style={{ color: '#fff', fontWeight: '600' }}>{sensors.S3.value}%</span></div>
              <div>Grad: <span style={{ color: '#fff', fontWeight: '600' }}>{sensors.S3.gradient}</span></div>
            </div>
          </div>
        </div>
      </div>

      {/* Complete 17-Feature Vector Table */}
      <div className="card">
        <span className="card-title">
          <Sliders size={18} color="#f59e0b" /> Complete 17-Feature Machine Learning Input Vector
        </span>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.75rem', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#94a3b8' }}>
                <th style={{ padding: '8px' }}>Feature Name</th>
                <th style={{ padding: '8px' }}>Extracted Value</th>
                <th style={{ padding: '8px' }}>Reference</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(features).map(([k, v]) => (
                <tr key={k} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                  <td style={{ padding: '6px 8px', color: '#cbd5e1', fontWeight: '600' }}>{k}</td>
                  <td style={{ padding: '6px 8px', color: '#38bdf8', fontFamily: 'JetBrains Mono, monospace' }}>
                    {typeof v === 'number' ? v.toFixed(2) : v}
                  </td>
                  <td style={{ padding: '6px 8px', color: '#64748b' }}>
                    {k.includes('Hue') ? 'Degrees (0-360)' : k.includes('Saturation') || k.includes('Value') || k.includes('Percent') ? '%' : k.includes('Temperature') ? '°C' : 'CIE76 / Abs'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
