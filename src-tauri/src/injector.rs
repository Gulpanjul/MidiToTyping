//! Keyboard injection abstraction. Whitelist + shift map ported verbatim
//! from legacy/src/keyboard_sim.py and legacy/src/constants.py CONVERSION_CASES.

use enigo::{Direction, Enigo, Key, Keyboard, Settings};
use std::sync::Mutex;
use std::sync::Mutex as StdMutex;

/// Verbatim from legacy/src/keyboard_sim.py:3-8
pub const ALLOWED: &str = concat!(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "0123456789",
    "!@#$%^&*()_+{}|:\"<>?",
    "`~-=[]\\;',./ "
);

pub fn is_allowed(c: char) -> bool {
    ALLOWED.contains(c)
}

/// Verbatim from legacy/src/keyboard_sim.py:11-15
pub fn is_shifted(c: char) -> bool {
    let v = c as u32;
    if (65..=90).contains(&v) {
        return true;
    }
    "!@#$%^&*()_+{}|:\"<>?".contains(c)
}

/// Verbatim from legacy/src/constants.py:12-15. Maps shifted-symbol -> base key.
pub fn shifted_to_base(c: char) -> Option<char> {
    Some(match c {
        '!' => '1',
        '@' => '2',
        '#' => '3',
        '£' => '3',
        '$' => '4',
        '%' => '5',
        '^' => '6',
        '&' => '7',
        '*' => '8',
        '(' => '9',
        ')' => '0',
        _ => return None,
    })
}

pub trait Injector: Send + Sync {
    fn press(&self, key: char);
    fn release(&self, key: char);
}

/// Records every press/release call. Used in tests so we never actually
/// inject keys into the OS.
#[derive(Default)]
pub struct MockInjector {
    pub events: Mutex<Vec<String>>,
}

impl Injector for MockInjector {
    fn press(&self, key: char) {
        if !is_allowed(key) {
            return;
        }
        self.events.lock().unwrap().push(format!("press {}", key));
    }
    fn release(&self, key: char) {
        if !is_allowed(key) {
            return;
        }
        self.events.lock().unwrap().push(format!("release {}", key));
    }
}

pub struct EnigoInjector {
    inner: StdMutex<Enigo>,
}

impl EnigoInjector {
    pub fn new() -> Result<Self, String> {
        let enigo = Enigo::new(&Settings::default())
            .map_err(|e| format!("enigo init failed: {e}"))?;
        Ok(Self {
            inner: StdMutex::new(enigo),
        })
    }

    fn key_for(c: char) -> Key {
        Key::Unicode(c)
    }
}

impl Injector for EnigoInjector {
    fn press(&self, key: char) {
        if !is_allowed(key) {
            return;
        }
        let mut enigo = self.inner.lock().unwrap();
        if is_shifted(key) {
            let base = shifted_to_base(key).unwrap_or_else(|| key.to_ascii_lowercase());
            // Mirror Python: release base, hold shift, press base, release shift
            let _ = enigo.key(Self::key_for(base), Direction::Release);
            let _ = enigo.key(Key::LShift, Direction::Press);
            let _ = enigo.key(Self::key_for(base), Direction::Press);
            let _ = enigo.key(Key::LShift, Direction::Release);
        } else {
            let _ = enigo.key(Self::key_for(key), Direction::Release);
            let _ = enigo.key(Self::key_for(key), Direction::Press);
        }
    }

    fn release(&self, key: char) {
        if !is_allowed(key) {
            return;
        }
        let mut enigo = self.inner.lock().unwrap();
        if is_shifted(key) {
            let base = shifted_to_base(key).unwrap_or_else(|| key.to_ascii_lowercase());
            let _ = enigo.key(Self::key_for(base), Direction::Release);
        } else {
            let _ = enigo.key(Self::key_for(key), Direction::Release);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn allowed_includes_letters_and_punctuation() {
        assert!(is_allowed('a'));
        assert!(is_allowed('Z'));
        assert!(is_allowed('!'));
        assert!(is_allowed(' '));
        assert!(!is_allowed('é'));
        assert!(!is_allowed('\n'));
    }

    #[test]
    fn shift_predicate_matches_python() {
        assert!(is_shifted('A'));
        assert!(is_shifted('Z'));
        assert!(is_shifted('!'));
        assert!(is_shifted(')'));
        assert!(!is_shifted('a'));
        assert!(!is_shifted('1'));
        assert!(!is_shifted('-'));
    }

    #[test]
    fn shifted_to_base_covers_eleven_entries() {
        let pairs = [
            ('!', '1'),
            ('@', '2'),
            ('#', '3'),
            ('£', '3'),
            ('$', '4'),
            ('%', '5'),
            ('^', '6'),
            ('&', '7'),
            ('*', '8'),
            ('(', '9'),
            (')', '0'),
        ];
        for (sym, base) in pairs {
            assert_eq!(shifted_to_base(sym), Some(base));
        }
        assert_eq!(shifted_to_base('A'), None);
    }

    #[test]
    fn mock_injector_drops_disallowed_chars() {
        let m = MockInjector::default();
        m.press('a');
        m.press('é');
        m.release('a');
        let events = m.events.lock().unwrap();
        assert_eq!(*events, vec!["press a", "release a"]);
    }
}
