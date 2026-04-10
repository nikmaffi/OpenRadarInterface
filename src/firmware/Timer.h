#ifndef __TIMER_H__
#define __TIMER_H__

#include <Arduino.h>

// Non-blocking millisecond timer
class Timer {
private:
    unsigned long t_start; // Timestamp of last reset
    unsigned wait;         // Interval duration (ms)
public:
    Timer(unsigned wait);

    Timer(Timer &&) = delete;
    Timer(const Timer &) = delete;

    // Returns true if interval has elapsed
    bool check(void);
    // Restart the timer
    void reset(void);
    // Update interval duration
    void setWait(unsigned wait);
};

#endif // __TIMER_H__
