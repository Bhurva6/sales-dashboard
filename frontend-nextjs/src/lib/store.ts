import { create } from 'zustand';

export interface AuthState {
  username: string;
  password: string;
  isAuthenticated: boolean;
  setCredentials: (username: string, password: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  username: '',
  password: '',
  isAuthenticated: false,
  setCredentials: (username: string, password: string) =>
    set({ username, password, isAuthenticated: true }),
  logout: () => set({ username: '', password: '', isAuthenticated: false }),
}));

export interface DashboardState {
  dashboardMode: 'avante' | 'iospl';
  hideInnovative: boolean;
  hideAvante: boolean;
  startDate: string;
  endDate: string;
  setSidebarOpen: (open: boolean) => void;
  setDashboardMode: (mode: 'avante' | 'iospl') => void;
  setHideInnovative: (hide: boolean) => void;
  setHideAvante: (hide: boolean) => void;
  setDateRange: (start: string, end: string) => void;
  sidebarOpen: boolean;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  dashboardMode: 'avante',
  hideInnovative: false,
  hideAvante: false,
  startDate: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0],
  endDate: new Date().toISOString().split('T')[0],
  sidebarOpen: true,
  setSidebarOpen: (open: boolean) => set({ sidebarOpen: open }),
  setDashboardMode: (mode: 'avante' | 'iospl') => set({ dashboardMode: mode }),
  setHideInnovative: (hide: boolean) => set({ hideInnovative: hide }),
  setHideAvante: (hide: boolean) => set({ hideAvante: hide }),
  setDateRange: (start: string, end: string) => set({ startDate: start, endDate: end }),
}));
