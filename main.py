import os
import time
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import tkinter as tk
from tkinter import filedialog, messagebox

PASSWORD = "mebcA1-puzvaz-jewnyn"
MAGIC_HEADER = b"FILESEC"
LOG_FILE = "encryption_log.txt"
BLOCK_SIZE = 16

def pad(data):
    pad_len = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + bytes([pad_len]) * pad_len

def unpad(data):
    pad_len = data[-1]
    return data[:-pad_len]

def derive_key(password, salt):
    return PBKDF2(password, salt, dkLen=32, count=500000)

def aes_encrypt(data: bytes) -> bytes:
    salt = get_random_bytes(16)
    iv = get_random_bytes(BLOCK_SIZE)
    key = derive_key(PASSWORD, salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(MAGIC_HEADER + data))
    return salt + iv + encrypted

def aes_decrypt(data: bytes) -> bytes:
    if len(data) < 32:
        return None
    salt = data[:16]
    iv = data[16:32]
    ciphertext = data[32:]
    key = derive_key(PASSWORD, salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    try:
        decrypted = cipher.decrypt(ciphertext)
        if not decrypted.startswith(MAGIC_HEADER):
            return None
        return unpad(decrypted[len(MAGIC_HEADER):])
    except Exception:
        return None

def process_file(path: str, encrypt: bool, overwrite: bool):
    try:
        with open(path, "rb") as f:
            data = f.read()
        result = aes_encrypt(data) if encrypt else aes_decrypt(data)
        if result is None:
            messagebox.showerror("복호화 실패", f"잘못된 키 또는 파일 손상: {os.path.basename(path)}")
            return False

        out_path = (
            path if overwrite else path + ".enc" if encrypt
            else path[:-4] if path.endswith(".enc") else path + ".dec"
        )
        with open(out_path, "wb") as f:
            f.write(result)

        log_action("Encrypted" if encrypt else "Decrypted", out_path)
        return True
    except Exception as e:
        messagebox.showerror("오류", f"{e}")
        return False

def process_directory(folder: str, encrypt: bool, overwrite: bool):
    for root, dirs, files in os.walk(folder):
        for name in files:
            fp = os.path.join(root, name)
            if encrypt and not name.endswith(".enc"):
                process_file(fp, True, overwrite)
            elif not encrypt and name.endswith(".enc"):
                process_file(fp, False, overwrite)

def log_action(action: str, path: str):
    with open(LOG_FILE, "a", encoding="utf-8") as lf:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        lf.write(f"{ts} - {action}: {path}\n")

def select_path():
    p = filedialog.askopenfilename() if var_mode.get() == "file" else filedialog.askdirectory()
    entry_path.delete(0, tk.END)
    entry_path.insert(0, p)

def start():
    path = entry_path.get().strip()
    encrypt = (var_enc.get() == "encrypt")
    overwrite = var_ovr.get()

    if not path:
        messagebox.showwarning("입력 부족", "경로를 입력하세요.")
        return

    if os.path.isdir(path):
        process_directory(path, encrypt, overwrite)
        messagebox.showinfo("완료", "디렉터리 작업 완료")
    else:
        ok = process_file(path, encrypt, overwrite)
        if ok:
            messagebox.showinfo("완료", "파일 처리 완료")

root = tk.Tk()
root.title("파괴형 AES 파일 암호화")
root.configure(bg="black")
root.geometry("480x320")

tk.Label(root, text="파일/폴더 경로:", bg="black", fg="white").pack(pady=(10,0))
entry_path = tk.Entry(root, width=60); entry_path.pack(padx=10)
tk.Button(root, text="찾아보기", command=select_path, bg="gray", fg="white").pack(pady=5)

tk.Label(root, text="(※ 비밀번호는 고정되어 있음)", bg="black", fg="gray").pack()

var_mode = tk.StringVar(value="file")
frm1 = tk.Frame(root, bg="black")
tk.Radiobutton(frm1, text="파일", variable=var_mode, value="file", bg="black", fg="white").pack(side="left", padx=5)
tk.Radiobutton(frm1, text="폴더", variable=var_mode, value="folder", bg="black", fg="white").pack(side="left", padx=5)
frm1.pack(pady=5)

var_enc = tk.StringVar(value="encrypt")
frm2 = tk.Frame(root, bg="black")
tk.Radiobutton(frm2, text="암호화", variable=var_enc, value="encrypt", bg="black", fg="white").pack(side="left", padx=5)
tk.Radiobutton(frm2, text="복호화", variable=var_enc, value="decrypt", bg="black", fg="white").pack(side="left", padx=5)
frm2.pack(pady=5)

var_ovr = tk.BooleanVar()
tk.Checkbutton(root, text="원본 덮어쓰기", variable=var_ovr, bg="black", fg="white").pack(pady=5)
tk.Button(root, text="실행", command=start, bg="gray", fg="white").pack(pady=15)

root.mainloop()
