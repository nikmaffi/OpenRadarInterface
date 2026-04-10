#include "Switch.h"

// Initialize pin mode and debounce timer
Switch::Switch(int attach, int flags):
attach(attach),
flags(flags),
st0(LOW),
st(LOW),
t(__SW_DEF_MS_DELAY) {
    bool is_pullup = (flags & __SW_PULLUP);

    pinMode(attach, is_pullup ? INPUT_PULLUP : INPUT);
}

// Default: pullup with rising edge
Switch::Switch(int attach): Switch(attach, __SW_PULLUP | __SW_RISING) {
}

// Check for debounced edge transition
bool Switch::isPressed(void) {
    st = digitalRead(attach);

    // No change, reset debounce
    if(st == st0) {
        t.reset();
        return false;
    }

    // Debounce elapsed, check edge type
    if(t.check()) {
        bool is_pullup = (flags & __SW_PULLUP);
        bool edge_trigger;

        bool pet = (st == HIGH && st0 == LOW);  // Positive edge
        bool net = (st == LOW && st0 == HIGH);   // Negative edge

        if((flags & __SW_RISING) && (flags & __SW_FALLING)) {
            edge_trigger = (st != st0);
        } else if(flags & __SW_RISING) {
            edge_trigger = is_pullup ? net : pet;
        } else if(flags & __SW_FALLING) {
            edge_trigger = is_pullup ? pet : net;
        } else {
            edge_trigger = is_pullup ? net : pet;
        }

        st0 = st;

        return edge_trigger;
    }

    return false;
}
