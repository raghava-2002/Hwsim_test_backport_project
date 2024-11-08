import re
from collections import defaultdict
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.colors as mcolors

# Sample data as a multi-line string
data = """
[104490.655846] Ap: random MAC: ca:7a:fd:c9:77:fd base mac: 02:00:00:00:00:00
[104490.655886] Ap: random MAC: 0e:b7:ec:4f:61:de base mac: 02:00:00:00:01:00
[104490.655892] Ap: random MAC: d6:3a:e4:c6:8f:cb base mac: 02:00:00:00:02:00
[104490.655898] Ap: random MAC: de:26:e9:ba:da:f1 base mac: 02:00:00:00:03:00
[104490.655903] Ap: random MAC: 8e:55:8f:14:24:30 base mac: 02:00:00:00:05:00
[104490.655909] Ap: random MAC: ba:e6:3d:1a:d6:63 base mac: 02:00:00:00:04:00
[104490.655927] Ap: random MAC: 96:73:78:4a:3a:c4 base mac: 02:00:00:00:06:00
[104490.655933] Ap: random MAC: 82:65:57:34:ca:a5 base mac: 02:00:00:00:08:00
[104490.655944] Ap: random MAC: 6e:2d:cd:64:26:cd base mac: 02:00:00:00:07:00
[104490.655950] Ap: random MAC: da:ac:75:6f:c6:b0 base mac: 02:00:00:00:09:00
[104490.655955] Ap: random MAC: be:be:a7:23:e0:ff base mac: 02:00:00:00:0a:00
[104505.592411] Ap: random MAC: be:ec:75:06:df:b5 base mac: 02:00:00:00:00:00
[104505.592419] Ap: random MAC: 1a:e5:56:f4:6b:49 base mac: 02:00:00:00:01:00
[104505.592424] Ap: random MAC: c6:99:ba:f7:50:19 base mac: 02:00:00:00:02:00
[104505.592429] Ap: random MAC: 8a:41:f2:0a:67:66 base mac: 02:00:00:00:03:00
[104505.592434] Ap: random MAC: 5a:dc:29:8c:28:25 base mac: 02:00:00:00:05:00
[104505.592439] Ap: random MAC: 56:f7:2d:9d:9c:6d base mac: 02:00:00:00:04:00
[104505.592445] Ap: random MAC: b6:75:3c:cb:ef:fe base mac: 02:00:00:00:06:00
[104505.592452] Ap: random MAC: ae:a8:44:00:5b:02 base mac: 02:00:00:00:08:00
[104505.592457] Ap: random MAC: 5e:20:34:28:bb:f2 base mac: 02:00:00:00:07:00
[104505.592470] Ap: random MAC: 1e:33:06:04:89:3d base mac: 02:00:00:00:09:00
[104505.592510] Ap: random MAC: 2e:8a:ee:31:d4:86 base mac: 02:00:00:00:0a:00
[104520.645178] Ap: random MAC: 72:76:dd:63:fa:7c base mac: 02:00:00:00:00:00
[104520.645179] Ap: random MAC: ae:93:9b:16:79:56 base mac: 02:00:00:00:01:00
[104520.645180] Ap: random MAC: 86:39:c3:55:20:b8 base mac: 02:00:00:00:02:00
[104520.645181] Ap: random MAC: b6:fd:bb:57:31:4d base mac: 02:00:00:00:03:00
[104520.645182] Ap: random MAC: 66:1d:36:1b:13:b0 base mac: 02:00:00:00:05:00
[104520.645183] Ap: random MAC: 06:6f:60:57:0e:29 base mac: 02:00:00:00:04:00
[104520.645184] Ap: random MAC: 02:fc:0a:7c:69:bd base mac: 02:00:00:00:06:00
[104520.645185] Ap: random MAC: 9e:ec:58:58:da:db base mac: 02:00:00:00:08:00
[104520.645186] Ap: random MAC: de:13:f6:b7:9a:d8 base mac: 02:00:00:00:07:00
[104520.645187] Ap: random MAC: ea:01:98:dd:ad:9d base mac: 02:00:00:00:09:00
[104520.645188] Ap: random MAC: 1e:7c:77:e0:7a:f2 base mac: 02:00:00:00:0a:00
[104535.595407] Ap: random MAC: ea:c3:c8:07:31:9f base mac: 02:00:00:00:00:00
[104535.595412] Ap: random MAC: 62:56:e8:32:ad:27 base mac: 02:00:00:00:01:00
[104535.595414] Ap: random MAC: 12:63:20:18:15:ed base mac: 02:00:00:00:02:00
[104535.595417] Ap: random MAC: 42:f3:9a:79:d1:f2 base mac: 02:00:00:00:03:00
[104535.595420] Ap: random MAC: 62:32:10:3e:16:18 base mac: 02:00:00:00:05:00
[104535.595423] Ap: random MAC: d6:97:ff:08:0c:a1 base mac: 02:00:00:00:04:00
[104535.595425] Ap: random MAC: c6:f0:e3:58:65:ef base mac: 02:00:00:00:06:00
[104535.595428] Ap: random MAC: a2:9c:32:52:88:70 base mac: 02:00:00:00:08:00
[104535.595431] Ap: random MAC: ce:75:d7:3d:e2:91 base mac: 02:00:00:00:07:00
[104535.595434] Ap: random MAC: c2:56:43:ad:49:77 base mac: 02:00:00:00:09:00
[104535.595439] Ap: random MAC: 7a:6e:d5:40:0e:c0 base mac: 02:00:00:00:0a:00
[104550.648231] Ap: random MAC: 16:9b:b9:e7:00:83 base mac: 02:00:00:00:00:00
[104550.648237] Ap: random MAC: c6:4a:f4:c6:d7:60 base mac: 02:00:00:00:01:00
[104550.648244] Ap: random MAC: 72:89:ac:65:ef:a3 base mac: 02:00:00:00:02:00
[104550.648251] Ap: random MAC: 42:1f:31:7c:a5:28 base mac: 02:00:00:00:03:00
[104550.648257] Ap: random MAC: c2:a3:0a:73:88:f9 base mac: 02:00:00:00:05:00
[104550.648263] Ap: random MAC: 16:54:36:9f:54:c4 base mac: 02:00:00:00:04:00
[104550.648272] Ap: random MAC: 2e:65:61:f3:57:9d base mac: 02:00:00:00:06:00
[104550.648281] Ap: random MAC: ea:2e:9c:df:13:4f base mac: 02:00:00:00:08:00
[104550.648286] Ap: random MAC: ca:98:61:95:06:47 base mac: 02:00:00:00:07:00
[104550.648291] Ap: random MAC: a6:01:1f:06:ae:a2 base mac: 02:00:00:00:09:00
[104550.648297] Ap: random MAC: 0e:80:38:65:55:ca base mac: 02:00:00:00:0a:00
[104565.598795] Ap: random MAC: 26:c3:7d:2e:74:7d base mac: 02:00:00:00:00:00
[104565.598802] Ap: random MAC: 6a:77:71:1a:b6:49 base mac: 02:00:00:00:01:00
[104565.598811] Ap: random MAC: 42:10:02:81:54:f8 base mac: 02:00:00:00:02:00
[104565.598817] Ap: random MAC: 26:7d:70:c2:18:a2 base mac: 02:00:00:00:03:00
[104565.598822] Ap: random MAC: 2e:08:9e:b6:5a:3e base mac: 02:00:00:00:05:00
[104565.598828] Ap: random MAC: c6:53:db:04:ff:ca base mac: 02:00:00:00:04:00
[104565.598837] Ap: random MAC: 6a:ec:bd:20:82:0b base mac: 02:00:00:00:06:00
[104565.598856] Ap: random MAC: e2:c4:98:bd:d7:69 base mac: 02:00:00:00:08:00
[104565.598861] Ap: random MAC: 5a:2a:70:24:0f:3b base mac: 02:00:00:00:07:00
[104565.598867] Ap: random MAC: 86:00:aa:8e:82:7e base mac: 02:00:00:00:09:00
[104565.598874] Ap: random MAC: 5e:7d:68:aa:3f:bb base mac: 02:00:00:00:0a:00
[104580.651422] Ap: random MAC: b6:66:07:47:0c:56 base mac: 02:00:00:00:00:00
[104580.651426] Ap: random MAC: a6:82:5f:ed:9c:9f base mac: 02:00:00:00:01:00
[104580.651432] Ap: random MAC: 66:77:7e:f7:77:39 base mac: 02:00:00:00:02:00
[104580.651435] Ap: random MAC: ae:1c:29:fd:be:4b base mac: 02:00:00:00:03:00
[104580.651450] Ap: random MAC: 2a:55:e1:53:4a:cc base mac: 02:00:00:00:05:00
[104580.651453] Ap: random MAC: 32:2a:ce:c8:f9:5f base mac: 02:00:00:00:04:00
[104580.651456] Ap: random MAC: 8a:4b:d4:db:d4:11 base mac: 02:00:00:00:06:00
[104580.651459] Ap: random MAC: 0e:82:67:65:bb:53 base mac: 02:00:00:00:08:00
[104580.651462] Ap: random MAC: 0e:d4:b4:5d:80:52 base mac: 02:00:00:00:07:00
[104580.651479] Ap: random MAC: 46:5e:fa:8e:74:f1 base mac: 02:00:00:00:09:00
[104580.651492] Ap: random MAC: 96:d4:a6:ce:14:3f base mac: 02:00:00:00:0a:00
[104595.602163] Ap: random MAC: 2e:ef:1c:f2:2e:27 base mac: 02:00:00:00:00:00
[104595.602167] Ap: random MAC: 76:e6:36:cd:65:94 base mac: 02:00:00:00:01:00
[104595.602171] Ap: random MAC: 02:f4:f8:7f:a8:bb base mac: 02:00:00:00:02:00
[104595.602173] Ap: random MAC: 5a:9f:fb:2b:3f:1f base mac: 02:00:00:00:03:00
[104595.602176] Ap: random MAC: 62:8b:8f:17:05:6f base mac: 02:00:00:00:05:00
[104595.602179] Ap: random MAC: 3a:cb:4e:c0:7f:73 base mac: 02:00:00:00:04:00
[104595.602183] Ap: random MAC: 56:22:45:a9:21:b6 base mac: 02:00:00:00:06:00
[104595.602186] Ap: random MAC: 26:c0:3d:cf:bc:5d base mac: 02:00:00:00:08:00
[104595.602188] Ap: random MAC: 06:d0:6c:50:37:3a base mac: 02:00:00:00:07:00
[104595.602191] Ap: random MAC: ca:3f:59:f8:1d:6e base mac: 02:00:00:00:09:00
[104595.602194] Ap: random MAC: 86:cf:81:05:20:46 base mac: 02:00:00:00:0a:00
[104610.654633] Ap: random MAC: e2:f1:e3:3f:4e:94 base mac: 02:00:00:00:00:00
[104610.654640] Ap: random MAC: ba:2a:60:6a:68:b6 base mac: 02:00:00:00:01:00
[104610.654648] Ap: random MAC: ce:66:ec:91:ed:4e base mac: 02:00:00:00:02:00
[104610.654653] Ap: random MAC: 92:10:2a:e8:18:e7 base mac: 02:00:00:00:03:00
[104610.654659] Ap: random MAC: 9a:dd:73:dd:e9:4f base mac: 02:00:00:00:05:00
[104610.654664] Ap: random MAC: 1e:f4:0c:2d:a6:51 base mac: 02:00:00:00:04:00
[104610.654670] Ap: random MAC: be:48:65:88:e4:0d base mac: 02:00:00:00:06:00
[104610.654675] Ap: random MAC: e2:1b:93:3a:b8:31 base mac: 02:00:00:00:08:00
[104610.654680] Ap: random MAC: 36:8b:a2:90:95:34 base mac: 02:00:00:00:07:00
[104610.654685] Ap: random MAC: 92:da:9e:88:1b:97 base mac: 02:00:00:00:09:00
[104610.654693] Ap: random MAC: 06:84:82:0d:fe:4b base mac: 02:00:00:00:0a:00
"""

