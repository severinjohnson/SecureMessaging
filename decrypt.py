from Crypto.Util.number import getPrime, inverse

def decrypt(private_key, hex_ciphertext):
    # Convert the hex ciphertext to an integer
    ciphertext = int(hex_ciphertext, 16)

    d, n = private_key
    # Decrypting using pow, which performs modular exponentiation, a key RSA operation.
    decrypted_msg = pow(ciphertext, d, n)

    # Convert the decrypted integer back to bytes
    decrypted_bytes = decrypted_msg.to_bytes((decrypted_msg.bit_length() + 7) // 8, 'big')

    # Attempt to decode the bytes to UTF-8 text
    try:
        plaintext = decrypted_bytes.decode('utf-8')
        return plaintext
    except UnicodeDecodeError:
        # If decoding fails, return the raw bytes or a message indicating the issue.
        # This is useful if the original encrypted message was not text, but binary data.
        return "Decoding Error: Original data might not be text."

# Example usage
private_key = ()
encrypted_hex = ""

decrypted_message = decrypt(private_key, encrypted_hex)
print(decrypted_message)