"""
simulasi_play.py
Skrip ini mensimulasikan playSong_clean.py di terminal tanpa membuka GUI
dan tanpa benar-benar menekan keyboard fisik (aman untuk dicoba).
"""

import sys
import time
import types
import threading

print("Menyiapkan simulasi...\n")

# 1. Mock modul 'keyboard' agar tidak memencet tombol sungguhan
keyboard_stub = types.ModuleType('keyboard')
keyboard_stub.press = lambda k: None  # Diam saja
keyboard_stub.release = lambda k: None # Diam saja
callbacks = {}
def mock_on_press(key, callback):
    callbacks[key] = callback
keyboard_stub.on_press_key = mock_on_press
sys.modules['keyboard'] = keyboard_stub

# 2. Import modul utama
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
import playSong_clean as app

# 3. Buat lagu bohongan (Twinkle Twinkle Little Star)
dummy_song = [
    [0.0, 'header'],
    [0.5, 'c'], [1.0, 'c'], [1.5, 'g'], [2.0, 'g'],
    [2.5, 'a'], [3.0, 'a'], [3.5, 'g'],
    [4.5, 'f'], [5.0, 'f'], [5.5, 'e'], [6.0, 'e'],
    [6.5, 'd'], [7.0, 'd'], [7.5, 'c']
]
parsed_song = (1.0, None, dummy_song)

# Bypass GUI di process_file
app.process_file = lambda: parsed_song

# 4. Fungsi simulasi penekanan tombol
def simulate_user_actions():
    time.sleep(1)
    
    print("\n[SIMULASI] User menekan tombol DELETE untuk PLAY...")
    callbacks['delete'](None)
    
    # Biarkan main beberapa nada
    time.sleep(4)
    
    print("\n[SIMULASI] User menekan tombol DELETE untuk PAUSE...")
    callbacks['delete'](None)
    
    time.sleep(2)
    
    print("\n[SIMULASI] User menekan tombol END untuk SKIP maju (+10)...")
    callbacks['end'](None)
    
    time.sleep(1)
    print("\n[SIMULASI] User menekan tombol DELETE untuk PLAY lagi dari titik baru...")
    callbacks['delete'](None)
    
    # Biarkan sampai lagu habis (karena sisa dikit)
    time.sleep(4)
    
    print("\n[SIMULASI] Lagu otomatis berhenti setelah selesai.")
    print("[SIMULASI] Keluar dalam 2 detik...")
    time.sleep(2)
    
    # Kirim sinyal keyboard interrupt ke main thread
    import _thread
    _thread.interrupt_main()

# Jalankan simulasi di background
threading.Thread(target=simulate_user_actions, daemon=True).start()

# Mulai aplikasi utama (tanpa GUI, tapi loop utama)
try:
    print("Menjalankan program utama (dengan GUI dan Keyboard di-mock)...")
    app.main()
except KeyboardInterrupt:
    print("\nProgram utama mendeteksi KeyboardInterrupt dan keluar dengan bersih.")
