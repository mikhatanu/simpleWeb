from flask import Flask, render_template,request
from configparser import ConfigParser
import requests

conf=ConfigParser()
conf.read('conf.ini')
rpcip=conf.get('chain','rpcip')
rpcuser=conf.get('chain','rpcuser')
rpcpassword=conf.get('chain','rpcpassword')
rpclink='http://'+rpcuser+rpcpassword+'@'+rpcip
try:
    chainname=conf['chain']['chainname']
except:
    chainname=''

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_new_box',methods=['GET','POST'])
def createNewBox():
    #check for request method
    if request.method == 'POST':
        box_id=str(request.form['box_id'])
        #Send to multichain
        headers={'content-type' : 'application/json'}
        data={"method":"issue","params":["1KnR1xn3jgLs7JRpn99TdBWgstcFzKnD4UKX9q",{"name":box_id,"open":True},1,1,0,{"asset_id":"smartbox"}],"chain_name":chainname}
        try:
            request_data=requests.post(rpclink,headers=headers,json=data)
            if request_data.ok:
                status = "Success creating box with txid "+request_data.text
                status_var=1
            else:
                status= "Error connecting to multichain"
                status_var=0
        except requests.exceptions.RequestException as e:
            status=str(e)
            status_var=0
        
        #return status message
        return render_template('create_new_box.html', status=status,status_var=status_var)
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