import { useEffect, useState } from 'react';
import { getCurrentWindow } from '@tauri-apps/api/window';
import { ConfigProvider } from './contexts/ConfigContext';
import { PlaybackProvider } from './contexts/PlaybackContext';
import { useTheme } from './hooks/useTheme';
import { useConfig } from './hooks/useConfig';
import { usePlayback } from './hooks/usePlayback';
import { TitleBar } from './components/TitleBar';
import { Header } from './components/Header';
import { FolderPane } from './components/FolderPane';
import { MusicPane } from './components/MusicPane';
import { BottomBar } from './components/BottomBar';
import { PlayerSheet } from './components/PlayerSheet';
import { UnsupportedBanner } from './components/UnsupportedBanner';
import { api } from './lib/tauri';
import type { MidiFile } from './types';

function Shell() {
  useTheme();
  const { config, ready } = useConfig();
  const { loadSong, pause } = usePlayback();
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

  async function onPlay() {
    if (!file) return;
    await loadSong(file.path); // arms engine in paused state at index 0
    setShowPlayer(true); // user presses Play in popup or DELETE hotkey to start
  }

  // "Pilih Lagu Lain" → pause and close popup (returns user to song browser).
  async function onPickAnother() {
    await pause();
    setShowPlayer(false);
  }

  // "Keluar" → pause, close popup, then close the app window. Mirrors
  // the Python main loop where `action == 'exit'` breaks out of the
  // outer while-loop in playSong_clean.py:79-80.
  async function onExit() {
    await pause();
    setShowPlayer(false);
    try {
      await getCurrentWindow().close();
    } catch {
      // running in browser dev mode (no Tauri runtime) — ignore
    }
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
        <MusicPane folder={folder} selectedFile={file} onSelectFile={setFile} />
      </div>
      <BottomBar selectedFile={file} onPlay={onPlay} />
      <PlayerSheet
        open={showPlayer}
        onClose={onPickAnother}
        onPickAnother={onPickAnother}
        onExit={onExit}
        songName={file?.name ?? ''}
      />
    </div>
  );
}

export default function App() {
  return (
    <ConfigProvider>
      <PlaybackProvider>
        <Shell />
      </PlaybackProvider>
    </ConfigProvider>
  );
}
