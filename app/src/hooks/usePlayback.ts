import { useContext } from 'react';
import { PlaybackContext } from '../contexts/PlaybackContext';

export function usePlayback() {
  return useContext(PlaybackContext);
}
