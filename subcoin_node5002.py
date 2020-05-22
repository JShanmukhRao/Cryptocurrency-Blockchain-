# Module 2 Cryptocurrency
# install Postman,Flask,requests
import datetime
import json
import hashlib
from flask import Flask , jsonify,request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Building Blockchain
class Blockchain:
    
    def __init__(self):
        self.chain=[]
        self.transaction=[]
        self.create_block(proof=1,previous_hash='0')
        self.node=set()
    
    def create_block(self,proof,previous_hash):
        block={'index':len(self.chain)+1,
            'timestamp':str(datetime.datetime.now()),
            'proof':proof,
            'previous_hash':previous_hash,
            'transaction':self.transaction
            }
        self.transaction=[]
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
        
    def proof_of_work(self,previous_proof):
        new_proof=1
        check_proof=False
        while check_proof is False:                                                   #hexdigest() is used to convert output of sha256 in hexa
            hash_operator=hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()  #encode() is used to encode the string in right format expected by sha256()
            if hash_operator[:4]=='0000':
                check_proof=True
            else:
                new_proof += 1
        return new_proof
        
    def hash(self,block):
        encoded_blocl= json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(encoded_blocl).hexdigest()

        
             
        
    def is_chain_valid(self,chain):
        previous_block=chain[0]
        block_index=1
        while block_index<len(chain):
            block=chain[block_index]
            if block['previous_hash']!=self.hash(previous_block):
                return False
            previous_proof=previous_block['proof']
            proof=block['proof']
            hash_operator=hashlib.sha256(str(proof**2-previous_proof**2).encode()).hexdigest()  #encode() is used to encode the string in right format expected by sha256()
            if hash_operator[:4]!='0000':
                return False
            previous_block=block
            block_index += 1
            return True
            
    def add_transaction(self,sender,receiver,amount):
        self.transaction.append({'sender':sender,
                                 'receiver':receiver,
                                 'amount':amount
                                 })
        return len(self.chain)+1
    def add_node(self,address):
        self.node.add(urlparse(address).netloc)
     
    def replace_chain(self):
        network=self.node
        longest_chain=None
        max_len=len(self.chain)
        for node in network:
            response=requests.get(f'http://{node}/get_chain')
           
            if response.status_code==200:
                length=response.json()['length']
                chain=response.json()['chain']
                if length > max_len and self.is_chain_valid(chain):
                    max_len=length
                    longest_chain=chain
        if longest_chain:
            self.chain=longest_chain
            return True
        return False
    
    def rec(self):
        network=self.node
        for node in network:
            response=requests.get(f'http://{node}/replace_chain')
    
# Mining our Blockchain
    
#creating Web App
app=Flask(__name__)

# Creating an address for the node on Port 5000
node_address=str(uuid4()).replace('-','')

#Creating Blockchain
blockchain=Blockchain()

#Mining new block
@app.route('/mine_block', methods=['GET'])

def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address , receiver='Yash' , amount=1)
    block=blockchain.create_block(proof, previous_hash)
    self_hash=blockchain.hash(block)
    response={'message':"SuccessFull",
              
              'index':block['index'],
              'timestamp':block['timestamp'],
              'proof':block['proof'],
              'previous_hash':block['previous_hash'],
              'self_hash':self_hash,
              'transaction': block['transaction']
              }
    blockchain.rec()
           
    return jsonify(response),200

 

# getting full blockchain
@app.route('/get_chain', methods=['GET'])

def get_chain():
    response={'chain': blockchain.chain,
              'length':len(blockchain.chain)}
    return jsonify(response),200

#Validation of chain
@app.route('/is_valid', methods=['GET'])

def is_valid():
    chain=blockchain.chain
    validation=blockchain.is_chain_valid(chain)
    response={'Validation':validation}
    return jsonify(response),200

# Adding new transaction on blockchain
@app.route('/add_transaction', methods=['POST'])

def add_transaction():
    json=request.get_json()
    transaction_key=['sender','receiver','amount']
    if not all(key in json for key in transaction_key):
        return 'some elements of transaction is missing', 400
    index=blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response={'message': f'this transaction will be added to block{index}'}
    return jsonify(response),201



# Connecting new nodes
@app.route('/connect_nodes', methods=['POST'])
def connect_nodes():
    json=request.get_json();
    nodes=json.get('nodes')
    if nodes is None:
        return 'No Nodes 400'
    for node in nodes:
        blockchain.add_node(node)
        
    response={'message':'All nodes are connected',
              'total':list(blockchain.node)}
    return jsonify(response),201

# Replacing the chain with longest chain
@app.route('/replace_chain', methods=['GET'])

def replace_chain():
    is_chain_valid=blockchain.replace_chain()
    if is_chain_valid:
        response={'message': 'The node has different nodes so chain was replaced by longest chain',
                  'new_chain':blockchain.chain}
    else:
        response={'message': 'The chain was longest',
                  'actual_chain':blockchain.chain}
    return jsonify(response),200

app.run(host='0.0.0.0',port= 5002)
