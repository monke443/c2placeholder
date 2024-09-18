from crypto_gen import *

confirm_private_file_hash = "confirm.txt"
original_file = "private_key.pem"
public_key = "public_key.pem"
Hello = "hello"

if __name__ == '__main__':
    public_key = load_public_key("public_key.pem")
    private_key = load_private_key("private_key.pem")

    print(f"Message before encryption -> {Hello}\n")
    encrypted_message= rsa_encrypt(Hello, public_key)

    print(f"Encrypted message ->  {encrypted_message}\n")

    decrypted_message = rsa_decrypt(encrypted_message, private_key)

    print (f"Decrypted messaage -> {decrypted_message}\n")



    