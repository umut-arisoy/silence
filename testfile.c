/*
 * Example C Program - For Steganography Testing
 * This file can be hidden inside PNG/BMP images
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_BUFFER 256

// Function to reverse a string
void reverseString(char* str) {
    int length = strlen(str);
    int i;
    
    for (i = 0; i < length / 2; i++) {
        char temp = str[i];
        str[i] = str[length - 1 - i];
        str[length - 1 - i] = temp;
    }
}

// Function to encrypt with XOR
void xorEncrypt(char* data, char key) {
    int i;
    for (i = 0; data[i] != '\0'; i++) {
        data[i] = data[i] ^ key;
    }
}

int main(int argc, char* argv[]) {
    char message[MAX_BUFFER];
    char key;
    
    printf("=================================\n");
    printf("  Simple XOR Encryption Tool\n");
    printf("=================================\n\n");
    
    if (argc < 3) {
        printf("Usage: %s <message> <key>\n", argv[0]);
        printf("Example: %s \"Hello World\" A\n", argv[0]);
        return 1;
    }
    
    strncpy(message, argv[1], MAX_BUFFER - 1);
    message[MAX_BUFFER - 1] = '\0';
    key = argv[2][0];
    
    printf("Original message: %s\n", message);
    printf("Encryption key: %c\n\n", key);
    
    // Encrypt
    xorEncrypt(message, key);
    printf("Encrypted: %s\n", message);
    
    // Decrypt (XOR again)
    xorEncrypt(message, key);
    printf("Decrypted: %s\n", message);
    
    return 0;
}
