# Luminosity Server Setup Guid

This guide explains how to set up and build the system step by step.

## 1. Install Raspberry Pi OS on an External SSD

1. Download the **Raspberry Pi Imager** from the official page: [Raspberry Pi Imager](https://www.raspberrypi.com/software/).  
2. Use the Imager to flash the **64-bit version** of Raspberry Pi OS onto your **external SSD**.  
3. Connect the SSD to your Raspberry Pi and power it on.  
4. Ensure your Raspberry Pi is set to boot from USB/SSD (check [Raspberry Pi boot options](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#usb-boot)).

## 2. Update and Upgrade Raspberry Pi OS

1. Connect to your Raspberry Pi via SSH.  
2. Update the system: `sudo apt update && sudo apt upgrade -y`  
3. Reboot the system: `sudo reboot`

## 3. Install Required Packages

1. Connect to your Raspberry Pi via SSH.
2. Install the following packages:
```
sudo apt install libopencv-dev
sudo apt install libzmq3-dev
```

