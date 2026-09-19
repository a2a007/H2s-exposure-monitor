import React from 'react';
import { LayoutDashboard, Camera, Cpu, TrendingUp, History } from 'lucide-react';

export default function BottomNav({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'dashboard', label: 'Monitor', icon: LayoutDashboard },
    { id: 'scanner', label: 'Scanner', icon: Camera },
    { id: 'features', label: 'ROIs & ML', icon: Cpu },
    { id: 'analytics', label: 'Long-Term', icon: TrendingUp },
    { id: 'history', label: 'History', icon: History }
  ];

  return (
    <div className="bottom-nav-bar">
      {tabs.map((t) => {
        const Icon = t.icon;
        const isActive = activeTab === t.id;
        return (
          <button
            key={t.id}
            className={`nav-item ${isActive ? 'active' : ''}`}
            onClick={() => onTabChange(t.id)}
          >
            <Icon />
            <span>{t.label}</span>
          </button>
        );
      })}
    </div>
  );
}
