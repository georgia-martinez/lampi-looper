# Assignment 9

## Martinez and Schlueter

## Peter Schlueter

Within this assignment, I learned how to create a bluetooth low energy (BLE) service which allows a central (in this case, the LAMPI application on an iPhone) to connect to a peripheral (in this case, the LAMPI device). I learned how to create this service through the `pybleno` library, and how BLE characteristics are used to describe bluetooth services and allow values to be read from and written to a peripheral's BLE characteristics. Additionally, I learned how to integrate MQTT into a BLE service, allowing messages published through the BLE service to be sent to other services subscribing to the topic the BLE service publishes MQTT messages to. Finally, I learned how to integrate a BLE service into an iOS application, sending values written to BLE characteristics to the application to update the application dynamically.

Additionally, I was surprised by the complexity of bluetooth services as a whole. The amount of documentation on bluetooth and the sheer amount of UUID descriptors for BLE services and characteristics is incredibly high, and I imagine that if not for the tutorials provided in the assignment the BLE service would have been much more difficult to implement. Moreover, I was surprised by the amount of code required to actually create the bluetooth service (`ble_peripheral.py`). I imagined that I would have to write a lot more than what we actually ended up writing to get everything working, and it was nice to see that something I initially thought would be incredibly complicated (i.e., creating a BLE service) was not as complex as I thought it would be if broken into smaller components.

## Georgia Martinez

something I learned ...
