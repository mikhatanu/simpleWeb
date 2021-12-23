import sqlite3
import requests
import sys
from configparser import ConfigParser 

#read config file for user and password
conf=ConfigParser()
conf.read('conf.ini')
#connect to db and execute the schema
connection=sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

#query multichain for the first addresses to be registered as pabrikbox address
headers = {'content-type' : 'application/json'}
data = {"method":"getnewaddress","params":[],"chain_name":"chain1"}
url='http://'+conf['chain']['rpcuser']+":"+conf['chain']['rpcpassword']+'@'+conf['chain']['rpcip']
request_data=requests.post(url, headers=headers, json=data)
if request_data:    
    pabrikbox_address=request_data.json()['result']
else:
    error_msg=request_data.text
    print(error_msg)
    sys.exit()
#pabrikbox_address=pabrikbox_data['result'](0)['address']

#set permission ke address baru
data={"method":"grant","params":[pabrikbox_address,"connect,send,receive,create,issue"],"chain_name":str(conf['chain']['chainname'])}
request_data=requests.post(url,headers=headers,json=data)

cur = connection.cursor()
cur.execute("INSERT INTO user (username,walletaddress) VALUES (?,?)",('pabrikbox',pabrikbox_address))
connection.commit()
connection.close()