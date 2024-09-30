#ifndef MAC_RANDOMIZATION_H
#define MAC_RANDOMIZATION_H

#include <netlink/netlink.h>
#include <netlink/msg.h>
#include <netlink/socket.h>
#include <stdint.h>
#include <stdbool.h>
#include <syslog.h>
#include <stdio.h>
#include <string.h>

#define ETH_ALEN 6
typedef uint8_t u8;
struct mac_pair {
    u8 s_base_mac[ETH_ALEN];
    // Add other fields if needed
};

struct mac_pair *kernel_search_mac_pair(u8 *random_mac);
int netlink_response_handler(struct nl_msg *msg, void *arg);

#endif // MAC_RANDOMIZATION_H