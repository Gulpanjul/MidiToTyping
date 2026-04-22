"""
test_playSong.py
Tes logika inti playSong_clean.py tanpa GUI/keyboard.
Jalankan: python test_playSong.py
"""

import sys, os, time, threading, importlib, types

# ──────────────────────────────────────────────────────────
# Stub modul 'keyboard' agar tidak perlu install / admin
# ──────────────────────────────────────────────────────────
pressed  = []
released = []

keyboard_stub = types.ModuleType('keyboard')
keyboard_stub.press   = lambda k: pressed.append(k)
keyboard_stub.release = lambda k: released.append(k)
keyboard_stub.on_press_key = lambda *a, **kw: None
sys.modules['keyboard'] = keyboard_stub

# Import modul setelah stub dipasang
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location(
    "playSong_clean",
    pathlib.Path(__file__).parent.parent / "playSong_clean.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

PASS = "\033[92m✔\033[0m"
FAIL = "\033[91m✘\033[0m"
results = []

def check(name, ok):
    results.append((name, ok))
    print(f"  {PASS if ok else FAIL}  {name}")

print("\n═══════════════════════════════════════════════")
print("   playSong_clean.py — Test Suite")
print("═══════════════════════════════════════════════\n")

# ─── Test 1: CONVERSION_CASES punya '#' ─────────────────
print("■ [BUG #7] CONVERSION_CASES '#' → '3'")
check("'#' ada di CONVERSION_CASES", '#' in m.CONVERSION_CASES)
check("'#' → '3'", m.CONVERSION_CASES.get('#') == '3')

# ─── Test 2: parse_info – tempo= di akhir di-pop ────────
print("\n■ [BUG #5] parse_info — tempo= di baris terakhir")

m.info_tuple = (1.0, None, [
    [0.0, 'header'],
    [0.0, 'q'],
    [0.5, 'w'],
    [1.0, 'tempo=120'],  # baris terakhir = tempo marker
])
notes = m.parse_info()
check("tempo= terakhir di-pop dari notes", all('tempo' not in n[1] for n in notes))
check("jumlah notes benar (2)", len(notes) == 2)

# ─── Test 3: parse_info – delay relatif dihitung benar ──
print("\n■ parse_info — delay relatif")

m.info_tuple = (1.0, None, [
    [0.0, 'header'],
    [0.0, 'q'],
    [0.5, 'w'],
    [1.5, 'e'],
])
notes = m.parse_info()
check("nada[0] delay = 0.5 * 1.0 = 0.5", abs(notes[0][0] - 0.5) < 1e-9)
check("nada[1] delay = 1.0 * 1.0 = 1.0", abs(notes[1][0] - 1.0) < 1e-9)
check("nada terakhir delay = 1.0 (hardcoded)", abs(notes[-1][0] - 1.0) < 1e-9)

# ─── Test 4: _play_gen mencegah double-play ──────────────
print("\n■ [BUG #2] Generation counter — timer basi diabaikan")

m.info_tuple = (1.0, None, [
    [0.5, 'q'],
    [0.5, 'w'],
])
m.stored_index = 0
m.is_playing   = True
m._play_gen    = 1
pressed.clear()

# Panggil dengan gen lama (0) → harus diabaikan
m.play_next_note(gen=0)
time.sleep(0.1)
check("gen=0 saat _play_gen=1 → tidak mainkan nada", len(pressed) == 0)

# Panggil dengan gen benar (1) → harus mainkan
m.stored_index = 0
m.play_next_note(gen=1)
time.sleep(0.1)
check("gen=1 saat _play_gen=1 → mainkan nada 'q'", 'q' in pressed)

# ─── Test 5: on_delete_press toggle + increment gen ─────
print("\n■ [BUG #2] on_delete_press — gen naik saat pause & play")

m.is_playing = False
m._play_gen  = 5
m.stored_index = 0
m.info_tuple   = (1.0, None, [[0.5, 'q'], [1.0, 'w']])

class FakeEvent: pass

m.on_delete_press(FakeEvent())           # → PLAY, gen=6
check("Play: is_playing=True", m.is_playing == True)
gen_after_play = m._play_gen
check("Play: _play_gen naik (6)", gen_after_play == 6)

time.sleep(0.05)
m.on_delete_press(FakeEvent())           # → PAUSE, gen=7
check("Pause: is_playing=False", m.is_playing == False)
check("Pause: _play_gen naik (7)", m._play_gen == 7)

# ─── Test 6: on_end_press reset + increment gen ──────────
print("\n■ [BUG #6] on_end_press — gen naik saat skip ke akhir")

m.info_tuple   = (1.0, None, [[0.5, 'q']] * 5)
m.stored_index = 3
m.is_playing   = True
m._play_gen    = 10

m.on_end_press(FakeEvent())   # 3+10=13 >= 5 → reset
check("Skip → reset: is_playing=False", m.is_playing == False)
check("Skip → reset: stored_index=0",  m.stored_index == 0)
check("Skip → reset: _play_gen naik",  m._play_gen == 11)

# ─── Test 7: is_shifted mengenali '#' ───────────────────
print("\n■ [BUG #7] is_shifted('#')")
check("is_shifted('#') = True", m.is_shifted('#') == True)

# ─── Ringkasan ───────────────────────────────────────────
print("\n═══════════════════════════════════════════════")
passed = sum(1 for _, ok in results if ok)
total  = len(results)
print(f"  Hasil: {passed}/{total} test passed\n")
if passed == total:
    print("  \033[92m✔ Semua test LULUS!\033[0m")
else:
    failed = [n for n, ok in results if not ok]
    print("  \033[91m✘ GAGAL:\033[0m", ", ".join(failed))
print("═══════════════════════════════════════════════\n")
sys.exit(0 if passed == total else 1)
