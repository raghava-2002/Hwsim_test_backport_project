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

// Use a global sequence number variable
static uint32_t seq_num = 0;

// Function to log messages to /home/rathan/Downloads/hwsim_test/final_test.log
static void log_to_file(const char *message) {
    int fd = open("/home/rathan/Downloads/hwsim_test/final_test.log", O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (fd < 0) {
        perror("Error opening final_test.log");
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
    log_to_file(log_message);  // Log the raw data

    // Extract the base MAC address from the received message
    memcpy(response->s_base_mac, raw_data, ETH_ALEN);

    // Log the received MAC for debugging
    snprintf(log_message, sizeof(log_message),
             "Extracted base MAC from kernel: %02x:%02x:%02x:%02x:%02x:%02x\n",
             response->s_base_mac[0], response->s_base_mac[1], response->s_base_mac[2],
             response->s_base_mac[3], response->s_base_mac[4], response->s_base_mac[5]);
    log_to_file(log_message);

    // Log the sequence number in the response
    snprintf(log_message, sizeof(log_message),
             "Received message with seq_num: %u\n", nlh->nlmsg_seq);
    log_to_file(log_message);

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

    log_to_file("Inside Starting MAC search in kernel\n");
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
    snprintf(mac_log_message, sizeof(mac_log_message),
             "Sending random MAC to kernel: %02x:%02x:%02x:%02x:%02x:%02x\n",
             random_mac[0], random_mac[1], random_mac[2],
             random_mac[3], random_mac[4], random_mac[5]);
    log_to_file(mac_log_message);

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
    snprintf(mac_log_message, sizeof(mac_log_message), "Netlink message sent to kernel with seq_num: %u\n", seq_num);
    log_to_file(mac_log_message);

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
        log_to_file("Netlink message sent to kernel successfully\n");
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
        log_to_file("Received response from Netlink successfully\n");
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

