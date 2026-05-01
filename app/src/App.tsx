import { Suspense, lazy, useEffect, useState } from 'react';
import { ConfigProvider } from './contexts/ConfigContext';
import { PlaybackProvider } from './contexts/PlaybackContext';
import { useTheme } from './hooks/useTheme';
import { useConfig } from './hooks/useConfig';
import { usePlaybackActions } from './hooks/usePlayback';
import { TitleBar } from './components/TitleBar';
import { Header } from './components/Header';
import { FolderPane } from './components/FolderPane';
import { MusicPane } from './components/MusicPane';
import { BottomBar } from './components/BottomBar';
import { Splash } from './components/Splash';
import { UnsupportedBanner } from './components/UnsupportedBanner';
import { api } from './lib/tauri';
import type { MidiFile } from './types';

// PlayerSheet pulls in lucide icons + tick-event subscription logic that's
// only needed once the user actually starts a song. Lazy-loading keeps the
// initial bundle (and thus splash → first-paint) lean.
const PlayerSheet = lazy(() =>
  import('./components/PlayerSheet').then((m) => ({ default: m.PlayerSheet }))
);

function Shell() {
  useTheme();
  const { config, ready } = useConfig();
  const { loadSong, pause } = usePlaybackActions();
  const [folder, setFolder] = useState<string | null>(null);
  const [file, setFile] = useState<MidiFile | null>(null);
  const [showPlayer, setShowPlayer] = useState(false);
  const [supported, setSupported] = useState(true);

  useEffect(() => {
    api.isPlaybackSupported().then(setSupported).catch(() => {});
  }, []);

  useEffect(() => {
    if (ready && !folder && config.folders[0]) setFolder(config.folders[0]);
  }, [ready, folder, config.folders]);

  async function onPlay(target?: MidiFile) {
    const f = target ?? file;
    if (!f) return;
    if (target && target.path !== file?.path) setFile(target);
    await loadSong(f.path); // arms engine in paused state at index 0
    setShowPlayer(true); // user presses Play in popup or DELETE hotkey to start
  }

  // X button / Esc → pause and close popup (returns user to song browser).
  // App-level exit is handled exclusively by the TitleBar close button.
  async function onClosePlayer() {
    await pause();
    setShowPlayer(false);
  }

  return (
    <div className="h-screen flex flex-col bg-[var(--bg)] text-[var(--text)] overflow-hidden overscroll-none">
      <TitleBar />
      {!supported && <UnsupportedBanner />}
      <Header />
      <div className="flex-1 flex overflow-hidden min-h-0">
        <FolderPane
          selectedFolder={folder}
          onSelectFolder={(p) => {
            setFolder(p || null);
            setFile(null);
          }}
        />
        <MusicPane
          folder={folder}
          selectedFile={file}
          onSelectFile={setFile}
          onPlayFile={(f) => onPlay(f)}
          disableNav={showPlayer}
        />
      </div>
      <BottomBar selectedFile={file} onPlay={() => onPlay()} />
      {/* PlayerSheet is lazy: render only when armed so the chunk isn't
          fetched until the user actually launches a song. Suspense fallback
          is null because the dialog itself is the visible UI. */}
      {showPlayer && (
        <Suspense fallback={null}>
          <PlayerSheet
            open={showPlayer}
            onClose={onClosePlayer}
            songName={file?.name ?? ''}
          />
        </Suspense>
      )}
    </div>
  );
}

export default function App() {
  return (
    <ConfigProvider>
      <PlaybackProvider>
        <Shell />
        <Splash />
      </PlaybackProvider>
    </ConfigProvider>
  );
}