# Dictionary to store sets of MAC address transitions for each base MAC
mac_sets = defaultdict(set)

# Regex pattern to extract random and base MAC addresses
pattern = re.compile(r"random MAC: ([\da-f:]+) base mac: ([\da-f:]+)")

# Parse the data and populate mac_sets
#for line in data.strip().splitlines():
#    match = pattern.search(line)
#    if match:
#         random_mac, base_mac = match.groups()
#        mac_sets[base_mac].add(random_mac)
#
# Parse the data and populate mac_sets while maintaining order
for line in data.strip().splitlines():
    match = pattern.search(line)
    if match:
        random_mac, base_mac = match.groups()
        if base_mac not in mac_sets:
            mac_sets[base_mac] = []  # Initialize as a list to preserve order
        mac_sets[base_mac].append(random_mac)


# Print the sets
for base_mac, random_macs in mac_sets.items():
    print(f"Base MAC: {base_mac}")
    print("Random MACs:")
    for random_mac in random_macs:
        print(f"  - {random_mac}")
    print()


# Example linking log
linking_log = """
Linked Old MAC: 02:00:00:00:05:00 -> New MAC: 96:73:78:4a:3a:c4 with time diff: 0.000994 seconds
Linked Old MAC: 02:00:00:00:07:00 -> New MAC: be:be:a7:23:e0:ff with time diff: 0.026506 seconds
Linked Old MAC: 02:00:00:00:0a:00 -> New MAC: ca:7a:fd:c9:77:fd with time diff: 0.068489 seconds
Linked Old MAC: 02:00:00:00:08:00 -> New MAC: 0e:b7:ec:4f:61:de with time diff: 0.026136 seconds
Linked Old MAC: 02:00:00:00:03:00 -> New MAC: 8e:55:8f:14:24:30 with time diff: 0.002057 seconds
Linked Old MAC: 02:00:00:00:02:00 -> New MAC: 6e:2d:cd:64:26:cd with time diff: 0.028336 seconds
Linked Old MAC: 02:00:00:00:00:00 -> New MAC: 82:65:57:34:ca:a5 with time diff: 0.027636 seconds
Linked Old MAC: 02:00:00:00:01:00 -> New MAC: de:26:e9:ba:da:f1 with time diff: 0.030572 seconds
Linked Old MAC: 02:00:00:00:06:00 -> New MAC: d6:3a:e4:c6:8f:cb with time diff: 0.075814 seconds
Linked Old MAC: 96:73:78:4a:3a:c4 -> New MAC: 56:f7:2d:9d:9c:6d with time diff: 0.001488 seconds
Linked Old MAC: be:be:a7:23:e0:ff -> New MAC: 5e:20:34:28:bb:f2 with time diff: 0.408350 seconds
Linked Old MAC: ca:7a:fd:c9:77:fd -> New MAC: ae:a8:44:00:5b:02 with time diff: 0.018113 seconds
Linked Old MAC: 0e:b7:ec:4f:61:de -> New MAC: 8a:41:f2:0a:67:66 with time diff: 0.292124 seconds
Linked Old MAC: 8e:55:8f:14:24:30 -> New MAC: 5a:dc:29:8c:28:25 with time diff: 0.008202 seconds
Linked Old MAC: 6e:2d:cd:64:26:cd -> New MAC: be:ec:75:06:df:b5 with time diff: 0.025312 seconds
Linked Old MAC: 82:65:57:34:ca:a5 -> New MAC: c6:99:ba:f7:50:19 with time diff: 0.058931 seconds
Linked Old MAC: de:26:e9:ba:da:f1 -> New MAC: b6:75:3c:cb:ef:fe with time diff: 0.059638 seconds
Linked Old MAC: d6:3a:e4:c6:8f:cb -> New MAC: 2e:8a:ee:31:d4:86 with time diff: 0.100366 seconds
Linked Old MAC: ba:e6:3d:1a:d6:63 -> New MAC: 1a:e5:56:f4:6b:49 with time diff: 0.157568 seconds
Linked Old MAC: da:ac:75:6f:c6:b0 -> New MAC: 1e:33:06:04:89:3d with time diff: 0.268099 seconds
Linked Old MAC: 56:f7:2d:9d:9c:6d -> New MAC: 02:fc:0a:7c:69:bd with time diff: 0.002862 seconds
Linked Old MAC: 5e:20:34:28:bb:f2 -> New MAC: 72:76:dd:63:fa:7c with time diff: 0.015371 seconds
Linked Old MAC: ae:a8:44:00:5b:02 -> New MAC: 86:39:c3:55:20:b8 with time diff: 0.014284 seconds
Linked Old MAC: 8a:41:f2:0a:67:66 -> New MAC: b6:fd:bb:57:31:4d with time diff: 0.020670 seconds
Linked Old MAC: 5a:dc:29:8c:28:25 -> New MAC: de:13:f6:b7:9a:d8 with time diff: 0.002933 seconds
Linked Old MAC: be:ec:75:06:df:b5 -> New MAC: 9e:ec:58:58:da:db with time diff: 0.020324 seconds
Linked Old MAC: c6:99:ba:f7:50:19 -> New MAC: ea:01:98:dd:ad:9d with time diff: 0.021006 seconds
Linked Old MAC: b6:75:3c:cb:ef:fe -> New MAC: 1e:7c:77:e0:7a:f2 with time diff: 0.021454 seconds
Linked Old MAC: 2e:8a:ee:31:d4:86 -> New MAC: ae:93:9b:16:79:56 with time diff: 0.015115 seconds
Linked Old MAC: 1a:e5:56:f4:6b:49 -> New MAC: 06:6f:60:57:0e:29 with time diff: 0.014824 seconds
Linked Old MAC: 1e:33:06:04:89:3d -> New MAC: 66:1d:36:1b:13:b0 with time diff: 0.035668 seconds
Linked Old MAC: 02:fc:0a:7c:69:bd -> New MAC: c2:56:43:ad:49:77 with time diff: 0.018199 seconds
Linked Old MAC: 72:76:dd:63:fa:7c -> New MAC: c6:f0:e3:58:65:ef with time diff: 0.013115 seconds
Linked Old MAC: 86:39:c3:55:20:b8 -> New MAC: d6:97:ff:08:0c:a1 with time diff: 0.014461 seconds
Linked Old MAC: b6:fd:bb:57:31:4d -> New MAC: a2:9c:32:52:88:70 with time diff: 0.014010 seconds
Linked Old MAC: de:13:f6:b7:9a:d8 -> New MAC: 12:63:20:18:15:ed with time diff: 0.012018 seconds
Linked Old MAC: 9e:ec:58:58:da:db -> New MAC: ea:c3:c8:07:31:9f with time diff: 0.022160 seconds
Linked Old MAC: ea:01:98:dd:ad:9d -> New MAC: 7a:6e:d5:40:0e:c0 with time diff: 0.024686 seconds
Linked Old MAC: 1e:7c:77:e0:7a:f2 -> New MAC: 42:f3:9a:79:d1:f2 with time diff: 0.018121 seconds
Linked Old MAC: ae:93:9b:16:79:56 -> New MAC: 62:32:10:3e:16:18 with time diff: 0.016092 seconds
Linked Old MAC: 06:6f:60:57:0e:29 -> New MAC: 62:56:e8:32:ad:27 with time diff: 0.025860 seconds
Linked Old MAC: 66:1d:36:1b:13:b0 -> New MAC: ce:75:d7:3d:e2:91 with time diff: 0.021373 seconds
Linked Old MAC: c2:56:43:ad:49:77 -> New MAC: 72:89:ac:65:ef:a3 with time diff: 0.011577 seconds
Linked Old MAC: c6:f0:e3:58:65:ef -> New MAC: 16:9b:b9:e7:00:83 with time diff: 0.006655 seconds
Linked Old MAC: d6:97:ff:08:0c:a1 -> New MAC: 16:54:36:9f:54:c4 with time diff: 0.016943 seconds
Linked Old MAC: a2:9c:32:52:88:70 -> New MAC: ea:2e:9c:df:13:4f with time diff: 0.015911 seconds
Linked Old MAC: 12:63:20:18:15:ed -> New MAC: c2:a3:0a:73:88:f9 with time diff: 0.020322 seconds
Linked Old MAC: ea:c3:c8:07:31:9f -> New MAC: c6:4a:f4:c6:d7:60 with time diff: 0.019593 seconds
Linked Old MAC: 7a:6e:d5:40:0e:c0 -> New MAC: a6:01:1f:06:ae:a2 with time diff: 0.009992 seconds
Linked Old MAC: 42:f3:9a:79:d1:f2 -> New MAC: 42:1f:31:7c:a5:28 with time diff: 0.015903 seconds
Linked Old MAC: 62:32:10:3e:16:18 -> New MAC: 2e:65:61:f3:57:9d with time diff: 0.025393 seconds
Linked Old MAC: 62:56:e8:32:ad:27 -> New MAC: ca:98:61:95:06:47 with time diff: 0.025563 seconds
Linked Old MAC: ce:75:d7:3d:e2:91 -> New MAC: 0e:80:38:65:55:ca with time diff: 0.017025 seconds
Linked Old MAC: 72:89:ac:65:ef:a3 -> New MAC: 86:00:aa:8e:82:7e with time diff: 0.013359 seconds
Linked Old MAC: 16:9b:b9:e7:00:83 -> New MAC: 6a:ec:bd:20:82:0b with time diff: 0.010954 seconds
Linked Old MAC: 16:54:36:9f:54:c4 -> New MAC: 5a:2a:70:24:0f:3b with time diff: 0.011358 seconds
Linked Old MAC: ea:2e:9c:df:13:4f -> New MAC: e2:c4:98:bd:d7:69 with time diff: 0.018359 seconds
Linked Old MAC: c2:a3:0a:73:88:f9 -> New MAC: 42:10:02:81:54:f8 with time diff: 0.011548 seconds
Linked Old MAC: c6:4a:f4:c6:d7:60 -> New MAC: 26:7d:70:c2:18:a2 with time diff: 0.017140 seconds
Linked Old MAC: a6:01:1f:06:ae:a2 -> New MAC: 5e:7d:68:aa:3f:bb with time diff: 0.013607 seconds
Linked Old MAC: 42:1f:31:7c:a5:28 -> New MAC: 6a:77:71:1a:b6:49 with time diff: 0.020883 seconds
Linked Old MAC: 2e:65:61:f3:57:9d -> New MAC: 26:c3:7d:2e:74:7d with time diff: 0.025039 seconds
Linked Old MAC: ca:98:61:95:06:47 -> New MAC: c6:53:db:04:ff:ca with time diff: 0.024586 seconds
Linked Old MAC: 0e:80:38:65:55:ca -> New MAC: 2e:08:9e:b6:5a:3e with time diff: 0.023924 seconds
Linked Old MAC: 86:00:aa:8e:82:7e -> New MAC: 0e:82:67:65:bb:53 with time diff: 0.014533 seconds
Linked Old MAC: 6a:ec:bd:20:82:0b -> New MAC: 2a:55:e1:53:4a:cc with time diff: 0.006787 seconds
Linked Old MAC: 5a:2a:70:24:0f:3b -> New MAC: 0e:d4:b4:5d:80:52 with time diff: 0.019958 seconds
Linked Old MAC: e2:c4:98:bd:d7:69 -> New MAC: 66:77:7e:f7:77:39 with time diff: 0.024763 seconds
Linked Old MAC: 42:10:02:81:54:f8 -> New MAC: a6:82:5f:ed:9c:9f with time diff: 0.021078 seconds
Linked Old MAC: 26:7d:70:c2:18:a2 -> New MAC: 46:5e:fa:8e:74:f1 with time diff: 0.015303 seconds
Linked Old MAC: 5e:7d:68:aa:3f:bb -> New MAC: 96:d4:a6:ce:14:3f with time diff: 0.019465 seconds
Linked Old MAC: 6a:77:71:1a:b6:49 -> New MAC: b6:66:07:47:0c:56 with time diff: 0.024975 seconds
Linked Old MAC: 26:c3:7d:2e:74:7d -> New MAC: 32:2a:ce:c8:f9:5f with time diff: 0.021116 seconds
Linked Old MAC: c6:53:db:04:ff:ca -> New MAC: ae:1c:29:fd:be:4b with time diff: 0.021406 seconds
Linked Old MAC: 2e:08:9e:b6:5a:3e -> New MAC: 8a:4b:d4:db:d4:11 with time diff: 0.030964 seconds
Linked Old MAC: 0e:82:67:65:bb:53 -> New MAC: 56:22:45:a9:21:b6 with time diff: 0.016005 seconds
Linked Old MAC: 2a:55:e1:53:4a:cc -> New MAC: 06:d0:6c:50:37:3a with time diff: 0.003213 seconds
Linked Old MAC: 0e:d4:b4:5d:80:52 -> New MAC: 26:c0:3d:cf:bc:5d with time diff: 0.019395 seconds
Linked Old MAC: 66:77:7e:f7:77:39 -> New MAC: 86:cf:81:05:20:46 with time diff: 0.006962 seconds
Linked Old MAC: a6:82:5f:ed:9c:9f -> New MAC: ca:3f:59:f8:1d:6e with time diff: 0.012256 seconds
Linked Old MAC: 46:5e:fa:8e:74:f1 -> New MAC: 5a:9f:fb:2b:3f:1f with time diff: 0.019663 seconds
Linked Old MAC: 96:d4:a6:ce:14:3f -> New MAC: 76:e6:36:cd:65:94 with time diff: 0.020913 seconds
Linked Old MAC: b6:66:07:47:0c:56 -> New MAC: 3a:cb:4e:c0:7f:73 with time diff: 0.011016 seconds
Linked Old MAC: 32:2a:ce:c8:f9:5f -> New MAC: 2e:ef:1c:f2:2e:27 with time diff: 0.015145 seconds
Linked Old MAC: ae:1c:29:fd:be:4b -> New MAC: 02:f4:f8:7f:a8:bb with time diff: 0.019098 seconds
Linked Old MAC: 8a:4b:d4:db:d4:11 -> New MAC: 62:8b:8f:17:05:6f with time diff: 0.030502 seconds
Linked Old MAC: 56:22:45:a9:21:b6 -> New MAC: ba:2a:60:6a:68:b6 with time diff: 0.013672 seconds
Linked Old MAC: 06:d0:6c:50:37:3a -> New MAC: be:48:65:88:e4:0d with time diff: 0.008729 seconds
Linked Old MAC: 26:c0:3d:cf:bc:5d -> New MAC: 9a:dd:73:dd:e9:4f with time diff: 0.006105 seconds
Linked Old MAC: 86:cf:81:05:20:46 -> New MAC: e2:f1:e3:3f:4e:94 with time diff: 0.015356 seconds
Linked Old MAC: ca:3f:59:f8:1d:6e -> New MAC: ce:66:ec:91:ed:4e with time diff: 0.012143 seconds
Linked Old MAC: 5a:9f:fb:2b:3f:1f -> New MAC: 06:84:82:0d:fe:4b with time diff: 0.011876 seconds
Linked Old MAC: 76:e6:36:cd:65:94 -> New MAC: 36:8b:a2:90:95:34 with time diff: 0.028004 seconds
Linked Old MAC: 3a:cb:4e:c0:7f:73 -> New MAC: 92:da:9e:88:1b:97 with time diff: 0.017437 seconds
Linked Old MAC: 2e:ef:1c:f2:2e:27 -> New MAC: 92:10:2a:e8:18:e7 with time diff: 0.026413 seconds
Linked Old MAC: 02:f4:f8:7f:a8:bb -> New MAC: e2:1b:93:3a:b8:31 with time diff: 0.026135 seconds
Linked Old MAC: 62:8b:8f:17:05:6f -> New MAC: 1e:f4:0c:2d:a6:51 with time diff: 0.030668 seconds
"""



