//! Platform-specific bits. Currently just Windows timer resolution.

#[cfg(windows)]
pub fn begin_high_resolution_timer() {
    use windows::Win32::Media::timeBeginPeriod;
    unsafe {
        let _ = timeBeginPeriod(1);
    }
}

#[cfg(windows)]
pub fn end_high_resolution_timer() {
    use windows::Win32::Media::timeEndPeriod;
    unsafe {
        let _ = timeEndPeriod(1);
    }
}

#[cfg(not(windows))]
pub fn begin_high_resolution_timer() {}

#[cfg(not(windows))]
pub fn end_high_resolution_timer() {}

pub fn is_playback_supported() -> bool {
    cfg!(windows)
}
