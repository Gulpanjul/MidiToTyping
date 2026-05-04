import { createContext, useEffect, useState, type ReactNode } from 'react';
import type { Config } from '../types';
import { api } from '../lib/tauri';

const DEFAULT: Config = { lang: 'id', theme: 'dark', palette: 'celestial', folders: [] };

interface Ctx {
  config: Config;
  setConfig: (c: Partial<Config>) => void;
  ready: boolean;
}

export const ConfigContext = createContext<Ctx>({
  config: DEFAULT,
  setConfig: () => {},
  ready: false,
});

export function ConfigProvider({ children }: { children: ReactNode }) {
  const [config, setLocal] = useState<Config>(DEFAULT);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    api
      .getConfig()
      .then((c) => {
        setLocal(c);
        setReady(true);
      })
      .catch(() => setReady(true));
  }, []);

  function setConfig(patch: Partial<Config>) {
    setLocal((prev) => {
      const next = { ...prev, ...patch };
      api.setConfig(next).catch(() => {});
      return next;
    });
  }

  return (
    <ConfigContext.Provider value={{ config, setConfig, ready }}>
      {children}
    </ConfigContext.Provider>
  );
}
