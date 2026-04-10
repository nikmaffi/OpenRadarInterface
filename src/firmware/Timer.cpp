#include "Timer.h"

// Initialize with interval, timer starts at 0
Timer::Timer(unsigned wait): t_start(0), wait(wait) {
}

// Check if interval has elapsed since last reset
bool Timer::check(void) {
    return (millis() - t_start >= wait);
}

// Restart timer from now
void Timer::reset(void) {
    t_start = millis();
}

// Change interval duration
void Timer::setWait(unsigned wait) {
    this->wait = wait;
}
