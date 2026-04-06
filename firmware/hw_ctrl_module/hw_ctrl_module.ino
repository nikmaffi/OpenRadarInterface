/**
 * NAME:            hw_ctrl_module (Hardware Control Module)
 * AUTHOR:          Nicolo' Maffi
 * WRITTEN:         5 apr 2026
 * COMPILED:        5 apr 2026
 * INSTALLATION:    ATmega328P
 */

// Headers
#include <Servo.h>

// Port mapping
#define __PORT_STR_STP 0x02
#define __PORT_TRIGGER 0x03
#define __PORT_ECHO    0x06
#define __PORT_SERVO   0x09 // PWM output

// Servo configurations
#define __SERVO_UNIT_STEP 0.02f // Radians
#define __SERVO_MAX_RAD   3.00f // Radians
#define __SERVO_MIN_RAD   0.35f // Radians

// Serial communication configs
#define __SERIAL_DELAY_MS      20 // Standard 50 Hz refresh rate
#define __SERIAL_DATA_SIZE      8 // Bytes
#define __SERIAL_BAUD_RATE 115200
#define __SERIAL_STOP_SIG    0xFF

// Conversion utility
#define RAD_TO_DEG(RAD) ((RAD) * 180.f / PI)

// Non-blocking timer utility
bool wait_for(unsigned long time) {
    static unsigned long t = time;
    static unsigned long start = millis();

    if(millis() - start >= t) {
        start = millis();
        return true;
    }

    return false;
}

// Radar hardware state
struct {
    bool forward; // Sweep direction: CW (true), CCW (false)
    float rad;    // Current angle value (radians)
    Servo servo;  // Servo controller object
} radar;

// Serial transmission buffer
union {
    struct {
        float distance; // Distance (cm)
        float radians;  // Angle (radians)
    };
    uint8_t bytes[__SERIAL_DATA_SIZE]; // Raw data
} radar_data;

// Volatile toggle for radar operation state
static volatile bool __is_active;

// ISR to switch radar activity
void start_stop_radar(void) {
    __is_active = !__is_active;
}

// Initialize hardware state
void init_radar(void) {
    radar.forward = true;
    radar.rad = __SERVO_MIN_RAD;
    radar.servo.attach(__PORT_SERVO);

    radar.servo.write(RAD_TO_DEG(radar.rad));
}

// Update servo position and sweep direction
void step_radar(void) {
    // Out of range checking
    if(radar.rad < __SERVO_MIN_RAD || radar.rad > __SERVO_MAX_RAD) {
        // Reversing direction
        radar.forward = !radar.forward;
    }

    radar.rad += (__SERVO_UNIT_STEP * (radar.forward ? 1 : -1));
    radar.servo.write(RAD_TO_DEG(radar.rad));
}

// Perform ultrasonic distance measurement
float radar_scan(void) {
    digitalWrite(__PORT_TRIGGER, LOW);

    // Trigger pulse
    digitalWrite(__PORT_TRIGGER, HIGH);
    delayMicroseconds(10);
    digitalWrite(__PORT_TRIGGER, LOW);

    // Calculate cm
    return 0.034f * pulseIn(__PORT_ECHO, HIGH) / 2;
}

void setup(void) {
    __is_active = true;

    pinMode(__PORT_TRIGGER, OUTPUT);
    pinMode(__PORT_ECHO,    INPUT );

    attachInterrupt(digitalPinToInterrupt(__PORT_STR_STP), start_stop_radar, CHANGE);

    init_radar();

    Serial.begin(__SERIAL_BAUD_RATE);
}

void loop(void) {
    // Frequency control
    if(!wait_for(__SERIAL_DELAY_MS)) {
        return;
    }

    if(__is_active) {
        step_radar();

        // Update data packet
        radar_data.distance = radar_scan();
        radar_data.radians = radar.rad;
    } else {
        // Sending RADAR STOPPED signal
        memset(radar_data.bytes, __SERIAL_STOP_SIG, __SERIAL_DATA_SIZE);
    }

    // Stream binary data
    Serial.write(radar_data.bytes, __SERIAL_DATA_SIZE);
}
