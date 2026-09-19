// Local Storage & Central API Sync Manager for H2S Android App

const STORAGE_KEYS = {
  EMPLOYEE: 'h2s_active_employee',
  HISTORY: 'h2s_exposure_history_local',
  SETTINGS: 'h2s_app_settings'
};

export const DEFAULT_EMPLOYEES = [
  { id: 'EMP-104', name: 'Alex Johnson', bandId: 'BAND-884', shift: 'Day Shift A', durationHours: 8.0, department: 'Hazmat Ops' },
  { id: 'EMP-208', name: 'Samantha Reed', bandId: 'BAND-312', shift: 'Night Shift B', durationHours: 10.0, department: 'Refinery 4' },
  { id: 'EMP-305', name: 'David Miller', bandId: 'BAND-509', shift: 'Rotation Shift C', durationHours: 12.0, department: 'Offshore Rig' }
];

export const getActiveEmployee = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEYS.EMPLOYEE);
    return saved ? JSON.parse(saved) : DEFAULT_EMPLOYEES[0];
  } catch (e) {
    return DEFAULT_EMPLOYEES[0];
  }
};

export const setActiveEmployee = (emp) => {
  try {
    localStorage.setItem(STORAGE_KEYS.EMPLOYEE, JSON.stringify(emp));
  } catch (e) {
    console.error('Failed saving employee:', e);
  }
};

export const getLocalHistory = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEYS.HISTORY);
    return saved ? JSON.parse(saved) : [];
  } catch (e) {
    return [];
  }
};

export const saveLocalHistoryRecord = (record) => {
  try {
    const history = getLocalHistory();
    const updated = [record, ...history];
    localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(updated.slice(0, 50)));
    return updated;
  } catch (e) {
    console.error('Failed saving local history:', e);
    return [];
  }
};
