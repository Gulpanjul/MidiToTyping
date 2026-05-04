//! MIDI pitch -> typing-key mapping. Verbatim port of legacy/src/midi_parser.py:7
//! and the wrap rule on lines 33-34.

pub const SCALE: &str = "1!2@34$5%6^78*9(0qQwWeErtTyYuiIoOpPasSdDfgGhHjJklLzZxcCvVbBnm";

pub fn midi_pitch_to_key(pitch: u8) -> char {
    let scale: Vec<char> = SCALE.chars().collect();
    let len = scale.len() as i32;
    let mut idx = pitch as i32 - 36;
    while idx >= len {
        idx -= 12;
    }
    while idx < 0 {
        idx += 12;
    }
    scale[idx as usize]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pitch_36_is_first_scale_char() {
        // C2 (MIDI 36) -> idx 0 -> '1'
        assert_eq!(midi_pitch_to_key(36), '1');
    }

    #[test]
    fn pitch_above_range_wraps_down() {
        // SCALE has 61 chars; idx 60 is in range. MIDI 96 -> idx 60.
        let scale: Vec<char> = SCALE.chars().collect();
        assert_eq!(scale.len(), 61);
        assert_eq!(midi_pitch_to_key(96), scale[60]);
    }

    #[test]
    fn pitch_below_range_wraps_up() {
        // MIDI 24 -> idx -12 -> +12 -> 0 -> '1'
        assert_eq!(midi_pitch_to_key(24), '1');
    }

    #[test]
    fn pitch_far_above_wraps_repeatedly() {
        // MIDI 120 -> idx 84 -> -12 -> 72 -> -12 -> 60 -> in range
        let scale: Vec<char> = SCALE.chars().collect();
        assert_eq!(midi_pitch_to_key(120), scale[60]);
    }
}
