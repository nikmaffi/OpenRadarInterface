#ifndef __SWITCH_H__
#define __SWITCH_H__

#include <Arduino.h>

#include "Timer.h"

// Debounce delay (ms)
#define __SW_DEF_MS_DELAY 100

// Edge detection flags
#define __SW_RISING    (1 << 0)
#define __SW_FALLING   (1 << 1)
#define __SW_PULLUP    (1 << 2)

// Debounced button with edge detection
class Switch {
private:
    int attach;  // Pin number
    int flags;   // Config flags (pullup, edge type)

    int st0, st; // Previous and current state
    Timer t;     // Debounce timer
public:
    Switch(int attach, int flags);
    Switch(int attach);

    Switch(Switch &&) = delete;
    Switch(const Switch &) = delete;

    // Returns true on configured edge after debounce
    bool isPressed(void);
};

#endif // __SWITCH_H__
