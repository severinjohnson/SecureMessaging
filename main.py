from Crypto.Util.number import getPrime, inverse

def generate_keypair(keysize):
    p = getPrime(keysize // 2)
    q = getPrime(keysize // 2)
    n = p * q

    phi = (p-1) * (q-1)  # Euler's totient function for n because p and q are co-prime

    e = 65537  # Common e value

    # Finding mod inverse of e
    d = inverse(e, phi)

    return ((e, n), (d, n))

def encrypt(public_key, plaintext):
    e, n = public_key

    # Converting a text message into numbers using UTF-8
    message_int = int.from_bytes(plaintext.encode('utf-8'), 'big')

    encrypted_msg = pow(message_int, e, n)
    return encrypted_msg

def decrypt(private_key, ciphertext):
    d, n = private_key
    # Decrypting using pow, The pow function here is used to perform modular exponentiation, which is a key operation in RSA decryption.
    decrypted_msg = pow(ciphertext, d, n)

    plaintext = decrypted_msg.to_bytes((decrypted_msg.bit_length() + 7) // 8, 'big').decode('utf-8')

    return plaintext

