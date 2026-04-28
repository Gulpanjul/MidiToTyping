import { useEffect, useState } from 'react';
import { ConfigProvider } from './contexts/ConfigContext';
import { PlaybackProvider } from './contexts/PlaybackContext';
import { useTheme } from './hooks/useTheme';
import { useConfig } from './hooks/useConfig';
import { usePlayback } from './hooks/usePlayback';
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
  const { loadSong, play } = usePlayback();
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
    await loadSong(file.path);
    await play();
    setShowPlayer(true);
  }

  return (
    <div className="h-screen flex flex-col bg-[var(--bg)] text-[var(--text)]">
      {!supported && <UnsupportedBanner />}
      <Header />
      <div className="flex-1 flex overflow-hidden">
        <FolderPane
          selectedFolder={folder}
          onSelectFolder={(p) => {
            setFolder(p || null);
            setFile(null);
          }}
        />
        <MusicPane folder={folder} selectedFile={file} onSelectFile={setFile} />
      </div>
      <BottomBar
        selectedFile={file}
        onPlay={onPlay}
        onCancel={() => {
          setFile(null);
          setShowPlayer(false);
        }}
      />
      <PlayerSheet
        open={showPlayer}
        onClose={() => setShowPlayer(false)}
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
