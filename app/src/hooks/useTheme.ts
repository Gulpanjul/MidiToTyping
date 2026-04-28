import { useEffect } from 'react';
import { applyTheme } from '../theme/themes';
import { useConfig } from './useConfig';

export function useTheme() {
  const { config } = useConfig();
  useEffect(() => {
    applyTheme(config.palette, config.theme);
  }, [config.palette, config.theme]);
}
