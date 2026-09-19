import React from 'react';
import { X, UserCheck, Plus } from 'lucide-react';
import { DEFAULT_EMPLOYEES } from '../utils/storage';

export default function EmployeeModal({ isOpen, onClose, activeEmp, onSelectEmp }) {
  if (!isOpen) return null;

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
        maxWidth: '440px',
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

        <h3 style={{ fontSize: '1.1rem', fontWeight: '800', marginBottom: '16px' }}>Select Active Employee</h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' }}>
          {DEFAULT_EMPLOYEES.map(emp => {
            const isSelected = emp.id === activeEmp.id;
            return (
              <div 
                key={emp.id}
                onClick={() => { onSelectEmp(emp); onClose(); }}
                style={{
                  background: isSelected ? 'rgba(56, 189, 248, 0.15)' : 'rgba(30, 41, 59, 0.5)',
                  border: isSelected ? '1px solid #38bdf8' : '1px solid rgba(255, 255, 255, 0.05)',
                  borderRadius: '12px',
                  padding: '12px',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div>
                  <div style={{ fontSize: '0.85rem', fontWeight: '700', color: '#f8fafc' }}>{emp.name} ({emp.id})</div>
                  <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>Band: {emp.bandId} | Shift: {emp.shift}</div>
                </div>
                {isSelected && <UserCheck size={18} color="#38bdf8" />}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
