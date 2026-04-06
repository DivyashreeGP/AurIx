import subprocess
import requests
import yaml
import xml.etree.ElementTree as ET
import lxml.etree
import httpx
import pickle
import marshal
import ssl
import tarfile
import zipfile
import random
from flask import Flask, request, make_response

app = Flask(__name__)

# -------- 1. subprocess shell=True (should trigger SUBPROC-SHELL-001) --------
subprocess.run("ls -la", shell=True)

# -------- 2. subprocess with concat (should trigger SUBPROC-CMD-CONCAT-001) --------
cmd = "ping " + request.args.get("host", "")
subprocess.Popen(cmd)

# -------- 3. Insecure pickle deserialization (PICKLE-LOADS-001) --------
data = pickle.loads(request.args.get("data", "").encode())

# -------- 4. Marshal loads (MARSHAL-LOADS-001) --------
x = marshal.loads(request.args.get("blob", "").encode())

# -------- 5. Unsafe YAML load without SafeLoader (YAML-LOAD-001) --------
content = request.args.get("yaml", "")
obj = yaml.load(content)

# -------- 6. XXE via xml.etree (XML-ETREE-FROMSTRING-001) --------
xml_data = request.args.get("xml", "")
root = ET.fromstring(xml_data)

# -------- 7. XXE via lxml (LXML-FROMSTRING-001) --------
root2 = lxml.etree.fromstring(xml_data)

# -------- 8. requests verify=False (REQUESTS-VERIFY-FALSE-001) --------
url = request.args.get("url", "")
requests.get(url, verify=False)

# -------- 9. SSRF via requests (SSRF-REQUESTS-001) --------
requests.post(request.args.get("url"))

# -------- 10. SSRF via urllib (SSRF-URLLIB-001) --------
import urllib.request
urllib.request.urlopen(request.args.get("url"))

# -------- 11. SSRF via httpx (SSRF-HTTPX-001) --------
httpx.get(request.args.get("url"))

# -------- 12. Insecure JWT decode (JWT-DECODE-NOVERIFY-001) --------
import jwt
jwt.decode(request.args.get("token", ""), options={"verify_signature": False})

# -------- 13. AES ECB mode (CRYP) --------
from Cryptodome.Cipher import AES
cipher = AES.new(b"SECRETSECRETSECRETS!", AES.MODE_ECB)

# -------- 14. Using random() for crypto (RANDOM-FOR-SECURITY-001) --------
token = random.choice("abcdef123456")

# -------- 15. Unverified SSL context (SSL-UNVERIFIED-CONTEXT-001) --------
ssl_context = ssl._create_unverified_context()

# -------- 16. Tarfile extractall (TARFILE-EXTRACTALL-001) --------
tar = tarfile.open("evil.tar")
tar.extractall("extract_here")

# -------- 17. Zipfile extractall (ZIPFILE-EXTRACTALL-001) --------
z = zipfile.ZipFile("evil.zip")
z.extractall("extract_zip")

# -------- 18. Missing cookie security flags (SET-COOKIE-MISSING-FLAGS-001) --------
@app.route("/setcookie")
def cookie():
    resp = make_response("ok")
    resp.set_cookie("sessionid", "12345")   # no httponly, secure, samesite
    return resp

# -------- 19. CORS allow * (CORS-ALLOW-ALL-001) --------
@app.after_request
def apply_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
