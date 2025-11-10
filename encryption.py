# encryption.py
# --------------------------------------------------------
# Simple XOR-based encryption/decryption with a fixed key
# --------------------------------------------------------
# You can change this fixed key (0–255) if you like
FIXED_KEY = 23

def encrypt_message(message: str) -> str:
    
    """ Encrypt a plain text message using XOR with FIXED_KEY.
    Returns a hex string representation of the encrypted data. """
    
    encrypted_chars = [format(ord(ch) ^ FIXED_KEY, '02x') for ch in message]
    return ''.join(encrypted_chars)

def decrypt_message(cipher_text: str) -> str:
    """Decrypt a hex string that was encrypted using encrypt_message().
    Returns the original plain text message."""

    chars = [
        chr(int(cipher_text[i:i+2], 16) ^ FIXED_KEY)
        for i in range(0, len(cipher_text), 2)
    ]
    return ''.join(chars)

"""
#--------------------------------------------------------
# Optional: test when running this file directly
# --------------------------------------------------------
if __name__ == "__main__":
    sample = "Hello World!"
    enc = encrypt_message(sample)
    dec = decrypt_message(enc)
    print("Original:", sample)
    print("Encrypted:", enc)
    print("Decrypted:", dec)
"""