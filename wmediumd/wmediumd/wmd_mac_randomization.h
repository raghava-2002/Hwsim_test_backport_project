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

// Structure to store MAC pairsßßßßß
struct mac_table {
    unsigned char base_mac[ETH_ALEN]; //the original MAC address of the station got from the kernel
    unsigned char random_mac[ETH_ALEN]; //the current random MAC address of the station
    unsigned char old_rnd_mac[ETH_ALEN]; //the old random MAC address of the station (from the previous time period)
    struct mac_table *next;
};

//functions to handle table operations
void log_to_file(const char *message);
void insert_entry(const unsigned char *base_mac, const unsigned char *random_mac);
void update_entry_by_random(const unsigned char *random_mac, const unsigned char *new_base_mac);
void update_entry_by_base(const unsigned char *base_mac, const unsigned char *new_random_mac);
struct mac_table *search_by_random_mac(const unsigned char *random_mac);
struct mac_table *search_by_base_mac(const unsigned char *base_mac);
void cleanup_translation_table(void);
void log_mac_translation_table(void);
void mac_to_string(const unsigned char *mac, char *buffer, size_t buffer_size);

struct mac_pair *kernel_search_mac_pair(u8 *random_mac);
int netlink_response_handler(struct nl_msg *msg, void *arg);

#endif // MAC_RANDOMIZATION_H