# Create a graph without edges
G = nx.Graph()

# Add nodes to the graph
for base_mac, random_macs in mac_sets.items():
    # Add the base MAC node
    G.add_node(base_mac)
    
    # Add the random MACs as nodes
    for random_mac in random_macs:
        G.add_node(random_mac)
        # For visualization purpose, position the random MAC nodes adjacent to the base MAC
        #G.add_edge(base_mac, random_mac)  # Adding an edge to keep nodes grouped, but it won't be shown


# Parse the linking log and add edges
pattern = re.compile(r"Linked Old MAC: ([0-9a-f:]+) -> New MAC: ([0-9a-f:]+)")
matches = pattern.findall(linking_log)
# Separate edges by color
green_edges = []
red_edges = []
for old_mac, new_mac in matches:
    G.add_edge(old_mac, new_mac)
    # Check if both old_mac and new_mac belong to the same base_mac in mac_sets
    same_set = False
    for base_mac, random_macs in mac_sets.items():
        if old_mac == base_mac or old_mac in random_macs:
            if new_mac == base_mac or new_mac in random_macs:
                same_set = True
                break
    if same_set:
        green_edges.append((old_mac, new_mac))
    else:
        red_edges.append((old_mac, new_mac))


#print no of green and red edges
print(f"Green edges: {len(green_edges)}")
print(f"Red edges: {len(red_edges)}")

