
#!/usr/bin/python


from mn_wifi.net import Mininet_wifi
from mn_wifi.cli import CLI


if __name__ == '__main__':
    info("*** Running CLI (Network will not stop)\n")
    # Start the CLI so you can interact with the network
    net = Mininet_wifi()
    CLI(net)
