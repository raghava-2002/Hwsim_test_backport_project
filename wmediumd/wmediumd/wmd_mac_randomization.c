#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/klog.h>
#include <libnl3/netlink/genl/genl.h>
#include <libnl3/netlink/genl/ctrl.h>
#include <fcntl.h>   // For open flags
#include <unistd.h>  // For write and close
#include "wmd_mac_randomization.h"
#include "wmediumd.h"
#define NETLINK_USER 30  // This must match the protocol number in the kernel

#define TABLE_SIZE 50  // Size of the table to store MAC pairs

// Use a global sequence number variable
static uint32_t seq_num = 0;

// Function to log messages to /home/rathan/Downloads/hwsim_test/final_test.log
void log_to_file(const char *message) {
    int fd = open("/home/rathan/thesis/hwsim_test/wmediumd/rathan_wmd_rnd.log", O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (fd < 0) {
        perror("Error opening rathan_wmd_rnd.log");
        return;
    }
    write(fd, message, strlen(message));
    close(fd);
}

// Callback function to handle the response from the Netlink socket
int netlink_response_handler(struct nl_msg *msg, void *arg) {
    struct nlmsghdr *nlh = nlmsg_hdr(msg);
    struct mac_pair *response = (struct mac_pair *)arg;
    char log_message[512];  // Larger buffer for debugging
    int data_len = nlh->nlmsg_len;  // Length of the Netlink message

    // Log the raw data received for debugging
    unsigned char *raw_data = nlmsg_data(nlh);
    int i;
    char *pos = log_message;

    pos += snprintf(pos, sizeof(log_message), "Received raw data from kernel (seq_num: %u): ", nlh->nlmsg_seq);
    for (i = 0; i < data_len; i++) {
        pos += snprintf(pos, sizeof(log_message) - (pos - log_message), "%02x ", raw_data[i]);
    }
    //log_to_file(log_message);  // Log the raw data

    // Extract the base MAC address from the received message
    memcpy(response->s_base_mac, raw_data, ETH_ALEN);

    /* // Log the received MAC for debugging
    snprintf(log_message, sizeof(log_message),
             "Extracted base MAC from kernel: %02x:%02x:%02x:%02x:%02x:%02x\n",
             response->s_base_mac[0], response->s_base_mac[1], response->s_base_mac[2],
             response->s_base_mac[3], response->s_base_mac[4], response->s_base_mac[5]);
    log_to_file(log_message);

    // Log the sequence number in the response
    snprintf(log_message, sizeof(log_message),
             "Received message with seq_num: %u\n", nlh->nlmsg_seq);
    log_to_file(log_message); */

    return NL_OK;
}

// Enhanced kernel_search_mac_pair with manual message reception
struct mac_pair *kernel_search_mac_pair(u8 *random_mac) {
    struct nl_sock *sock = NULL;
    struct nl_msg *msg = NULL;
    struct mac_pair *response = malloc(sizeof(struct mac_pair));  // Allocate memory for response
    char mac_log_message[256];  // Buffer for logging
    int ret;
    struct nl_cb *cb;

    //log_to_file("Inside Starting MAC search in kernel\n");
    if (!response) {
        log_to_file("Error allocating memory for MAC response\n");
        return NULL;
    }

    // Step 1: Create a Netlink socket
    sock = nl_socket_alloc();
    if (!sock) {
        log_to_file("Error allocating Netlink socket\n");
        free(response);
        return NULL;
    }

    // Step 2: Connect the Netlink socket
    ret = nl_connect(sock, NETLINK_USER);  // NETLINK_USER is the same identifier used in the kernel
    if (ret < 0) {
        log_to_file("Error connecting to Netlink\n");
        nl_socket_free(sock);
        free(response);
        return NULL;
    }

    // Step 3: Log the random MAC address before sending
    /* snprintf(mac_log_message, sizeof(mac_log_message),
             "Sending random MAC to kernel: %02x:%02x:%02x:%02x:%02x:%02x\n",
             random_mac[0], random_mac[1], random_mac[2],
             random_mac[3], random_mac[4], random_mac[5]);
    log_to_file(mac_log_message); */

    // Step 4: Create a Netlink message to the kernel
    msg = nlmsg_alloc();
    if (!msg) {
        log_to_file("Error allocating Netlink message\n");
        nl_socket_free(sock);
        free(response);
        return NULL;
    }

    // Step 5: Fill the message with the random MAC address
    genlmsg_put(msg, NL_AUTO_PORT, ++seq_num, 0, 0, 0, NETLINK_USER, 1);

    // Log the sequence number
    //snprintf(mac_log_message, sizeof(mac_log_message), "Netlink message sent to kernel with seq_num: %u\n", seq_num);
    //log_to_file(mac_log_message);

    ret = nla_put(msg, 1, ETH_ALEN, random_mac);  // Assuming attribute 1 is the MAC address
    if (ret < 0) {
        log_to_file("Error adding MAC attribute to Netlink message\n");
        nlmsg_free(msg);
        nl_socket_free(sock);
        free(response);
        return NULL;
    }

    // Step 6: Send the message to the kernel
    ret = nl_send_auto(sock, msg);
    if (ret < 0) {
        log_to_file("Error sending Netlink message to kernel\n");
        nlmsg_free(msg);
        nl_socket_free(sock);
        free(response);
        return NULL;
    } else {
        //log_to_file("Netlink message sent to kernel successfully\n");
    }

    // Step 7: Set up callback
    cb = nl_cb_alloc(NL_CB_DEFAULT);
    if (!cb) {
        log_to_file("Error allocating callback\n");
        nlmsg_free(msg);
        nl_socket_free(sock);
        free(response);
        return NULL;
    }

    // Set the callback for valid messages
    nl_cb_set(cb, NL_CB_SEQ_CHECK, NL_CB_CUSTOM, netlink_response_handler, response);

    // Step 8: Manually receive and process the response from the kernel
    ret = nl_recvmsgs(sock, cb);  // Manually receiving messages
    if (ret < 0) {
        snprintf(mac_log_message, sizeof(mac_log_message),
                 "Error receiving response from Netlink: %s, seq_num: %u\n", nl_geterror(ret), seq_num);
        log_to_file(mac_log_message);
        nlmsg_free(msg);
        nl_socket_free(sock);
        nl_cb_put(cb);
        free(response);
        return NULL;
    } else {
        //log_to_file("Received response from Netlink successfully\n");
    }

    // Check if the callback was triggered by checking if we have valid data
    if (memcmp(response->s_base_mac, random_mac, ETH_ALEN) == 0) {
        log_to_file("Received the same MAC address as sent, returning NULL\n");
        free(response);
        response = NULL;
    }

    // Clean up
    nlmsg_free(msg);
    nl_cb_put(cb);
    nl_socket_free(sock);

    return response;
}


//wmediumd table handling functions and structures

struct mac_table *translation_table[TABLE_SIZE] = { NULL }; // Global translation hash table

// Hash function that combines the bytes of a MAC address
unsigned int hash_function(const unsigned char *mac) {
    unsigned int hash = 0;
	int i;
    for (i = 0; i < ETH_ALEN; i++) {
        hash = (hash << 5) + mac[i]; // Rotate hash and add next byte
    }
    return hash % TABLE_SIZE; // Modulo to fit within table size
}

// Function to insert a new entry into the hash table
void insert_entry(const unsigned char *base_mac, const unsigned char *random_mac) {
    unsigned int index = hash_function(random_mac);
    struct mac_table *new_entry = malloc(sizeof(struct mac_table));
    if (new_entry == NULL) {
        // Handle memory allocation failure
        log_to_file("new creation in the table failure\n");
        return;
    }
    //log_to_file("new entry created\n");
    memcpy(new_entry->base_mac, base_mac, ETH_ALEN);
    memcpy(new_entry->random_mac, random_mac, ETH_ALEN);
    memcpy(new_entry->old_rnd_mac, random_mac, ETH_ALEN); // Initially set old MAC to current MAC
    new_entry->next = translation_table[index];
    translation_table[index] = new_entry;
}

void update_entry_by_base(const unsigned char *base_mac, const unsigned char *new_random_mac) {
    struct mac_table *entry = search_by_base_mac(base_mac);
    if (entry != NULL) {
        // Entry with the specified base MAC address found, update its random MAC address
        //log_to_file("entry found and updated\n");
        memcpy(entry->old_rnd_mac, entry->random_mac, ETH_ALEN); // Save the old random MAC
        memcpy(entry->random_mac, new_random_mac, ETH_ALEN);
    } else {
        //printk(KERN_DEBUG "Rathan: MAT b Entry with base MAC address not found.\n");
        //if their is no entry with the base mac address then insert the new entry
        //log_to_file("entry not found cannot update the table need new entry\n");
        insert_entry(base_mac, new_random_mac);
        //printk(KERN_DEBUG "Rathan: MAT b Entry with base MAC address not found. Inserted new entry.\n");
    }
}

//this function is not needed or not using in the logic
void update_entry_by_random(const unsigned char *random_mac, const unsigned char *new_base_mac) {
    struct mac_table *entry = search_by_random_mac(random_mac);
    if (entry != NULL) {
        // Entry with the specified random MAC address found, update its base MAC address
        memcpy(entry->base_mac, new_base_mac, ETH_ALEN);
    } else {
        //printk(KERN_DEBUG "Rathan: MAT r Entry with random MAC address not found.\n");
        //log_to_file("entry not found cannot update the table\n");
    }
}

// Function to perform a reverse search to find the base MAC address associated with a randomized MAC address returns entry
struct mac_table *search_by_random_mac(const unsigned char *random_mac) {
    // Iterate over all entries in the translation table
	unsigned int index;
    for (index = 0; index < TABLE_SIZE; ++index) {
        struct mac_table *entry = translation_table[index];
        while (entry != NULL) {
            if (memcmp(entry->random_mac, random_mac, ETH_ALEN) == 0) {
                //log_to_file("entry found and returned\n");
                //log_mac_translation_table();
                return entry;
            }
            entry = entry->next;
        }
    }

    for (index = 0; index < TABLE_SIZE; ++index) {
        struct mac_table *entry = translation_table[index];
        while (entry != NULL) {
            if (memcmp(entry->old_rnd_mac, random_mac, ETH_ALEN) == 0) {
                //log_to_file("entry found and returned\n");
                //log_mac_translation_table();
                return entry;
            }
            entry = entry->next;
        }
    }

    // Entry with the specified base MAC address not found
    //log_to_file("entry not found ask kernel\n");
    return NULL;
}

// Function to search for a randomized MAC address with base MAC address returns the entry
struct mac_table *search_by_base_mac(const unsigned char *base_mac) {
    // Iterate over all entries in the translation table
	unsigned int index;
    for (index = 0; index < TABLE_SIZE; ++index) {
        struct mac_table *entry = translation_table[index];
        while (entry != NULL) {
            if (memcmp(entry->base_mac, base_mac, ETH_ALEN) == 0) {
                // Found the entry with the specified base MAC address
                //printk(KERN_DEBUG "Rathan: Found the entry with the specified base MAC address %pM\n", base_mac);
                return entry;
            }
            entry = entry->next;
        }
    }
    //printk(KERN_DEBUG "search by base MAC address not found.\n");
    // Entry with the specified base MAC address not found
    return NULL;
}

// Cleanup function
void cleanup_translation_table(void) {
    for (int i = 0; i < TABLE_SIZE; ++i) {
        struct mac_table *entry = translation_table[i];
        while (entry != NULL) {
            struct mac_table *temp = entry;
            entry = entry->next;
            free(temp);
        }
        translation_table[i] = NULL;
    }
}



//debugging function to print the table

// Function to convert a MAC address to a readable string
void mac_to_string(const unsigned char *mac, char *buffer, size_t buffer_size) {
    snprintf(buffer, buffer_size, "%02x:%02x:%02x:%02x:%02x:%02x",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

// Function to log the MAC translation table
void log_mac_translation_table() {
    char log_entry[128]; // Adjust size if needed
    char random_mac_str[18], base_mac_str[18], old_mac_str[18];
    
    for (int i = 0; i < TABLE_SIZE; i++) {
        struct mac_table *entry = translation_table[i];
        while (entry != NULL) {
            mac_to_string(entry->random_mac, random_mac_str, sizeof(random_mac_str));
            mac_to_string(entry->base_mac, base_mac_str, sizeof(base_mac_str));
            mac_to_string(entry->old_rnd_mac, old_mac_str, sizeof(old_mac_str));
            
            // Format the entry into a log message
            snprintf(log_entry, sizeof(log_entry), "Random MAC: %s -> Base MAC: %s -> Old rnd MAC: %s\n", random_mac_str, base_mac_str, old_mac_str);
            
            // Log the entry to file
            log_to_file(log_entry);
            
            // Move to the next entry in the list
            entry = entry->next;
        }
    }
}
