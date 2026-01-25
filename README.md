# Luminosity Server Setup Guid

This guide explains how to set up and build the system step by step.

## 1. Install Raspberry Pi OS on an External SSD

1. Download the **Raspberry Pi Imager** from the official page: [Raspberry Pi Imager](https://www.raspberrypi.com/software/).  
2. Use the Imager to flash the **64-bit version** of Raspberry Pi OS onto your **external SSD**.  
3. Connect the SSD to your Raspberry Pi and power it on.  
4. Ensure your Raspberry Pi is set to boot from USB/SSD (check [Raspberry Pi boot options](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#usb-boot)).
5. Ensure your Raspberry Pi is connected to the internet (check [Raspberry Pi network configuration](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#network-configuration)).
To set up the network, you need display and keyboard.
6. Ensure username is **dev**, fixed directory pathes has been used in the code.

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
sudo apt instal npm
sudo apt install cmake
```
3. Update ldconfig: `sudo ldconfig`
4. Check the installed packages: `ldconfig -p | grep opencv`, `ldconfig -p | grep libzmq`

## 4. Clone the Repository

1. Connect to your Raspberry Pi via SSH.
2. Clone the repository: `git clone https://github.com/mojtaba1989/hlm_web.git`
3. Navigate to the cloned directory: `cd hlm_web`

## 5. Build the C++ video recorder node

1. Connect to your Raspberry Pi via SSH.
2. Navigate to the repository directory: `cd hlm_web/backend/nodes`
3. Create a build directory: `mkdir build`
4. Navigate to the build directory: `cd build`
5. Run CMake: `cmake ..`
6. Build the project: `make`
7. Check the video recorder node: `./rec test.avi`

## 6. Install Node.js Dependencies

1. Connect to your Raspberry Pi via SSH.
2. Navigate to the repository directory: `cd hlm_web/frontend`
3. Install dependencies: `npm install`

## 7. Install Python Dependencies

1. Connect to your Raspberry Pi via SSH.
2. Create a virtual environment: `python3 -m venv ~/hlm_env`
3. Append system-side packages to the virtual environment: `python3 -m venv --system-site-packages ~/hlm_env` 
3. Add the virtual environment to the bash profile: `echo "source ~/hlm_env/bin/activate" >> ~/.bashrc` [REQUIRED for headless mode]
4. Activate the virtual environment: `source ~/hlm_env/bin/activate`
**Note**: Manually adding the virtual environment to the bash profile is not required if source cmd is added to the .bashrc file. Check this with `source ~/.bashrc`.
5. Install dependencies: `pip install -r requirements.txt`

## 8. Test and Run the Server

1. Connect to your Raspberry Pi via SSH.
2. Navigate to the repository directory: `cd hlm_web`
3. Run the server: `./run_dev.sh`

If it successfully starts, the server should be accessible at `http://<Raspberry Pi IP>:3000.`

## 9. Setup Headless Mode

1. Connect to your Raspberry Pi via SSH.
2. Copy the `hlm_server.service` file to the `/etc/systemd/system/` directory: `sudo cp hlm_server.service /etc/systemd/system/`
3. Reload the systemd daemon: `sudo systemctl daemon-reload`
4. Enable the service: `sudo systemctl enable hlm_server.service`
5. Start the service: `sudo systemctl start hlm_server.service`

If it successfully starts, the server should be accessible at `http://<Raspberry Pi IP>:3000.`

Restart the Pi to check if it works. You should be able to access the server at `http://<Raspberry Pi IP>:3000.` within network.

