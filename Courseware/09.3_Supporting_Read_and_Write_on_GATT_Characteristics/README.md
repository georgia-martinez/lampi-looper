# Supporting Read and Write on GATT Characteristics

So far, our GATT Service and Characteristics are pretty boring - read only values.  We will expand our BTLE capabilties with additional Characterstic properties, but first we will need to build a little bit of infrastructure.

## Generating UUIDs

For our proprietary Services and Characteristics, we need our own 128-bit UUIDs.  You can generate these in several ways, but one simple way is to use the [Online UUID Generator](https://www.uuidgenerator.net/) to generate a Version 4 UUID.

Here is our UUID for this section:

```
7a4bbfe6-999f-4717-b63a-066e06971f59
```

By convention, we can use our UUID as a "base", similar to how the Bluetooth SIG uses a Base UUID, and then derive other UUIDs from that UUID.  We will use the two bytes represented by the four X's (remember, a byte in hexadecimal is represented by two "nibbles" of 4-bits each, 0-F):

```
7a4bXXXX-999f-4717-b63a-066e06971f59
```

## Our State Object

Let's build a simple object to hold some device state information, with one accessor method.

Create a new file `number_state.py`

```python3
from collections import defaultdict
from typing import Callable, Optional


class NumberState():
    def __init__(self):
        self._number = 0

        self.callbacks: Dict[str, List[Callable]] = defaultdict(list)


    # event handler registration
    def on(self, event: str, func: Optional[Callable] = None):
        def subscribe(func: Callable):
            if not callable(func):
                raise ValueError("Argument func must be callable.")
            self.callbacks[event].append(func)
            return func
        if func is None:
            return subscribe
        subscribe(func)

    # generate (emit) events
    def emit(self, event, message):
        for callback in self.callbacks[event]:
            callback(message)

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, new_value):
        if new_value != self._number:
            if new_value >= 0xff:
                new_value = 0
            self._number = new_value
```

This is a simple class `NumberState` to hold a single property `number` - note: we're using the Python [@property decorator](https://docs.python.org/3.7/library/functions.html?highlight=property#property).

The `NumberState` class also supports the registration of event handlers and event geeration:

* `on(self, event: str, func: Optional[Callable] = None)` - allows you to register an event hanlder for a particular event string
* `emit(self, event, message)` - allows you to generate the event and invoke all registered event handlers for that event

We will cover these more shortly.

## Our Number Service

Create a new file to hold our new Service `number_service.py`:

```python3
from pybleno import BlenoPrimaryService, Characteristic, Descriptor
from number_state import NumberState
import struct


class NumberCharacteristic(Characteristic):
    def __init__(self, number_state):
        Characteristic.__init__(self, {
            'uuid': '7a4b0001-999f-4717-b63a-066e06971f59',
            'properties': ['read', 'write', 'notify'],
            'value': None,
            'descriptors': [
                Descriptor({
                    'uuid': '2901',
                    'value': bytes("Some Number", 'utf-8')
                }),
                Descriptor({
                    'uuid': '2904',
                    # Presentation Format fields are:
                    # Format      1 octet :  0x04 - unsigned 8-bit integer
                    # Exponent    1 octet :  0x00
                    # Unit        2 octets:  0x2700 - unitless
                    # Name Space  1 octet :  0x01 - Bluetooth SIG
                    # Description 2 octets:  0x0000 - blank
                    'value': struct.pack("<BBHBH", 0x01, 0x00,
                                         0x2700, 0x01, 0x0000)
                })

            ]
        })
        self.number_state = number_state
        self.updateValueCallback = None

    def _encode_some_number(self):
        return struct.pack("<B", self.number_state.number)

    def onReadRequest(self, offset, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG, None)
        else:
            data = self._encode_some_number()
            callback(Characteristic.RESULT_SUCCESS, data)


class SomeNumberService(BlenoPrimaryService):
    uuid = '7a4bbfe6-999f-4717-b63a-066e06971f59'

    def __init__(self):
        self.number_state = NumberState()

        BlenoPrimaryService.__init__(self, {
            'uuid': self.uuid,
            'characteristics': [
                NumberCharacteristic(self.number_state)
            ]
        })
```

Here we have created a new Service `SomeNumberService` with our newly generated UUID, with one Characteristic `NumberCharacteristic` with a derived UUID, and the same Descriptors as we used for the Device Information Service (but with different values - a different name 'Some Number' and a different Presentation).  Again, see the Python [struct.pack](https://docs.python.org/3.7/library/struct.html?highlight=struct%20unpack#struct.pack) for more information, including the **Format Strings**.  The `SomeNumberService` creates a `NumberState` and passes that object to the `NumberCharacteristic` when it is constructed.

We will discuss `self.updateValueCallback = None` in a later section.

The `NumberCharacteristic` has two methods

* `_encode_some_number(self)` - this is a utility function that contains the code to encode the characteristic value to a `bytes` type using the `NumberState` `number` property.  It uses the `stuct.pack()` function, albeit in a trivial way since we are only encoding a single byte.  
* `onReadRequest(self, offset, callback)` overrides the parent class method to define how our characteristic should respond to requests to read the characteristic value (it uses the `_encode_some_number()` method).  The `callback(Characteristic.RESULT_SUCCESS, data)` invokes the `callback` callable that was provided in the invocation of `onReadRequest` passing in the `bytes` encoded characteristic value.

## Modify our Application

Now modify `ble_demo.py` like so to use our new service

```python3
#! /usr/bin/env python3
from pybleno import Bleno
from device_info_service import DeviceInfoService
from number_service import SomeNumberService
import time


class DemoBLEPeripheral():
    def __init__(self):
        self.bleno = Bleno()
        self.info_service = DeviceInfoService('CWRU', 'LAMPI', '123456')
        self.number_service = SomeNumberService()

        self.bleno.on('stateChange', self.onStateChange)
        self.bleno.on('advertisingStart', self.onAdvertisingStart)

    def start(self):
        self.bleno.start()

    def stop(self):
        self.bleno.stopAdvertising()
        self.bleno.disconnect()

    def onStateChange(self, state):
        print('on -> stateChange: ' + state)

        if (state == 'poweredOn'):
            self.bleno.startAdvertising('Lampi-Test',
                                        [
                                            self.info_service.uuid,
                                            self.number_service.uuid]
                                        )
        else:
            self.bleno.stopAdvertising()

    def onAdvertisingStart(self, error):
        print('on -> advertisingStart: '
              + ('error ' + error if error else 'success'))

        if not error:
            self.bleno.setServices([
                self.info_service,
                self.number_service,
            ])


def main():

    ble_peripheral = DemoBLEPeripheral()
    ble_peripheral.start()

    while True:
        time.sleep(1)

    print("\nStopping BLE peripheral\n")
    ble_peripheral.stop()


if __name__ == "__main__":
    main()
```

This will add our new `NumberSerice` to both the advertising broacast packets and to the services that are provided when Centrals connect.

Go ahead and run the updated application:

```bash
./ble_demo.py
```

You should see both of our Services in `LightBlue`, including our 'Some Number' Characteristic:

![](Images/lightblue_both_services.png)

If you drill into the 'Some Number' Characteristic and use the 'Read Again' mechanism a few times you should see multiple reads, all with the value of 0x00).

![](Images/lightblue_some_number_value.png)

## Writable Characteristics

Now, let's allow users (Bluetooth Centrals, really) to modify our 'Some Number' Characteristic.

Modify `number_service.py` and add `'write'` to the `properties` list after `'read'`.  

Then add the following method after the 'onReadRequest':

```python3
    def onWriteRequest(self, data, offset, withoutResponse, callback):
        if offset:
            callback(Characteristic.RESULT_ATTR_NOT_LONG)
        elif len(data) != 1:
            callback(Characteristic.RESULT_INVALID_ATTRIBUTE_LENGTH)
        else:
            print(f'Writing SomeNumber {data}')
            self.number_state.number = struct.unpack("<B", data)[0]
            callback(Characteristic.RESULT_SUCCESS)

```

Again, we do some basic error checking (note the incoming data length test), and then read the value out as a UInt8 with Python's [`struct.unpack()`](https://docs.python.org/3.7/library/struct.html?highlight=struct%20unpack#struct.unpack).


Run the application and connect with `LightBlue`:

You will notice that "Write new value" now appears:

![](Images/lightblue_write_available.png)

Try "Write new value" and enter a value in hex:

![](Images/lightblue_write_hex.png)

and observe the new value:

![](Images/lightblue_with_new_written_value.png)

Congratulations, you have add Read and Write support!

Next up: [09.4 Supporting Notify on GATT Characteristics](../09.4_Supporting_Notify_on_GATT_Characteristics/README.md)

&copy; 2015-2024 LeanDog, Inc. and Nick Barendt
