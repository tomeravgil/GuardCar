# GuardCar

Welcome to GuardCar. GuardCar is a Computer Vision Powered Car Monitor with multifunctionality.

# Things to get started

In order to use, you must have a:

- Raspberry Pi 5
- Google Coral TPU
- 2 IR Cameras

# Steps to install

Download Raspberry Pi Debian 64-bit and go to terminal

run 

```
sudo rpi-update d16727d
sudo reboot
```

then open back up terminal and run installation.sh. This will install docker and the edge tpu runtime.

Once installed, run build.sh. This will build and run the docker containers needed to run the program.