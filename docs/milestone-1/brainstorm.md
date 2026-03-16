# Project Brainstorming

## Purpose

Our project is a smart cat adoption monitoring system that tracks cat wellbeing before adoption. The system collects environmental and behavior data (temperature, humidity, light, movement, and location) and uses simple actuators to improve comfort and safety in real time. This helps staff make informed care decisions and gives adopters more confidence by showing that each cat has been monitored in a healthy, responsive environment.

## Subsystems

### Subsystem 1

This subsystem focuses on observation and interaction tracking in the adoption area. The camera captures live or periodic footage of each cat, while motion sensing detects activity around the enclosure and visitor engagement. It supports the project by helping staff monitor behavior and identify stress or unusual movement patterns.

#### Devices

| Component Name                                   | Interface Type | Documentation Link                                                      |
| ------------------------------------------------ | -------------- | ----------------------------------------------------------------------- |
| Camera Module (Raspberry Pi Camera / USB Camera) | CSI or USB     | https://www.raspberrypi.com/documentation/accessories/camera.html       |
| Motion Sensor (PIR)                              | GPIO           | https://learn.adafruit.com/pir-passive-infrared-proximity-motion-sensor |

### Subsystem 2

This subsystem manages mobility and comfort support for cats during monitoring. GPS provides location awareness for transport scenarios or supervised movement, and the fan provides active cooling when needed. It contributes to the project by improving safety tracking and keeping cats in a comfortable environment.

#### Devices

| Component Name      | Interface Type                      | Documentation Link                                             |
| ------------------- | ----------------------------------- | -------------------------------------------------------------- |
| GPS Module (NEO-6M) | UART (serial)                       | https://learn.adafruit.com/adafruit-ultimate-gps               |
| Cooling Fan (5V DC) | GPIO (via transistor/relay control) | https://projects.raspberrypi.org/en/projects/temperature-log/5 |

### Subsystem 3

This subsystem is responsible for enclosure environment sensing and access control. It tracks temperature/humidity and luminosity to understand living conditions, and uses a motorized lock mechanism to control enclosure access when needed. It supports the project by combining wellbeing metrics with controlled physical safety.

#### Devices

| Component Name                        | Interface Type             | Documentation Link                                                            |
| ------------------------------------- | -------------------------- | ----------------------------------------------------------------------------- |
| Temperature + Humidity Sensor (DHT22) | GPIO (digital single-wire) | https://learn.adafruit.com/dht                                                |
| Luminosity Sensor (BH1750)            | I2C                        | https://learn.adafruit.com/adafruit-bh1750-ambient-light-sensor               |
| Motor for Lock (Servo/Actuator)       | PWM / GPIO                 | https://learn.adafruit.com/adafruit-16-channel-servo-driver-with-raspberry-pi |
