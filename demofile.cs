using System;
using System.Text;
using System.Security.Cryptography;

namespace SteganoTest
{
    /// <summary>
    /// Example C# class for steganography testing
    /// This file demonstrates hiding C# source code in images
    /// </summary>
    public class CryptoHelper
    {
        private const int KeySize = 256;
        private const int Iterations = 10000;

        /// <summary>
        /// Encrypts a string using AES encryption
        /// </summary>
        public static string Encrypt(string plainText, string password)
        {
            if (string.IsNullOrEmpty(plainText))
                throw new ArgumentNullException(nameof(plainText));
            
            if (string.IsNullOrEmpty(password))
                throw new ArgumentNullException(nameof(password));

            byte[] salt = GenerateSalt();
            byte[] encrypted;

            using (Aes aes = Aes.Create())
            {
                var key = new Rfc2898DeriveBytes(password, salt, Iterations);
                aes.Key = key.GetBytes(KeySize / 8);
                aes.IV = key.GetBytes(aes.BlockSize / 8);
                aes.Mode = CipherMode.CBC;

                using (var encryptor = aes.CreateEncryptor(aes.Key, aes.IV))
                using (var msEncrypt = new System.IO.MemoryStream())
                {
                    using (var csEncrypt = new CryptoStream(msEncrypt, encryptor, CryptoStreamMode.Write))
                    using (var swEncrypt = new System.IO.StreamWriter(csEncrypt))
                    {
                        swEncrypt.Write(plainText);
                    }
                    encrypted = msEncrypt.ToArray();
                }
            }

            // Combine salt and encrypted data
            byte[] result = new byte[salt.Length + encrypted.Length];
            Buffer.BlockCopy(salt, 0, result, 0, salt.Length);
            Buffer.BlockCopy(encrypted, 0, result, salt.Length, encrypted.Length);

            return Convert.ToBase64String(result);
        }

        /// <summary>
        /// Decrypts an AES-encrypted string
        /// </summary>
        public static string Decrypt(string cipherText, string password)
        {
            if (string.IsNullOrEmpty(cipherText))
                throw new ArgumentNullException(nameof(cipherText));

            if (string.IsNullOrEmpty(password))
                throw new ArgumentNullException(nameof(password));

            byte[] fullCipher = Convert.FromBase64String(cipherText);
            
            // Extract salt
            byte[] salt = new byte[32];
            Buffer.BlockCopy(fullCipher, 0, salt, 0, salt.Length);

            // Extract encrypted data
            byte[] encrypted = new byte[fullCipher.Length - salt.Length];
            Buffer.BlockCopy(fullCipher, salt.Length, encrypted, 0, encrypted.Length);

            string plaintext;

            using (Aes aes = Aes.Create())
            {
                var key = new Rfc2898DeriveBytes(password, salt, Iterations);
                aes.Key = key.GetBytes(KeySize / 8);
                aes.IV = key.GetBytes(aes.BlockSize / 8);
                aes.Mode = CipherMode.CBC;

                using (var decryptor = aes.CreateDecryptor(aes.Key, aes.IV))
                using (var msDecrypt = new System.IO.MemoryStream(encrypted))
                using (var csDecrypt = new CryptoStream(msDecrypt, decryptor, CryptoStreamMode.Read))
                using (var srDecrypt = new System.IO.StreamReader(csDecrypt))
                {
                    plaintext = srDecrypt.ReadToEnd();
                }
            }

            return plaintext;
        }

        private static byte[] GenerateSalt()
        {
            byte[] salt = new byte[32];
            using (var rng = new RNGCryptoServiceProvider())
            {
                rng.GetBytes(salt);
            }
            return salt;
        }

        // Example usage
        public static void Main(string[] args)
        {
            Console.WriteLine("=================================");
            Console.WriteLine("    AES Encryption Demo");
            Console.WriteLine("=================================\n");

            if (args.Length < 2)
            {
                Console.WriteLine("Usage: CryptoHelper <text> <password>");
                Console.WriteLine("Example: CryptoHelper \"Secret Message\" MyPass123");
                return;
            }

            string originalText = args[0];
            string password = args[1];

            Console.WriteLine($"Original: {originalText}");
            
            string encrypted = Encrypt(originalText, password);
            Console.WriteLine($"\nEncrypted: {encrypted}");

            string decrypted = Decrypt(encrypted, password);
            Console.WriteLine($"\nDecrypted: {decrypted}");
        }
    }
}
