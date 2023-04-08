#!/usr/bin/python

import logging
import sys
from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource, request
from dns_zone import DnsZone

app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
api = Api(app)

DEBUG = True

zone = 'clim.nl'                        # domein naam
nameserver = '44.214.171.38'           # IP van de DNS server
dns_zone = DnsZone(zone, nameserver)    # hierin geef je de benodigde gegevens voor de DnsZone module

parser = reqparse.RequestParser()
# Argumenten die je via curl en de methoden PUT en POST via "-d" kan meegeven, bv:
# curl http://192.168.190.100:5000/url/url -d "name=jan" -d "street=kerkstraat" -X POST
parser.add_argument('mail')
parser.add_argument('token')
parser.add_argument('fqdn')
parser.add_argument('ipv4')
# hier de overige argumenten ook zo benoemen



class NewUser(Resource):
      
    def post(self):
        
        data = request.get_json()   # haalt alle data op in JSON
        fqdn = data.get('fqdn')     # verwerkt de JSON in een "normale" format
        ipv4 = data.get('ipv4')
        #print(fqdn)
        #print(ipv4)     
        result, error = dns_zone.add_address(fqdn, ipv4)

        if error:
            print(f"Error: {result}")
        else:
            print(f"Success: {result}")
            
        return {'status': 'ok'}
        
        

class UserEdit(Resource):
    
    def put(self, user_mail):
        args = parser.parse_args()
        
        data = request.get_json()   
        fqdn = data.get('fqdn')     
        ipv4 = data.get('ipv4')

        dns_zone.update_address(fqdn, ipv4)     # update de A record in de DNS server
        
        
        return {'status': 'ok'}

    # Vraag informatie op over de user
    # curl http://192.168.190.100:5000/client/name/jan

    
class UserDelete(Resource):
    
    def delete(self):    # verwijdert de A record
            
        data = request.get_json()
        fqdn = data.get('fqdn')

        dns_zone.clear_address(fqdn)
            
        return {'status': 'ok'}
    
    
class UserRequest(Resource):

    def get(self):
        # data = request.get_json    
        # fqdn = data.get('fqdn')     # verwerkt de JSON in een "normale" format
        # print(fqdn)
        # # ipv4 = data.get('ipv4')

        # # result, error = dns_zone.check_address(fqdn)
        # result = dns_zone.check_address(fqdn)

        # # if error:
        # #     print(f"Error: {result}")
        # # else:
        # #     print(f"Success: {result}")
            
        # return {'status': 'ok'}


        data = request.get_json()
        fqdn = data.get('fqdn')
        result = dns_zone.check_address(fqdn)
        
        return jsonify(result)

##
## Elke url moet je hieronder apart definieren, dus /client/new  of /client/name
## Als een deel van de url een variabele is dan tussen vishaken, bv <user_name>
##
api.add_resource(NewUser, '/client/new')      # toont op welke URL er geluisterd wordt naar API requests  
api.add_resource(UserEdit, '/client/name/<user_mail>')
api.add_resource(UserDelete, '/client/delete')
api.add_resource(UserRequest, '/client/request')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
