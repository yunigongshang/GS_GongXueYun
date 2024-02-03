
from decry.utils import AES,UTC as pytz

key = '23DbtQHR2UMbH6mJ'

def aes_encrypt(text):
    aes = AES(key.encode("utf-8"))
    res = aes.encrypt(str(text).encode('utf-8'))
    msg = res.hex()
    return msg

if __name__ == '__main__':
    print(aes_encrypt('11111'))
