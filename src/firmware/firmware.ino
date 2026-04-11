/**
 * NAME:            Radar Firmware Module (firmware.ino)
 * AUTHOR:          Nicolo' Maffi
 * WRITTEN:          5 apr 2026
 * COMPILED:        11 apr 2026
 * INSTALLATION:    ATmega328P
 */

// Headers
#include <Servo.h>

#include "Switch.h"
#include "Timer.h"

// Port mapping
#define __PORT_STR_STP 0x0A
#define __PORT_MODE    0x0B
#define __PORT_TRIGGER 0x05
#define __PORT_ECHO    0x06
#define __PORT_SERVO   0x03 // PWM output
#define __PORT_JOY       A0 // Analog input

// Servo config
#define __SERVO_UNIT_STEP 0.01f // Radians
#define __SERVO_MAX_RAD   3.00f // Radians
#define __SERVO_MIN_RAD   0.35f // Radians

// Serial config
#define __SERIAL_DELAY_MS      20 // Standard 50 Hz refresh rate
#define __SERIAL_BAUD_RATE 115200
#define __SERIAL_STR_DEL   "@"
#define __SERIAL_STOP_SIG  "STOP"

// Radar modes
#define __MODE_MANUAL 0x00
#define __MODE_AUTO   0x01

#define MODE_TOGGLE(MODE) ((MODE) == __MODE_MANUAL ? __MODE_AUTO : __MODE_MANUAL)

// Unit conversion
#define RAD_TO_DEG(RAD) ((RAD) * 180.f / PI)
#define DEG_TO_RAD(DEG) ((DEG) * PI / 180.f)

// Radar active state
static volatile bool __is_active;
// Radar operation mode
static volatile int __radar_mode;

// Radar hardware state
struct {
    bool forward; // Sweep direction: CW (true), CCW (false)
    float rad;    // Current angle (radians)
    Servo servo;  // Servo controller
} radar;

Timer serial_timer(__SERIAL_DELAY_MS);

Switch str_stp_switch(__PORT_STR_STP, __SW_PULLUP | __SW_RISING);
Switch mode_switch(__PORT_MODE, __SW_PULLUP | __SW_RISING);

// Initialize radar hardware
void init_radar(void) {
    radar.forward = true;
    radar.rad = __SERVO_MAX_RAD / 2;
    radar.servo.attach(__PORT_SERVO);

    radar.servo.write(RAD_TO_DEG(radar.rad));
}

// Update servo position
void step_radar(void) {
    if(__radar_mode == __MODE_MANUAL) {
        static float filtered = 512.0f;
        float alpha = 0.1f;

        filtered += alpha * (analogRead(__PORT_JOY) - filtered);

        int map_val = map((int)filtered, 0, 1023, RAD_TO_DEG(__SERVO_MIN_RAD), RAD_TO_DEG(__SERVO_MAX_RAD));

        radar.rad = DEG_TO_RAD(map_val);
    } else {
        // Clamp and reverse at limits
        if(radar.rad < __SERVO_MIN_RAD || radar.rad > __SERVO_MAX_RAD) {
            // Reverse sweep direction
            radar.forward = !radar.forward;

            if(radar.rad < __SERVO_MIN_RAD) {
                radar.rad = __SERVO_MIN_RAD;
            } else {
                radar.rad = __SERVO_MAX_RAD;
            }
        }

        radar.rad += (__SERVO_UNIT_STEP * (radar.forward ? 1 : -1));
    }

    radar.servo.write(RAD_TO_DEG(radar.rad));
}

// Measure distance via ultrasonic pulse (cm)
// Returns -1 on timeout (no echo received)
float radar_scan(void) {
    // Ensure trigger is LOW before pulse
    digitalWrite(__PORT_TRIGGER, LOW);
    delayMicroseconds(2);

    // Trigger pulse
    digitalWrite(__PORT_TRIGGER, HIGH);
    delayMicroseconds(10);
    digitalWrite(__PORT_TRIGGER, LOW);

    // Timeout ~38ms (~650cm max round-trip)
    unsigned long duration = pulseIn(__PORT_ECHO, HIGH, 38000UL);

    if(duration == 0) {
        return -1;
    }

    // Convert to cm
    return 0.034f * duration / 2;
}

void setup(void) {
    __is_active = false;
    __radar_mode = __MODE_AUTO;

    pinMode(__PORT_TRIGGER, OUTPUT);
    pinMode(__PORT_ECHO,    INPUT );

    init_radar();

    Serial.begin(__SERIAL_BAUD_RATE);
}

void loop(void) {
    if(mode_switch.isPressed()) {
        __radar_mode = MODE_TOGGLE(__radar_mode);
    }

    if(str_stp_switch.isPressed()) {
        __is_active = !__is_active;
    }

    // Rate limiting
    if(!serial_timer.check()) {
        return;
    }

    serial_timer.reset();

    if(__is_active) {
        step_radar();

        // Read sensor data
        float distance = radar_scan();
        float radians = radar.rad;

        // Send data over serial
        Serial.print(distance);
        Serial.print(__SERIAL_STR_DEL);
        Serial.println(radians);
    } else {
        // Send stop signal
        Serial.println(__SERIAL_STOP_SIG);
    }
}
