# msfs2fltplan
 Connects Microsoft Flight Simulator 2020 (MSFS 2020) to the mobile [FltPlan Go](https://www.fltplan.com/) app. This tool allows you to specify the IP address of your mobile device running FltPlan Go, and is primarily for users who cannot run MSFS and FltPlan Go on the same local network, or are having trouble using the official FltPlan Go FSX plugin.

 (This tool should also connect you to [ForeFlight](https://foreflight.com/itunes) as well, although that use is unsupported.)

## Install
1) Install the 64-bit version of [Python 3](https://www.python.org/ftp/python/3.8.6/python-3.8.6-amd64.exe). (Make sure you check the option to add Python to your PATH.)
2) Download [the latest release of this tool](https://github.com/musurca/msfs2fltplan/releases/download/v1.0/msfs2fltplan_v1.0.zip) and unzip to a directory of your choice, e.g. `C:\fltplan`

## How to Use
1) Run Microsoft Flight Simulator.
2) From a command-line, switch to the directory into which you installed this repository.
3) Run `connect [ip_address]` using the IP address of your mobile device running FltPlan Go. For example:
```
connect 10.20.223.11
``` 
4) In FltPlan Go, go to the External menu and select "X-Plane" from the Simulators category. After a few seconds, the Status should turn green and read "Connected."
5) Done! (If you don't see your plane on the map, make sure you've turned on "Enable Ship Position" in the FltPlan Go settings.)

NOTE: You can also connect to more than one device running FltPlan Go by specifying multiple IP addresses, e.g.:
```
connect 10.20.223.11 240.10.113.34 192.168.0.52
```

## Dependencies
* [Python 3](https://www.python.org/downloads/)
* [Python-SimConnect](https://github.com/odwdinc/Python-SimConnect)
* FltPlan Go ([iOS](https://apps.apple.com/us/app/fltplan-go/id694832363) / [Android](https://play.google.com/store/apps/details?id=com.fltplan.go&hl=en_US))
