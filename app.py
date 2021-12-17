from flask import Flask, render_template,request
from configparser import ConfigParser
import requests

conf=ConfigParser()
conf.read('conf.ini')
rpcip=conf['chain']['rpcip']
rpcuser=conf['chain']['rpcuser']
rpcpassword=conf['chain']['rpcpassword']
rpcLink='http://'+rpcuser+rpcpassword+'@'+rpcip

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_new_box',methods=['GET','POST'])
def createNewBox():
    #check for request method
    if request.method == 'POST':
        status = "Success creating box"
        
        #Send to multichain

        #return success message
        return render_template('create_new_box.html', status=status)
    return render_template('create_new_box.html')

@app.route('/send_box')
def sendBox():
    #send box/asset to other person
    return render_template('send_box.html')

@app.route('/daftar/pelanggan')
def daftarPelanggan():
    return render_template('daftar/daftar_pelanggan.html')


@app.route('/daftar/driver')
def daftarDriver():
    return render_template('daftar/daftar_driver.html')

@app.route('/daftar')
def daftar():
    return render_template('daftar/daftar.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)