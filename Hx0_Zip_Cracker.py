import os
import sys
import time
import zipfile
import string
import itertools as its
from concurrent.futures import ThreadPoolExecutor

def is_zip_encrypted(file_path):
    with zipfile.ZipFile(file_path) as zf:
        return any(info.flag_bits & 0x1 for info in zf.infolist())

def fix_zip_encrypted(file_path):
    with zipfile.ZipFile(file_path) as zf, zipfile.ZipFile(file_path + ".tmp", "w") as temp_zf:
        for info in zf.infolist():
            if info.flag_bits & 0x1:
                info.flag_bits ^= 0x1
            temp_zf.writestr(info, zf.read(info.filename))
    return file_path + ".tmp"

def crack_password(password, zip_file):
    try:
        with zipfile.ZipFile(zip_file) as zf:
            zf.setpassword(password.encode())
            zf.extractall()
            print(f'[*]恭喜您！密码破解成功,该压缩包的密码为：{password}')
            os._exit(0)
            return True
    except Exception as e:
        print(f'\r[-]尝试密码: {password}', end="", flush=True)
    return False

def generate_passwords(dict_file='password_list.txt'):
    try:
        with open(dict_file, 'r') as f:
            yield from (line.strip() for line in f)
    except Exception as e:
        print(f'[!]加载字典失败！，原因：{e}')
        os._exit(0)

    for length in range(1, 7):
        yield from (f'{i:0{length}d}' for i in range(10 ** length))

if __name__ == '__main__':
    print("cyx14998")
    if len(sys.argv) == 1:
        print("[*]用法1(内置字典): Python3 Hx0_Zip_Cracker.py YourZipFile.zip \n[*]用法2(自定义字典): Python3 Hx0_Zip_Cracker.py YourZipFile.zip YourDict.txt 50")
        os._exit(0)

    zip_file = sys.argv[1]
    if is_zip_encrypted(zip_file):
        print(f'[!]系统检测到 {zip_file} 是一个加密的ZIP文件')
        try:
            fix_zip_name = fix_zip_encrypted(zip_file)
            print(f"[*]压缩包 {zip_file} 为伪加密，已修复为 {fix_zip_name}，正在尝试解压...")
            zip_file = fix_zip_name
        except Exception as e:
            print(f'[+]压缩包 {zip_file} 不是伪加密，准备尝试暴力破解')

    password_file = sys.argv[2] if len(sys.argv) > 2 else 'password_list.txt'
    max_workers = int(sys.argv[3]) if len(sys.argv) > 3 else 50

    password_generator = generate_passwords(password_file)
    pool = ThreadPoolExecutor(max_workers=max_workers)

    for password in password_generator:
        if crack_password(password, zip_file):
            os._exit(0)
            break
