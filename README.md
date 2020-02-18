# PEBCAW

![](https://raw.githubusercontent.com/wdbm/pebcaw/master/media/The_Pier.png)

PEBCAW (Problem Exists Between Computer And World) monitors internet connection security by comparing the observed IP or country with a whitelist of VPN and Tor IPs or a whitelist of countries. It notifies if the IP or country is not whitelisted, and optionally can notify if the IP is in a SIGINT country, and optionally can display observed IP details continuously.

# setup

```Bash
pip install pebcaw
```

# usage

```Bash
pebcaw
```

```Bash
pebcaw --help
```
