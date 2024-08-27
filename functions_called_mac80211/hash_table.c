#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define ETH_ALEN 6
#define TABLE_SIZE 100

struct mac_translation_entry {
    unsigned char base_mac[ETH_ALEN];
    unsigned char random_mac[ETH_ALEN];
    struct mac_translation_entry *next;
};

struct mac_translation_entry *hash_table[TABLE_SIZE] = { NULL };

unsigned int hash_function(const unsigned char *mac) {
    unsigned int hash = 0;
    for (int i = 0; i < ETH_ALEN; i++) {
        hash += mac[i];
    }
    return hash % TABLE_SIZE;
}

void insert_entry(const unsigned char *base_mac, const unsigned char *random_mac) {
    unsigned int index = hash_function(random_mac);
    struct mac_translation_entry *new_entry = malloc(sizeof(struct mac_translation_entry));
    if (new_entry == NULL) {
        printf("Memory allocation failed.\n");
        return;
    }
    memcpy(new_entry->base_mac, base_mac, ETH_ALEN);
    memcpy(new_entry->random_mac, random_mac, ETH_ALEN);
    new_entry->next = hash_table[index];
    hash_table[index] = new_entry;
}

const unsigned char* reverse_search(const unsigned char *random_mac) {
    unsigned int index = hash_function(random_mac);
    struct mac_translation_entry *entry = hash_table[index];
    while (entry != NULL) {
        if (memcmp(entry->random_mac, random_mac, ETH_ALEN) == 0) {
            return entry->base_mac;
        }
        entry = entry->next;
    }
    return NULL;
}

const unsigned char* search_by_base_mac(const unsigned char *base_mac) {
    for (int i = 0; i < TABLE_SIZE; i++) {
        struct mac_translation_entry *entry = hash_table[i];
        while (entry != NULL) {
            if (memcmp(entry->base_mac, base_mac, ETH_ALEN) == 0) {
                return entry->random_mac;
            }
            entry = entry->next;
        }
    }
    return NULL;
}

int main() {
    // Insert some entries into the hash table
    unsigned char base_mac1[ETH_ALEN] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xab};
    unsigned char random_mac1[ETH_ALEN] = {0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff};
    unsigned char base_mac2[ETH_ALEN] = {0x11, 0x22, 0x33, 0x44, 0x55, 0x66};
    unsigned char random_mac2[ETH_ALEN] = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55};
    
    insert_entry(base_mac1, random_mac1);
    insert_entry(base_mac2, random_mac2);

    // Perform a reverse search
    const unsigned char *found_base_mac = reverse_search(random_mac1);
    if (found_base_mac != NULL) {
        printf("Base MAC Address for Random MAC Address 1: ");
        for (int i = 0; i < ETH_ALEN; i++) {
            printf("%02x", found_base_mac[i]);
            if (i < ETH_ALEN - 1) printf(":");
        }
        printf("\n");
    } else {
        printf("Base MAC Address for Random MAC Address 1 not found.\n");
    }

    // Search for a random MAC address based on a given base MAC address
    const unsigned char *found_random_mac = search_by_base_mac(base_mac2);
    if (found_random_mac != NULL) {
        printf("Random MAC Address for Base MAC Address 2: ");
        for (int i = 0; i < ETH_ALEN; i++) {
            printf("%02x", found_random_mac[i]);
            if (i < ETH_ALEN - 1) printf(":");
        }
        printf("\n");
    } else {
        printf("Random MAC Address for Base MAC Address 2 not found.\n");
    }

    return 0;
}

