import sqlite3
import requests
from configparser import ConfigParser 

#read config file for user and password
conf=ConfigParser()
conf.read('conf.ini')
#connect to db and execute the shema
connection=sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

#query multichain for the first addresses to be registered as pabrikbox address
headers = {'content-type' : 'application/json'}
data = {"method":"listaddresses","params":["*",true,1,0],"chain_name":"chain1"}
url='http://'+conf['chain']['rpcuser']+conf['chain']['rpcpassword']+'@'+conf['chain']['rpcip']
request_data=requests.post(url, headers=headers, json=data)
pabrikbox_data=request_data.json()
pabrikbox_address=pabrikbox_data['result'](0)['address']

cur = connection.cursor
cur.execute("INSERT INTO user (username,walletaddress) VALUES (?,?)",('pabrikbox',pabrikbox_address))