# Assign colors to each base_mac and its random_macs
colors = list(mcolors.TABLEAU_COLORS.keys())
node_colors = {}
for i, (base_mac, random_macs) in enumerate(mac_sets.items()):
    color = colors[i % len(colors)]
    node_colors[base_mac] = color
    for random_mac in random_macs:
        node_colors[random_mac] = color


# Position nodes in rows for each base MAC and its random MACs
pos = {}
y = 0  # Initial y-position
x_spacing = 2  # Horizontal spacing between nodes
for base_mac, random_macs in mac_sets.items():
    # Position base MAC node
    pos[base_mac] = (0, y)
    # Position each random MAC node in a row to the right of the base MAC
    for i, random_mac in enumerate(random_macs, 1):
        pos[random_mac] = (i * x_spacing, y)
    y -= 1  # Move down for the next row

# Plot the graph without edges
plt.figure(figsize=(15, 10))
nx.draw_networkx_nodes(G, pos, node_size=1000, node_color=[node_colors[node] for node in G.nodes()], alpha=0.5)
#nx.draw_networkx_labels(G, pos, font_size=6)
#nx.draw_networkx_edges(G, pos, edge_color="red", arrows=True)
nx.draw_networkx_edges(G, pos, edgelist=green_edges, edge_color='green', arrows=True, width=5)
nx.draw_networkx_edges(G, pos, edgelist=red_edges, edge_color='red', arrows=True)

