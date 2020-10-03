# msfs2fltplan
 Connects Microsoft Flight Simulator 2020 (MSFS 2020) to the mobile [FltPlan Go](https://www.fltplan.com/) app. This tool allows you to specify the IP address of your mobile device running FltPlan Go, and is primarily for users who cannot run MSFS and FltPlan Go on the same local network, or are having trouble using the official FltPlan Go FSX plugin.

 (This tool should also connect you to [ForeFlight](https://foreflight.com/itunes) as well, although that use is unsupported.)

## Install
1) Install the 64-bit version of [Python 3](https://www.python.org/ftp/python/3.8.6/python-3.8.6-amd64.exe). (Make sure you check the option to add Python to your PATH.)
2) Download [the latest release of this tool](https://github.com/musurca/msfs2fltplan/releases/download/v1.1/msfs2fltplan_v1.1.zip) and unzip to a directory of your choice, e.g. `C:\fltplan`

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

## Troubleshooting

Make sure you’re using the right IP address for your network setup. There are a few possibilities here:

* If the computer running MSFS and your mobile device are on the same local wifi network (the easiest way), you can just use the IP address reported by your mobile device.
(iOS) Settings -> Wi-Fi -> (your network) -> IP Address
(Android) Settings -> About -> Status -> IP Address

* However, if they’re on different networks, things get a little more complicated. By far the easiest way to handle this situation is to use a free VPN service like [ZeroTier One](https://www.zerotier.com/) to connect your computer and your mobile device on a virtual local network. (There are clients for Windows, iOS, and Android.) When activated, the ZeroTier client will give your mobile device a static IP address that only works on that network, and that would be the IP you would plug into the script.

* If your devices are on different networks and you can’t use a VPN like ZeroTier for whatever reason, you’ll need to configure the wifi router used by your mobile device to assign it a static IP on the network, and to forward incoming UDP packets on port 49002 directly to that IP. However, that will NOT be the IP you’ll plug into the script. Instead you’ll want to use the external IP address, which can be found by going to https://whatismyipaddress.com/ on your mobile device.

## Dependencies
* [Python 3](https://www.python.org/downloads/)
* [Python-SimConnect](https://github.com/odwdinc/Python-SimConnect)
* FltPlan Go ([iOS](https://apps.apple.com/us/app/fltplan-go/id694832363) / [Android](https://play.google.com/store/apps/details?id=com.fltplan.go&hl=en_US))
