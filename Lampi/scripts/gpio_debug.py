import pigpio
import time

# Create a connection to the pigpio daemon
pi = pigpio.pi()

# Set up GPIO pins as inputs with pull-up resistors
pi.set_mode(27, pigpio.INPUT)
pi.set_pull_up_down(27, pigpio.PUD_UP)

pi.set_mode(23, pigpio.INPUT)
pi.set_pull_up_down(23, pigpio.PUD_UP)

pi.set_mode(22, pigpio.INPUT)
pi.set_pull_up_down(22, pigpio.PUD_UP)

pi.set_mode(17, pigpio.INPUT)
pi.set_pull_up_down(17, pigpio.PUD_UP)

try:
    while True:
        for pin in [27, 23, 22, 17]:
            if not pi.read(pin):
                print(pin)

        # Delay to avoid excessive CPU usage
        time.sleep(0.1)

except KeyboardInterrupt:
    # Clean up GPIO when script is interrupted
    pi.stop()
