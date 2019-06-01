# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/29
"""

from binascii import b2a_hex, a2b_hex

from Crypto.Cipher import AES

from conf import *


class AESCrypt(object):
    """
        en crypto (str and bytes) --> bytes,
        de crypto bytes --> bytes
    """

    def __init__(self, key, iv, mode=AES.MODE_CBC):
        self.key = key
        self.iv = iv
        self.mode = mode
        self.cipher = None

    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.iv)
        length = 16
        count = len(text)
        if (count % length) != 0:
            add = length - (count % length)
        else:
            add = 0
        text = text if isinstance(text, bytes) else text.encode()
        text = text + (b'\0' * add)
        self.cipher = cryptor.encrypt(text)
        return b2a_hex(self.cipher)

    # 解密后，去掉补足的空格
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.iv)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip(b'\0')


crypto = AESCrypt(PRIVATE_TOKEN, PRIVATE_TOKEN_IV)

if __name__ == '__main__':
    test_text = '1229979797989823666qwe'
    encrypt_text = crypto.encrypt(test_text)
    original_text = crypto.decrypt(encrypt_text)
    print(encrypt_text)
    print(original_text)
