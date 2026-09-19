import React from 'react';
import { TrendingUp, AlertTriangle, ShieldCheck, Calendar, Activity, BarChart2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export default function LongTermTab({ historyAnalytics }) {
  const weeklyDose = historyAnalytics?.weekly_dose ?? 14.5;
  const monthlyTwa = historyAnalytics?.monthly_twa ?? 0.38;
  const rotationDose = historyAnalytics?.rotation_dose ?? 32.0;

  // Threshold criteria evaluation
  const isWeeklyAction = weeklyDose >= 20.0;
  const isMonthlyAction = monthlyTwa >= 0.5;
  const isRotationAction = rotationDose >= 40.0;

  const longTermAlertRequired = isWeeklyAction || isMonthlyAction || isRotationAction;

  // Sample weekly shift dataset for interactive BarChart visualizer
  const weeklyData = [
    { day: 'Mon', shiftDose: 4.2 },
    { day: 'Tue', shiftDose: 5.8 },
    { day: 'Wed', shiftDose: 3.1 },
    { day: 'Thu', shiftDose: 6.4 },
    { day: 'Fri', shiftDose: 4.0 },
    { day: 'Sat', shiftDose: 2.5 },
    { day: 'Sun', shiftDose: 1.2 }
  ];

  return (
    <>
      {/* Long Term Decision Engine Banner */}
      <div className={`status-banner ${longTermAlertRequired ? 'warning' : 'normal'}`}>
        {longTermAlertRequired ? (
          <>
            <AlertTriangle size={20} />
            LONG-TERM EXPOSURE ACTION REQUIRED
          </>
        ) : (
          <>
            <ShieldCheck size={20} />
            LONG-TERM DOSIMETRY WITHIN NORMAL BOUNDS
          </>
        )}
      </div>

      {/* Long Term Summary Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
        <div className="metric-box" style={{ textAlign: 'center' }}>
          <div className="metric-label">Weekly Dose</div>
          <div className="metric-value" style={{ color: isWeeklyAction ? '#f87171' : '#38bdf8' }}>
            {weeklyDose.toFixed(1)}
          </div>
          <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>ppm·hr (Limit: 20)</div>
        </div>

        <div className="metric-box" style={{ textAlign: 'center' }}>
          <div className="metric-label">Monthly TWA</div>
          <div className="metric-value" style={{ color: isMonthlyAction ? '#f87171' : '#34d399' }}>
            {monthlyTwa.toFixed(2)}
          </div>
          <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>ppm (Limit: 0.5)</div>
        </div>

        <div className="metric-box" style={{ textAlign: 'center' }}>
          <div className="metric-label">Rotation Dose</div>
          <div className="metric-value" style={{ color: isRotationAction ? '#f87171' : '#fbbf24' }}>
            {rotationDose.toFixed(1)}
          </div>
          <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>ppm·hr (Limit: 40)</div>
        </div>
      </div>

      {/* Interactive Weekly Shift Dose Chart */}
      <div className="card">
        <div className="card-title-row">
          <span className="card-title">
            <BarChart2 size={18} color="#3b82f6" /> Weekly Accumulated Shift Dose (Σ Shift Dose)
          </span>
          <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>7-Day Rolling</span>
        </div>

        <div style={{ width: '100%', height: 220, marginTop: '10px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={weeklyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <XAxis dataKey="day" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
              <Tooltip 
                contentStyle={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}
                formatter={(val) => [`${val} ppm·hr`, 'Shift Exposure']}
              />
              <ReferenceLine y={5.0} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: 'Warn', fill: '#f59e0b', fontSize: 10 }} />
              <Bar dataKey="shiftDose" fill="#3b82f6" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Long-Term Threshold Rules Evaluation Table */}
      <div className="card">
        <span className="card-title">
          <Calendar size={18} color="#06b6d4" /> Long-Term Occupational Health Limits
        </span>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: 'rgba(30,41,59,0.5)', borderRadius: '8px' }}>
            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: '700', color: '#f8fafc' }}>Weekly Action Level</div>
              <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Σ Shift Dose over 7 days &ge; 20.0 ppm·hr</div>
            </div>
            <span style={{ fontSize: '0.8rem', fontWeight: '700', color: isWeeklyAction ? '#f87171' : '#34d399' }}>
              {isWeeklyAction ? 'ACTION REQUIRED' : 'PASS'}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: 'rgba(30,41,59,0.5)', borderRadius: '8px' }}>
            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: '700', color: '#f8fafc' }}>Monthly Weighted TWA</div>
              <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Weighted TWA over 30 days &ge; 0.50 ppm</div>
            </div>
            <span style={{ fontSize: '0.8rem', fontWeight: '700', color: isMonthlyAction ? '#f87171' : '#34d399' }}>
              {isMonthlyAction ? 'ACTION REQUIRED' : 'PASS'}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px', background: 'rgba(30,41,59,0.5)', borderRadius: '8px' }}>
            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: '700', color: '#f8fafc' }}>Rotational Reference Dose</div>
              <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>Σ Shift Dose over 84 hours &ge; 40.0 ppm·hr</div>
            </div>
            <span style={{ fontSize: '0.8rem', fontWeight: '700', color: isRotationAction ? '#f87171' : '#34d399' }}>
              {isRotationAction ? 'ACTION REQUIRED' : 'PASS'}
            </span>
          </div>
        </div>
      </div>
    </>
  );
}
