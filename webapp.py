import sqlite3
from sqlite3 import Error
from flask import Flask, render_template,request
from configparser import ConfigParser
import requests

#Below loads config from conf.ini
conf=ConfigParser()
conf.read('conf.ini')
rpcip=conf.get('chain','rpcip')
rpcuser=conf.get('chain','rpcuser')
rpcpassword=conf.get('chain','rpcpassword')
rpclink='http://'+rpcuser+":"+rpcpassword+'@'+rpcip

try:
    chainname=conf['chain']['chainname']
except:
    chainname=''

#variable used globally
boxcreator="pabrikbox"
headers={'content-type' : 'application/json'}


app = Flask(__name__)
app.config["DEBUG"] = True

def createUserPelangganDB(username,walletaddress):
    """
    Create new user in user database
    :params username: (string)
    :params walletaddress: (string)
    :return :(boolean) true if succeed, false if not
    """
    try:
        conn=sqlite3.connect('database.db')
        cur=conn.cursor()
        cur.execute("INSERT INTO user (username,walletaddress) VALUES (?,?)",(username,walletaddress))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def createUserDriverDB(username,walletaddress):
    """
    Create new driver in driver database
    :params username: (string)
    :params walletaddress: (string)
    :return :(boolean) true if succeed, false if not
    """
    try:
        conn=sqlite3.connect('database.db')
        cur=conn.cursor()
        cur.execute("INSERT INTO driver (username,walletaddress) VALUES (?,?)",(username,walletaddress))
        conn.commit()
        conn.close()
        return True
    except:
        return False


def searchNameDB(address):
    """
    search name of user using user's address
    :param address: (string)
    :return dbdata: (string) from database, :(boolean) if false
    """
    walletaddress=str(address).replace(" ","")
    conn=sqlite3.connect('database.db')
    cur=conn.cursor()
    cur.execute("SELECT username FROM user WHERE walletaddress=?",(walletaddress,))
    try:
        dbdata=cur.fetchall()[0][0]
    except:
        conn.close()
        return False
    # print(dbdata)
    conn.close()
    return dbdata

def searchNameDriverDB(address):
    """
    search name of driver using driver's address
    :param address: (string)
    :return dbdata: (string) from database, :(boolean) if false
    """
    walletaddress=str(address).replace(" ","")
    conn=sqlite3.connect('database.db')
    cur=conn.cursor()
    cur.execute("SELECT username FROM driver WHERE walletaddress=?",(walletaddress,))
    try:
        dbdata=cur.fetchall()[0][0]
    except:
        conn.close()
        return False
    # print(dbdata)
    conn.close()
    return dbdata

def searchAddressDB(name):
    """
    search address of user using user's username
    :param name: (string)
    :return dbdata: (string) from database, :(boolean) if false
    """
    conn=sqlite3.connect('database.db')
    cur=conn.cursor()
    cur.execute("SELECT walletaddress FROM user WHERE username=?",(name,))
    try:
        dbdata=cur.fetchall()[0][0]
    except:
        conn.close()
        return False
    conn.close()
    return dbdata

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_new_box',methods=['GET','POST'])
def createNewBox():
    """
    Create new box to the boxcreator (pabrikbox) when posted. 
    :return render_template:(html) this html page with status code if 'post'. Return this page if 'get'
    """
    #check for request method
    if request.method == 'POST':
        box_id=str(request.form['box_id']).replace(" ","")
        if box_id:
        #connect to database to find pabrikbox wallet made in initdb.py
            try:
                #query pabrikbox's walletaddress
                box_creator_address=searchAddressDB(boxcreator)
                
                #Send to multichain
            
                data={"method":"issue","params":[str(box_creator_address),{"name":box_id,"open":True},1,1,0,{"asset_id":"smartbox"}],"chain_name":chainname}
                try:
                    request_data=requests.post(rpclink,headers=headers,json=data)
                    if request_data.ok:
                        status = "Success creating box with txid '"+request_data.json()["result"]+"'"
                        status_var=1
                    else:
                        status= "Error connecting to multichain"
                        status_var=0
                except requests.exceptions.RequestException as e:
                    status="Error connecting to multichain: "+str(e)
                    status_var=0
            except Error as e:
                status="Error connecting to database: " + str(e)
                status_var=0        
            #return status message
            return render_template('create_new_box.html', status=status,status_var=status_var)
        else:
            status='Please fill box id'
            status_var=0
            return render_template('create_new_box.html',status=status,status_var=status_var)
    return render_template('create_new_box.html')

