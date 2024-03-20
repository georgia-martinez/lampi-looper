# Assignment

In this assignment you will build a working Bluetooth LAMPI and accompanying iOS application.

## Part 1 - LAMPI Service

The first part of the assignment is to build a working BLTE Service with `pybleno` to control LAMPI and update clients on setting changes.

Use `LightBlue` to debug and incrementally test and build your Bluetooth Solution.

All of the Python code for this assignment should located in your repository in the `Lampi/bluetooth` directory with the specified filenames.

The main Python file for your Bluetooth service should be named **ble_peripheral.py**.  **ble_peripheral.py** should be executable as a shell script (e.g., `#! /usr/bin/env python3`).

### Bluetooth Specifications

Please refer to [Core Specification 5.1](https://www.bluetooth.com/specifications/specs/core-specification-5-1/) - the first PDF file - for information on Characteristics and Descriptors.  Note, this is a somewhat daunting document.  Do not be intimidated - you can work your way through it.  Some things you might find useful in the specification:

* GATT `Characteristic User Description` (UUID 0x2901)
* GATT `Characteristic Presentation Format` (UUID 0x2904) (7 bytes or "octets")

Hints for `Characteristic Presentation Format`:

* `unitless` (0x2700) should be used for all Unit octets
* 0x01 is the Bluetooth SIG Namespace and should be used in the Name Space octet
* 0x0000 can be used for the Description octets


Please refer to [Device Information Service](https://www.bluetooth.com/specifications/specs/device-information-service-1-1/) for information about Bluetooth SIG defined Characteristics (e.g., "Manufacturer Name String", "Model Number String", etc.).

Please refer to 16-bitt UIIDs found in the [Assigned Numbers Dcoument](https://www.bluetooth.com/specifications/assigned-numbers/) for information about Bluetooth SIG defined UUIDs (including Characteristic Descriptors, Units - e.g., .


### Services

Your device should Advertise and support the following Services:

| Service Name | Service UUID | Filename |
| ------------ | ------------ | -------- |
| 'Device Information Service' | 0x180A | **device_info_service.py** |
| 'Lamp Service' | 0001A7D3-D8A4-4FEA-8174-1736E808C066 | **lampi_service.py** |

The 'Lamp Service' should be Advertised by name.


### Characteristics

#### Device Information Service Characteristics

The 'Device Information Service' should support the following Characteristics:

| Characteristic | UUID | Descriptors | Value |
| -------------- | ---- | ----------- | ----- |
| Manufacturer Name String | 0x2A29 | | 'CWRU' or 'CSU'| 
| | | 0x2901 :'Manufacturer Name'| |
| | | 0x2904 : appropriate value for Characterstic |  | 
| Model Number String | 0x2A24 | | 'LAMPI'| 
| | | 0x2901 : 'Model Number'| |
| | | 0x2904 : appropriate value for Characterstic |  | 
| Serial Number String | 0x2A25 | | Device_ID as a UTF-8 String | 
| | | 0x2901 : 'Serial Number'| |
| | | 0x2904 : appropriate value for Characterstic |  | 

All of the Device Information Service's Characterstics should be read-only.

(Hint: this is provided in the courseware.)

#### Lamp Service Characteristics

The 'Lamp Service' should support the following Characteristics:

| Characteristic | UUID |  Filename |
| -------------- | ---- |  ----- |
| On / Off       | 0004A7D3-D8A4-4FEA-8174-1736E808C066 | **on_off_characteristic.py** |
| Brightness     | 0003A7D3-D8A4-4FEA-8174-1736E808C066 | **brightness_characteristic.py** |
| HSV            | 0002A7D3-D8A4-4FEA-8174-1736E808C066 | **hsv_characteristic.py** |


| Characteristic | Descriptors | Value |
| -------------- |  ----------- | ----- |
| On / Off       |  | lamp on/off state encoded in single UINT8 (0x00 is OFF; 0x01 is ON)|
| | 0x2901 : 'On / Off'| |
| | 0x2904 : appropriate value for Characterstic |  |
| Brightness     |  | lamp brightness encoded in UINT8 (0x00 is 0.0; 0xFF is full brightness) |
| | 0x2901 : 'Brightness'| |
| | 0x2904: appropriate value for Characterstic |  |
| HSV     | | lamp HSV Color encoded in array of three UINT8 elements in this order [hue, saturation, value]  [0x00 is 0.0; 0xFF is full hue/saturation] - value should always be 0xFF|
| | 0x2901 : 'HSV'| |
| | 0x2904 : appropriate value for Characterstic |  |


All of the 'Lamp Service' Service's Characterstics should support: read, write, and notify.


### Lamp State

Your application will need to maintain Lamp state, and keep that state updated - this is exactly analogous to the `NumberState` of our demo `pybleno` application.  The Lamp state class should be in a file named **lampi_state.py**


The Lamp Service must communicate with MQTT to change the configuration of LAMPI as well as be updated when other's update the configuration (e.g., the touchscreen).  This should work exactly as the MQTT integration in the demo applciation.


You should be able to control your lamp with `LightBlue` and see notifications of Lamp state changes (e.g., On/Off, Brightness, Hue, Saturation) when the Lamp is controlled from the touchscreen.

**NOTE:** _your service should ignore lamp state updates that it caused to occur (like our other clients), to prevent feedback loops._

### Supervisor

Your **ble_peripheral.py** application should automatically start at boot time.  Here's a Supervisor configuration for it (autostart and autorestart).

```ini
[program:bluetooth_service]
command="{{ repo_directory }}/Lampi/bluetooth/ble_peripheral.py"
directory={{ repo_directory }}/Lampi/
environment=HOME="/home/pi"
priority=500
autostart=true
autorestart=true
```

## Part 2 - iOS Application

**AFTER** successfully building your Bluetooth solution and testing it with `LightBlue` you can work on Part 2 of the Assignment - updating our iOS application to interact with the lamp.  There is enough complexity in building the iOS app that you should get everything working as expected via `LightBlue` before starting on building the iOS application.

You should start with the iOS solution from the previous week provided in [Mobile/iOS/Lampi/Lampi.xcodeproj](../../Mobile/iOS/Lampi/Lampi.xcodeproj).  You should modify that project and submit an updated version of that project.

Your iOS application needs to discover and connect to only one LAMPI.

When complete, your iOS application should:

* Upon startup, update the UI to reflect the current state of the LAMP
* Encapsulate the On/Off, Brightness, Hue, Saturation and Connection properties into a single State structure.
* Changing On/Off, Brightness, Hue, or Saturation in the iOS application should cause the Lamp to update via BTLE
* Changing On/Off, Brightness, Hue, or Saturation on the touchscreen should cause the iOS application to update via BTLE Notifications
* Do not allow input into the iOS application until all required Characteristics are discovered.
* Limit BTLE write rates to something reasonable (e.g., with `dispatch_after`)
* Handle BTLE disconnections in the application by automatically reconnecting 

The Hue and Saturation is packed into a 3-byte value -- hue is the first byte and saturation is the second byte, represented as 0-255. The third byte is ignored. Here is how to parse it from Data:

```swift
guard let value = hsvCharacteristic.value else { return }

var newState = state // this effectively copies the current state

// update our copy with the new values
newState.hue = Double(value[0]) / 255.0
newState.saturation = Double(value[1]) / 255.0

// set to the new state
state = newState
```

> NOTE: This example uses an early exit to ensure the characteristic value is not nil.

Here is how to pack it into Data:

```swift
var hsv: UInt32 = 0
let hueInt = UInt32(state.hue * 255.0)
let satInt = UInt32(state.saturation * 255.0)
let valueInt = UInt32(255)

hsv = hueInt
hsv += satInt << 8
hsv += valueInt << 16

let data = Data(bytes: &hsv, count: 3)
```

## What to Turn in 

You need to turn in the following:

1. A short (a few sentences) write up from each member of the pair summarizing what they learned completing the assignment, and one thing that surprised them (good, bad, or just surprising).  This should in **connected-devices/writeup.md** in [Markdown](https://daringfireball.net/projects/markdown/) format.  You can find a template file in **connected-devices/template\_writeup.md**
2. A Git Pull Request
3. A short video demonstrating the required behaviors emailed to the instructor and TA.  The video should be named **[assignment 3]_[LAST_NAME_1]\_[LAST_NAME_2].[video format]**.  So, for this assignment, if your pair's last names are "Smith" and "Jones" and you record a .MOV, you would email a file named ```2_smith_jones.mov``` to the instructor.
4. A live demo at the beginning of the next class - **be prepared!**

Notes:

* The video must show the iOS app running on an iOS device AND the LAMPI AND your Web Browser Interface at the same time.
* Each pair must have a Mac with Xcode and an iOS device between them.


&copy; 2015-2024 LeanDog, Inc. and Nick Barendt
