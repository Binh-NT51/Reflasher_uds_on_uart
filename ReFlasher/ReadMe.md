<h3 align="center">Reflasher</h3>

<div align="center">

  [![Status](https://img.shields.io/badge/status-active-success.svg)]() 

</div>

---

<p align="center"> Tester to reprogram a binary file to the target.
    <br> 
</p>

## Table of Contents
- [About](#about)
- [Getting Started](#getting_started)
- [Uage](#usage)
- [Development Guide](#development_guide)
- [Contributors](#contributors)
- [License](#license)

## About <a name = "about"></a>
To verify the reprogramming of application feature in DNGA Pre-Development project, Reflasher is designed as a slight tool to reflash the binary file to the target by using UDS on UART.

## Getting Started <a name = "getting_started"></a>
### Prerequisites
#### Target set-up
User shall ensure that the binaries of hsm, flash boot, dual bank manager and application are flashed into the target (using debugger).
If it is satisfied, please contact supporter for help.

#### Connection set-up
The target is connected to the host (PC/ Rasperry Pi) by USB-UART connector. Ensure that device driver is installed in your host (.\utils\CP210x_Universal_Windows_Driver.zip).
Connect 3 pins GND, TXD, RXD from the device correspondingly to GND, RXD, TXD of the target. Do not connect 3v3 pin in case there is no debugger connected.

#### Prepare application binary file
Currently ReFlasher only accepts hex file with seamless data (no empty data block in hex file). In DNGA pre-dev, user need to convert .s19 file to .hex file.
Use hexConverter to convert .s19 to .hex file. Refer the manual: \hexConverter\Readme.md

### Installing
**For user**: no need to install the environment. Just run .exe file to start the tool. 

If you are developer, below environment is required to modify the tool:
- Python 3.7.x or above
- pip

For developer only, run setup.py to setup the environment to run the project.
```
- Run setup.py
```

## Uage    <a name = "uage"></a>
- **Start the tool**
    - For user:
    ```
    - Run bin\ReFlasher.exe
    ```
    - For developer:
    ```
    - Run reflasher\mainGUI.py
    ```
The GUI will be launched. Then, follow below steps to configure and run the reflashing:

![Alt text](docs/images/Steps_Run.PNG?raw=true "Steps to run")

- **Serial communcation**

    **1.** Select serial port name that connects to uart channel of target. User can check the device manager in PC or in /dev/ in Linux system.
    
    **2.** Select proper baudrate supported by that channel. Currently, the target is only support 115200. Please select 115200. 
    
    **3.** Click Apply to save the configuration

- **Binary of application file**

    **4.** Browse to the valid application file in format of .hex

- **Logging**

    **5.** Select the folder where the log file will be stored. The name of the log file is current date time. If no log file is specified, no log file is generated.

- **Reflash**

    **6.** Finally, click Download to start the download sequence.

The progress of download is displayed in the GUI and user can check the log after the download sequence is finished.

## Development Guide <a name = "development_guide"></a>
For developer who would like to improve or customize the tool. Please refer the docs for the guide.

## Contributors <a name = "contributors"></a>
Supporter:
```
Nguyen Thanh Binh
```

## License <a name = "license"></a>
This tool is free to use.