@app.route('/send_box',methods=['GET','POST'])
def sendBox():
    """
    send box/asset to other person. If get, only webpage is returned. If post, then data will be send to multichain
    :return render_template: (html) html page 'get' and html plus status message if 'post'
    """
    #check for request method
    if request.method == 'POST':
        driver_address=str(request.form['driver_address']).replace(" ","")
        box_id=str(request.form['box_id']).replace(" ","")

        if not driver_address and box_id:
            status="Please fill all the field!"
            status_var=0 
            return render_template('send_box.html', status=status, status_var=status_var)

        
        #search database for driver and pabrikbox
        driver_name = searchNameDriverDB(driver_address)
        box_creator_address=searchAddressDB(boxcreator)

        #check if driver's address is registered already
        if not driver_name and box_creator_address:
            status = "Driver name or box creator address is not found"
            status_var=0
            return render_template('send_box.html',status=status, status_var=status_var)
        #print(box_creator_address +'\n'+ driver_name)
        try:
        
            #send asset from pabrikbox to multichain
            data={"method":"sendassetfrom","params":[box_creator_address,driver_address,box_id,1,0,boxcreator,driver_name],"chain_name":chainname}
            try:
                request_data=requests.post(rpclink,headers=headers,json=data)
                if request_data.ok:           
                        txid=request_data.json()["result"]
                elif not request.data:
                    status = "Box already sent or not created yet"
                    status_var=0
                    return render_template('send_box.html', status=status, status_var=status_var)
                else:
                    status="Error sending asset in multichain with status code "+str(request_data.status_code)
                    status_var=0 
                    return render_template('send_box.html', status=status, status_var=status_var)

                #create stream
                data={"method":"create","params":["stream",box_id,{"restrict":""},{"description":"stream for tracking smartbox"}],"chain_name":chainname}
                try:
                    request_data=requests.post(rpclink,headers=headers,json=data)
                    if request_data.ok:
                        status = "Success creating box with txid '"+txid+"' and stream with txid '"+request_data.json()["result"]+"'"
                        status_var=1
                    else:
                        status="Error creating stream in multichain with status code "+str(request_data.status_code)
                        status_var=0
                except requests.exceptions.RequestException as e:
                    status="Error occured"+str(e)
                    status_var=0
                #end create stream

            except requests.exceptions.RequestException as e:
                status="Error occured: "+str(e)
                status_var=0
            #end send asset

        except Error as e:
            status="Error connecting to database: " + str(e)
            status_var=0
        #end check database
        return render_template('send_box.html', status=status, status_var=status_var)
    return render_template('send_box.html')

@app.route('/register/pelanggan',methods=['GET','POST'])
def daftarPelanggan():
    """
    Register new user
    :return render_template: (html) html page if 'get' and html page with status and status code if 'post'
    """
    if request.method=='POST':
        username=str(request.form['username']).replace(" ","")
        if not username:
            status="Please fill the username"
            status_var=0
            return render_template('register/daftar_pelanggan.html',status=status,status_var=status_var)
        elif username == boxcreator:
            status="Please change the username"
            status_var=0
            return render_template('register/daftar_pelanggan.html',status=status,status_var=status_var)

        #register new user
        data = {"method":"getnewaddress","params":[],"chain_name":chainname}
        try:
            request_data=requests.post(rpclink,headers=headers,json=data)
            if request_data.ok:    
                new_address=request_data.json()['result']
                status="Success creating new address with address '"+new_address+"'"
                status_var=1
            else:
                status="Error connecting to multichain: "+request_data.status_code +"<br> Error Creating new address"
                status_var=0
        except requests.exceptions.RequestException as e:
            status="Error occured: "+str(e)
            status_var=0

        #grant permission
        data={"method":"grant","params":[new_address,"send,receive"],"chain_name":chainname}
        try:
            request_data=requests.post(rpclink,headers=headers,json=data)
        except requests.exceptions.RequestException as e:
            status="Error occured: "+str(e)
            status_var=0
        try:
            createUserPelangganDB(username,new_address)
        except Error as e:
            status="Error creating new user: "+str(e)
            status_var=0
        return render_template('register/daftar_pelanggan.html',status=status,status_var=status_var)
    return render_template('register/daftar_pelanggan.html')


@app.route('/register/driver',methods=['GET','POST'])
def daftarDriver():
    """
    Register new driver
    :return render_template: (html) html page if 'get' and html page with status and status code if 'post'
    """
    if request.method=='POST':
        username=str(request.form['username']).replace(" ","")
        if not username:
            status="Please fill the username"
            status_var=0
            return render_template('register/daftar_pelanggan.html',status=status,status_var=status_var)
            
        #register new user
        data = {"method":"getnewaddress","params":[],"chain_name":chainname}
        try:
            request_data=requests.post(rpclink,headers=headers,json=data)
            if request_data.ok:    
                new_address=request_data.json()['result']
                status="Success creating new address with address '"+new_address+"'"
                status_var=1
            else:
                status="Error connecting to multichain: "+request_data.status_code +"<br> Error Creating new address"
                status_var=0
        except requests.exceptions.RequestException as e:
            status="Error occured: "+str(e)
            status_var=0

        #grant permission
        data={"method":"grant","params":[new_address,"send,receive"],"chain_name":chainname}
        try:
            request_data=requests.post(rpclink,headers=headers,json=data)
        except requests.exceptions.RequestException as e:
            status="Error occured: "+str(e)
            status_var=0
        try:
            createUserDriverDB(username,new_address)
        except Error as e:
            status="Error creating new driver: "+str(e)
            status_var=0
        return render_template('register/daftar_pelanggan.html',status=status,status_var=status_var)

    return render_template('register/daftar_driver.html')

@app.route('/register')
def daftar():
    return render_template('register/register.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)