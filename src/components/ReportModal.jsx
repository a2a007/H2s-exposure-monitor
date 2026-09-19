import React from 'react';
import { X, Printer, Download, ShieldCheck, ShieldAlert } from 'lucide-react';
import jsPDF from 'jspdf';

export default function ReportModal({ isOpen, onClose, activeEmp, lastResult, historyAnalytics }) {
  if (!isOpen) return null;

  const records = historyAnalytics?.records || [];
  const empRecords = records.filter(r => r.Employee_ID === activeEmp.id || !r.Employee_ID);

  const downloadPdfReport = () => {
    const doc = new jsPDF();
    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text("H2S EXPOSURE MONITORING SYSTEM — AUDIT REPORT", 14, 20);

    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 28);
    doc.text(`Employee Name: ${activeEmp.name} (${activeEmp.id})`, 14, 34);
    doc.text(`Band ID: ${activeEmp.bandId} | Shift: ${activeEmp.shift}`, 14, 40);

    doc.line(14, 44, 196, 44);

    doc.setFont("helvetica", "bold");
    doc.text("CURRENT SHIFT SUMMARY", 14, 52);
    doc.setFont("helvetica", "normal");
    doc.text(`Current H2S Concentration: ${lastResult?.h2s_ppm || 0} ppm`, 14, 60);
    doc.text(`Shift Exposure Dose: ${lastResult?.shift_exposure_ppm_hr || 0} ppm.hr`, 14, 66);
    doc.text(`8-Hour Equivalent TWA: ${lastResult?.twa_8hr_ppm || 0} ppm`, 14, 72);
    doc.text(`Status: ${lastResult?.alert_level || 'NORMAL'}`, 14, 78);

    doc.line(14, 84, 196, 84);

    doc.setFont("helvetica", "bold");
    doc.text("LONG-TERM DOSIMETRY METRICS", 14, 92);
    doc.setFont("helvetica", "normal");
    doc.text(`Weekly Accumulated Dose (7 days): ${historyAnalytics?.weekly_dose || 0} ppm.hr`, 14, 100);
    doc.text(`Monthly Weighted TWA (30 days): ${historyAnalytics?.monthly_twa || 0} ppm`, 14, 106);
    doc.text(`Rotational Exposure Dose (84 hours): ${historyAnalytics?.rotation_dose || 0} ppm.hr`, 14, 112);

    doc.line(14, 118, 196, 118);

    doc.setFont("helvetica", "bold");
    doc.text("RECENT SCAN LOGS", 14, 126);

    let y = 134;
    doc.setFontSize(9);
    empRecords.slice(0, 10).forEach((rec, i) => {
      doc.text(`${rec.Timestamp || ''} | H2S: ${rec.H2S_Concentration_ppm} ppm | Dose: ${rec.Shift_Exposure_ppm_hr} ppm.hr | Status: ${rec.Alert_Status}`, 14, y);
      y += 6;
    });

    doc.save(`H2S_Exposure_Report_${activeEmp.id}_${Date.now()}.pdf`);
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.85)',
      backdropFilter: 'blur(8px)',
      zIndex: 100,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '16px'
    }}>
      <div style={{
        background: '#0f172a',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: '20px',
        width: '100%',
        maxWidth: '540px',
        maxHeight: '90vh',
        overflowY: 'auto',
        padding: '24px',
        color: '#f8fafc',
        position: 'relative'
      }}>
        <button 
          onClick={onClose} 
          style={{ position: 'absolute', top: '16px', right: '16px', background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
        >
          <X size={20} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <ShieldAlert size={28} color="#38bdf8" />
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: '800' }}>Official Employee Exposure Report</h2>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Occupational Safety Audit Document</div>
          </div>
        </div>

        <div style={{ background: 'rgba(30,41,59,0.5)', padding: '14px', borderRadius: '12px', fontSize: '0.82rem', marginBottom: '16px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div><strong>Employee:</strong> {activeEmp.name} ({activeEmp.id})</div>
          <div><strong>Department:</strong> {activeEmp.department}</div>
          <div><strong>Band ID:</strong> {activeEmp.bandId} | Shift: {activeEmp.shift}</div>
          <div><strong>Timestamp:</strong> {new Date().toLocaleString()}</div>
        </div>

        <div style={{ marginBottom: '16px' }}>
          <h3 style={{ fontSize: '0.9rem', color: '#38bdf8', marginBottom: '8px' }}>Current Shift Readings</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.8rem' }}>
            <div style={{ background: '#1e293b', padding: '10px', borderRadius: '8px' }}>
              <div style={{ color: '#94a3b8' }}>H₂S Concentration</div>
              <div style={{ fontSize: '1.1rem', fontWeight: '700' }}>{lastResult?.h2s_ppm || 0} ppm</div>
            </div>
            <div style={{ background: '#1e293b', padding: '10px', borderRadius: '8px' }}>
              <div style={{ color: '#94a3b8' }}>Shift Dose</div>
              <div style={{ fontSize: '1.1rem', fontWeight: '700' }}>{lastResult?.shift_exposure_ppm_hr || 0} ppm·hr</div>
            </div>
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '0.9rem', color: '#34d399', marginBottom: '8px' }}>Long-Term Dosimetry Summary</h3>
          <ul style={{ fontSize: '0.8rem', color: '#cbd5e1', paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <li>Weekly Total Exposure (7 days): <strong>{historyAnalytics?.weekly_dose || 0} ppm·hr</strong></li>
            <li>Monthly Weighted TWA (30 days): <strong>{historyAnalytics?.monthly_twa || 0} ppm</strong></li>
            <li>Rotational Dose (84 hours): <strong>{historyAnalytics?.rotation_dose || 0} ppm·hr</strong></li>
          </ul>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <button className="btn-secondary" onClick={() => window.print()}>
            <Printer size={16} /> Print Document
          </button>
          <button className="btn-primary" onClick={downloadPdfReport}>
            <Download size={16} /> Export PDF Report
          </button>
        </div>
      </div>
    </div>
  );
}
