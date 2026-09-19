import React, { useState } from 'react';
import { History, Download, FileText, Search, Filter, HardDrive } from 'lucide-react';

export default function HistoryTab({ 
  historyAnalytics, 
  onOpenReport 
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const records = historyAnalytics?.records || [];

  const filteredRecords = records.filter(r => {
    const matchesSearch = (r.Employee_ID || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (r.Band_ID || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (r.Timestamp || '').includes(searchTerm);
    const matchesFilter = statusFilter === 'ALL' || r.Alert_Status === statusFilter;
    return matchesSearch && matchesFilter;
  });

  const exportCsv = () => {
    const listToExport = filteredRecords.length > 0 ? filteredRecords : records;
    if (listToExport.length === 0) {
      alert("No exposure records available to export.");
      return;
    }
    
    const headers = [
      "Timestamp", "Employee_ID", "Band_ID", "Shift_Info", 
      "H2S_Concentration_ppm", "Exposure_Duration_hr", 
      "Shift_Exposure_ppm_hr", "TWA_8hr_ppm", "Alert_Status"
    ];

    const rows = listToExport.map(r => 
      headers.map(h => `"${(r[h] ?? '').toString().replace(/"/g, '""')}"`).join(",")
    );

    const csvString = [headers.join(","), ...rows].join("\r\n");

    // Use Blob and URL.createObjectURL for 100% reliable browser download
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `H2S_Exposure_History_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const downloadDirectServerCsv = () => {
    window.open('http://localhost:5000/api/history/download', '_blank');
  };

  return (
    <>
      {/* Top Header Card */}
      <div className="card">
        <div className="card-title-row">
          <span className="card-title">
            <History size={18} color="#38bdf8" /> Historical Employee Exposure Logs
          </span>
          <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>{records.length} Total Records</span>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <button className="btn-secondary" onClick={exportCsv} title="Download CSV file directly">
            <Download size={16} /> Export CSV
          </button>
          <button className="btn-primary" onClick={onOpenReport} title="Generate printable PDF audit report">
            <FileText size={16} /> Audit Report PDF
          </button>
        </div>

        {/* Search & Filter Controls */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '8px', marginTop: '4px' }}>
          <div style={{ position: 'relative' }}>
            <Search size={14} style={{ position: 'absolute', top: '12px', left: '10px', color: '#64748b' }} />
            <input 
              type="text" 
              className="form-input" 
              placeholder="Search Emp ID / Band ID..." 
              value={searchTerm} 
              onChange={(e) => setSearchTerm(e.target.value)} 
              style={{ paddingLeft: '32px', fontSize: '0.8rem' }}
            />
          </div>

          <select 
            className="form-input" 
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ fontSize: '0.8rem' }}
          >
            <option value="ALL">All Status</option>
            <option value="NORMAL">NORMAL</option>
            <option value="WARNING">WARNING</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>
        </div>
      </div>

      {/* History Log Cards List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {filteredRecords.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', color: '#94a3b8', padding: '30px' }}>
            No exposure history records match your filter criteria.
          </div>
        ) : (
          filteredRecords.map((r, idx) => (
            <div key={idx} className="card" style={{ padding: '14px', gap: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <span style={{ fontSize: '0.85rem', fontWeight: '700', color: '#f8fafc' }}>{r.Employee_ID || 'EMP-104'}</span>
                  <span style={{ fontSize: '0.72rem', color: '#94a3b8', marginLeft: '8px' }}>Band: {r.Band_ID || 'BAND-884'}</span>
                </div>
                <span className={`status-badge ${r.Alert_Status?.toLowerCase() || 'normal'}`}>
                  {r.Alert_Status || 'NORMAL'}
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px', fontSize: '0.75rem', background: 'rgba(30,41,59,0.5)', padding: '8px', borderRadius: '8px' }}>
                <div>
                  <div style={{ color: '#64748b', fontSize: '0.68rem' }}>H₂S ppm</div>
                  <div style={{ fontWeight: '700', color: '#38bdf8' }}>{r.H2S_Concentration_ppm} ppm</div>
                </div>

                <div>
                  <div style={{ color: '#64748b', fontSize: '0.68rem' }}>Shift Dose</div>
                  <div style={{ fontWeight: '700', color: '#fbbf24' }}>{r.Shift_Exposure_ppm_hr} ppm·hr</div>
                </div>

                <div>
                  <div style={{ color: '#64748b', fontSize: '0.68rem' }}>8-hr TWA</div>
                  <div style={{ fontWeight: '700', color: '#34d399' }}>{r.TWA_8hr_ppm || (r.Shift_Exposure_ppm_hr / 8).toFixed(2)} ppm</div>
                </div>
              </div>

              <div style={{ fontSize: '0.68rem', color: '#64748b', textAlign: 'right' }}>
                {r.Timestamp}
              </div>
            </div>
          ))
        )}
      </div>
    </>
  );
}
