import { useContext } from 'react';
import {
  PlaybackActionsContext,
  PlaybackStateContext,
} from '../contexts/PlaybackContext';

/** Subscribes to live playback state (is_playing / index / total / speed).
 *  Re-renders at most once per animation frame because the underlying
 *  tick stream is rAF-throttled in PlaybackProvider. */
export function usePlaybackState() {
  return useContext(PlaybackStateContext);
}

/** Subscribes to playback actions (loadSong / play / pause / etc). The
 *  actions object has stable identity for the lifetime of the provider,
 *  so consumers reading *only* actions never re-render from playback
 *  state changes. */
export function usePlaybackActions() {
  return useContext(PlaybackActionsContext);
}
