Weaponized encryption utility written in python 3.
Rewritten with pycryptodome instead of the vulnerable pycrypto library.
This file WILL harm your PC. Don't use it unless you know what you're doing.
DO NOT use this file for anything illegal!


Setup:

         git clone https://github.com/pyCity/Excalibur && cd Excalibur
         pip3 install -r requirements.txt || chmod +x setup.sh && ./setup.sh
         python3 setup.py install
         
Usage:
   
         python3 Excalibur.py -h         


This program functions well as is, but is best to compile using pyinstaller before delivery

        pyinstaller --onefile Excalibur.py
       
If you pyinstaller raises an ImportError, double check that you 
have installed requirements.txt and try:

pip3 install --upgrade pyinstaller