i=1
# Add station names to the left of the first node
for base_mac, random_macs in mac_sets.items():
    plt.text(pos[base_mac][0] - 0.5, pos[base_mac][1], f'STA{i}', horizontalalignment='right', verticalalignment='center', fontsize=10, color='black')
    i += 1


# Add re-randomization event numbers below each column
# Add re-randomization event numbers below each column for the last mac_sets
last_base_mac, last_random_macs = list(mac_sets.items())[-1]
for i, random_mac in enumerate([last_base_mac] + last_random_macs, 1):
    plt.text(pos[random_mac][0], pos[random_mac][1] - 0.4, f'Cycle {i}', horizontalalignment='center', verticalalignment='top', fontsize=10, color='black')

# Print the number of green and red edges on the graph
plt.text(0.95, 0.95, f"Correct links: {len(green_edges)}", horizontalalignment='left', verticalalignment='top', transform=plt.gca().transAxes, fontsize=12, color='green')
plt.text(0.95, 0.90, f"Incorrect links: {len(red_edges)}", horizontalalignment='left', verticalalignment='top', transform=plt.gca().transAxes, fontsize=12, color='red')
plt.text(0.95, 0.85, f"Accuracy: {((len(green_edges) / (len(green_edges) + len(red_edges))) * 100):.3f}%", horizontalalignment='left', verticalalignment='top', transform=plt.gca().transAxes, fontsize=12, color='green')
plt.title("MAC Address Re-randomization and Linking Accuracy Across Stations", fontsize=16)
plt.xlabel("Re-randomization Events")
plt.ylabel("Stations")
plt.axis("off")
plt.savefig("mac_transitions_graph.pdf", bbox_inches="tight", format="pdf")