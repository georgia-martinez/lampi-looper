# Building a Simple BTLE Peripheral

During this Chapter we will be building a simple Bluetooth Low Energy (BTLE or BLE) peripheral and an iOS application to connect and use it.

BTLE has become very popular for connecting to "smart" devices. The combination of broad support in smartphones and tablets and low-cost BTLE chips has accelerated its adoption.  It is useful for a whole range of applications, particularly for devices that have limited UIs and/or are battery powered - the standard truly provides a low-energy communications mechanism.

The BTLE specification has two roles:  **Central** (typically a device like your smartphone) and **Peripheral** (a device like a fitness tracker).  Some devices can switch between roles as needed, while many devices, like a fitness tracker are only peripherals.  We will be adding BTLE Peripheral support to LAMPI so that a mobile app can control it.

The [Raspberry PI 3 B board has WiFI and BTLE built-in](https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus/).  Under Linux, Bluetooth is supported by the [BlueZ](http://www.bluez.org/about/) project.  We will be completely bypassing BlueZ and instead using a Python library [pybleno](https://github.com/Adam-Langley/pybleno) and communicates directly with the Bluetooth Host Controller Interface (HCI) designed specifically for building BTLE peripherals.  (FWIW:`pybleno` is a Python port of a now-unsupported NodeJS library, [bleno](https://github.com/noble/bleno).)


## Install `pybleno`:

We need to install some system dependencies needed for `pybleno`:


Install `pybleno` with 'pip':

```bash
sudo pip3 install pybleno
```

## Granting Permissions

We need to grant system permissions to `python3` so that it can acess "raw" devices (including the Bluetooth hardware):

```bash
sudo setcap cap_net_raw+eip $(eval readlink -f `which python3`)
```

## Blueooth Device Name

There are several ways to set the Bluetooth device name on a Raspberry Pi, but the simplest is to modify the `hostname`.

Change your LAMPI hostname by editing `/etc/hostname`:

```bash
sudo nano /etc/hostname
```
We will use a hostname for our devices of the form `LAMPI-<DeviceID>` where `<DeviceID>` is the same Device ID we have used to uniquely identify our LAMPI devices.  

If your LAMPI's DeviceID is `b827ebb9372e` then the hostname should be `LAMPI-b827ebb9372e`.

Save your changes.  Then reboot:

```bash
sudo reboot
```

**NOTE: you must reboot your LAMPI for this change to fully propagate.**


## Disable 'bluetooth' Daemon

We need to disable the default **bluetooth** daemon; it will interfere with `pybleno`.:

Do the following to stop it

```bash
sudo systemctl stop bluetooth
```

and then do the following to make sure it will not be restarted when the system is restarted:

```bash
sudo systemctl disable bluetooth
```

Then reboot your LAMPI to make sure we are properly configured.

After rebooting:

```bash
sudo systemctl status bluetooth
```

which should indicate that the 'bluetooth' is disabled.

### Starting Bluetooth HCI

Next we want to make sure the Bluetooth Host Controller Interface (HCI) is "up".  HCI is the standard used for software communication to Bluetooth hardware.  `hciconfig` is the Bluetooth equivalent of the `ifconfig` command for network interfaces.  On the Raspberry Pi 3, 'hci0' is the built-in Bluetooth device.

Run:

```bash
sudo hciconfig
```

which should output something like:

```bash
hci0:	Type: BR/EDR  Bus: UART
	BD Address: B8:27:EB:A2:EF:B4  ACL MTU: 1021:8  SCO MTU: 64:1
	UP RUNNING
	RX bytes:654 acl:0 sco:0 events:33 errors:0
	TX bytes:419 acl:0 sco:0 commands:33 errors:0
```

If you do not see 'UP RUNNING' you can start the HCI with 

```bash
sudo hciconfig hci0 up
```

To make sure that happens reliably everytime the system starts up, create a **supervisord** configuration like so:

```ini
[program:hci0_up]
command=/bin/hciconfig hci0 up
priority=200
autostart=true
autorestart=false
startretries=1
```

(note the `autorestart=false` and `startretries=1` - **hciconfig** runs and exits - it does not keep running).

## Simple iBeacon with `pybleno`

We are going to build our first BTLE Peripheral with `pybleno`; we will build a simple [iBeacon](https://en.wikipedia.org/wiki/IBeacon) compatible service.  iBeacon's are used for proximity detection - they periodically (typicallly a few times per second) broadcast a BTLE advertising packet.  BTLE Central devices can scan for nearby BTLE peripherals.  By measuring the strength of the BTLE received RF signal from the beacon, the Central can estimate the distance to the iBeacon device.  Because RF power measurements are noisy, the distance is just an estimate.  If multiple iBeacons are in the area, though, and the precise locations of iBeacons are known, a BTLE Central can develop a fairly accurate position (this is the indoor equivalent of GPS).

Generally BLTE Central's connect to Peripherals in two-phases:

1.  Discover BTLE Peripherals that are Advertising
2.  Connect to the desired BTLE Peripheral

For iBeacons, though, only Step 1 is done - iBeacon's Advertise, but are not connectable - they do not provide any actual BLTE Services (although they can provide a small amount of useful information in their broadcast Advertisement packets).

## Some Tools

To see whether or not your Raspberry Pi 3 BTLE is behaving as expected you will need some software tools.

These will be critical for the Assignment.

For general Bluetooth Debugging:

* [LightBlue Explorer for iOS](https://itunes.apple.com/us/app/lightblue-explorer-bluetooth-low-energy/id557428110?mt=8)
* [LightBlue for Android](https://play.google.com/store/apps/details?id=com.punchthrough.lightblueexplorer&hl=en_US)
* [BLE Scanner for Android](https://play.google.com/store/apps/details?id=com.macdom.ble.blescanner&hl=en)

Additionally, for the following section, having an iBeacon tool is handy:

* [Locate Beacon for iOS](https://itunes.apple.com/us/app/locate-beacon/id738709014?mt=8)
* [Locate Beacon for Android](https://play.google.com/store/apps/details?id=com.radiusnetworks.locate&hl=en)

(there are many options - find one you like).

### iBeacon

Create a new file on your LAMPI named **ibeacon.py**:

```python3
#! /usr/bin/env python3
from pybleno import Bleno
import sys
import signal
import time


uuid = 'B9407F30-F5F8-466E-AFF9-25556B57FE6D'  # Estimote iBeacon UUID
major = 0
minor = 0
measuredPower = -59


class DemoiBeacon():
    def __init__(self):
        self.bleno = Bleno()
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
            self.bleno.startAdvertisingIBeacon(
                uuid,
                major,
                minor,
                measuredPower,
            )
        else:
            self.bleno.stopAdvertising()

    def onAdvertisingStart(self, error):
        print('on -> advertisingStart: '
              + ('error ' + error if error else 'success'))


def main():
    ibeacon = DemoiBeacon()
    ibeacon.start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
```

Run this program:

```bash
python3 ibeacon.py
```

You should see `advertising` show up in the shell to indicate that `pybleno` is running and advertising now.

Using `LightBlue` in Discovery mode, you should see your device show up in the list (you can use the Filter option in the top right corner of the `LightBlue` discovery screen to filter out devices with low signal strength - this is helpful if you're in an area with many BTLE devices; put your phone near your LAMPI so the signal is very strong until you're sure you are seeing your device).

Using `LocateBeacon` look for an Estimote Beacon with Major and Minor of 0.  [Estimote](https://estimote.com/) is  a popular manufacturer of iBeacons.  We are using their UUID for this test, so `LocateBeacon` will identify your Raspberry Pi 3 device as an Estimote Beacon.

![](Images/our_ibeacon.png)

If you kill your NodeJS program (CTRL-C) the Beacon should disappear from the list (you might need to kill `LocateBeacon` and restart - it seems to cache the Beacon for a while).

#### iBeacon Application Explanation

What is the application doing?  Let's walk through it:

```python3
#! /usr/bin/env python3
from pybleno import Bleno
import sys, signal, time
```
> The above code imports the `Bleno` class and some additional Python packages.

```python3
uuid = 'B9407F30-F5F8-466E-AFF9-25556B57FE6D' # Estimote iBeacon UUID
major = 0
minor = 0
measuredPower = -59
```

> iBeacon's include four pieces of information in their Advertisement broadcasts (along with the standard BTLE Advertisement data):

> * a 128-bit UUID (BTLE makes heavy use of UUIDs) identifying the beacon type - typically identical for all beacons in a group; in our example we are using Estimote's UUID - since many third party tools (like `Locate Beacon` support Estimote iBeacons, our beacon shows up automatically
> * major number - a 16-bit value used to identitfy a specific beacon, in conjunction with `minor number`
> * minor number - a 16-bit value used to identitfy a specific beacon, in conjunction with `major number`
> * measured power at 1m - the transmit power of the beacon measured at 1m away in dB; used by receivers to estimate distance based on the [RSSI](https://en.wikipedia.org/wiki/Received_signal_strength_indication) (we are just making a number up here) 

```python3
class DemoiBeacon():
    def __init__(self):
        self.bleno = Bleno()
        self.bleno.on('stateChange', self.onStateChange)
        self.bleno.on('advertisingStart', self.onAdvertisingStart)
```
> `pybleno` uses a callback pattern for asynchronous event handling.  The `DemoiBeacon` class has an `__init__` method that creates a `Bleno` object and then assigns two event handlers - one for the the `stateChange` event and one for the `advertisingStart` event.

```python3
    def onStateChange(self, state):
        print('on -> stateChange: ' + state)

        if (state == 'poweredOn'):
            self.bleno.startAdvertisingIBeacon(
                uuid,
                major,
                minor,
                measuredPower,
            )
        else:
            self.bleno.stopAdvertising()
```
> The `stateChange` handler is called when the Bluetooth controller state changes - in this case, we catch an event when it powers up (initialized as a side-effect of the `Bleno` object initializer).  The "stateChange" event indicates changes to the hardware state (HCI) - in this case we watch for the "poweredOn" state to let us know that we can start advertising.  The call to the `bleno.startAdvertisingIBeacon()` method initiates adveritising as an iBeacon.

```python3
    def onAdvertisingStart(self, error):
        print('on -> advertisingStart: '
              + ('error ' + error if error else 'success'))
```
> The `advertisingStart` event indicates that the BTLE hardware is broadcasting the Advertising packets.  Normally we would set up our BTLE Services when Advertising has started.  Since iBeacons do not have any Services, that is not needed here (but will be later).

FYI, the Bluetooth Specifications require some additional Services for compliance - `pybleno` provides those automatically for you - you can see them in `pybleno`'s source code if you look in `hci-socket/Gatt.py`.


Next up: [09.2 Building a Simple BTLE GATT Service](../09.2_Building_a_Simple_BTLE_GATT_Service/README.md)

&copy; 2015-2024 LeanDog, Inc. and Nick Barendt
