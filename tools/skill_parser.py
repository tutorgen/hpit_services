import csv
import json
import argparse
import requests

import json

from itertools import groupby

from pymongo import MongoClient
from couchbase import Couchbase

parser = argparse.ArgumentParser(description='Parse transaction log from datashop.')
parser.add_argument('filename', metavar='filename', type=str, 
                   help='The filename of the datashop transaction log file.')
parser.add_argument('--json', action="store_true", help='Parse the file as json.(i.e. previous dump from this program)')
parser.add_argument('--first', action="store_true", help='Dump only the first transaction object.')
parser.add_argument('--distinct', dest='attribute', help='Get the distinct entries for an attribute')
parser.add_argument('--dump', action="store_true", help='Dump transaction data as json.')
parser.add_argument('--relax', action="store_true", help='Send to HPIT')
parser.add_argument("--db", action="store_true",help = "Store to MongoDB and Couchbase cache")

def read_rows(filename):
    rows = []
    with open(filename, newline = '') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', quotechar='"')
        for row in reader:
            rows.append(row)

    return rows


def slug_item(item):
    item = item.lower()
    item = item.replace(' ', '_')
    item = item.replace('-', '_')
    item = item.replace('(', '')
    item = item.replace(')', '')
    return item

def slug_headers(header_row):
    return [slug_item(i) for i in header_row]

def kill_empty_pairs(transaction):
    return {k:v for k,v in transaction.items() if v}

def build_transactions(headers, rows):
    #fields = ['school', 'class', 'level_unit', 'level_section', 'problem_name', 'step_name']
    fields = []
    trans = [dict(zip(headers, r)) for r in rows]
    trans = [kill_empty_pairs(t) for t in trans]
    trans = [split_knowledge_components(t) for t in trans]
    trans = group_by_fields(trans, fields)
    return {trans[0] : trans[1]}

def split_knowledge_components(transaction):
    knowledge_components = {}
    remove_keys = []
    for k,v in transaction.items():
        if k[0:3] == "kc_":
            knowledge_components[k[3:]] = v
            remove_keys.append(k)

    transaction = {k:v for k,v in transaction.items() if k not in remove_keys}
    transaction['knowledge_components'] = knowledge_components

    return transaction

def remove_fields(transaction, field_names):
    for field in field_names:
        if field in transaction:
            del transaction[field]

    return transaction

def clean_transactions(transactions):
    fields = []#['level_unit', 'level_section', 'school', 'class', 
        #'problem_name', 'step_name', 'row']
    return [remove_fields(t, fields) for t in transactions]

def group_by_fields(transactions, fields):

    if not fields:
        return ('transactions', clean_transactions(transactions))

    field = fields[0]
    items = []
    key_func = lambda x: x[field] if field in x else None
    trans = sorted(transactions, key=key_func)
    for value, group in groupby(trans, key=key_func):
        sub_items = group_by_fields(list(group), fields[1:])

        items.append({
            'name': value,
            sub_items[0]: sub_items[1]
            })

    return (field, items)

#Attr string is a . separated list of attributes where . is a scope resolution operator
def extract_attribute(transaction, attr_string):
    attrs = attr_string.split('.')

    trans_obj = transaction
    for attr in attrs:
        if attr in trans_obj:
            trans_obj = trans_obj[attr]

    if type(trans_obj) != type(dict()):
        return trans_obj


def key_on_attribute(attr_string):
    attrs = attr_string.split('.')

    def wrapped(transaction):
        trans_obj = transaction
        for attr in attrs:
            if attr in trans_obj:
                trans_obj = trans_obj[attr]

        if type(trans_obj) != type(dict()):
            return trans_obj
        pass

    return wrapped


def skills_to_db(filename):
    
    skills = {}

    with open(filename, newline = '') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', quotechar='"')
 
        headers = None
        for row in reader:
            if headers == None:
                headers = slug_headers(row)
                continue
            try:
                transaction = build_transactions(headers,[row])["transactions"][0]
            except IndexError:
                print("Warning: problem in parsing; transactions[0] raises IndexError")
                print("--> " + str(transaction))
                continue
                
            try:
                skill = transaction["knowledge_components"]["ktskills_mcontext_single"]
            except KeyError:
                print("Warning: No ktskills_mcontect_single found in knowledge_components")
                print("--> " + str(transaction))
                continue
                
            if skill not in skills:
                skills[skill] = 0
            else:
                skills[skill] += 1
        
        cache = Couchbase.connect(bucket = "skill_cache", host = "127.0.0.1") 
        client = MongoClient()
        db = client.hpit.hpit_skills
        for k,v in skills.items():
            iid = db.update({"skill_name":skills[k]},{"skill_name":skills[k]},upsert=True)
            cache.set(str(skills[k]),str(iid))
        
if __name__ == '__main__':
    args = parser.parse_args()
    #skills_to_db(args.filename)
    
    transactions = []
    if args.json:
        with open(args.filename) as f:
            transactions = json.loads(''.join(f.readlines()))
    else:
        rows = read_rows(args.filename)
        header_row = rows[0]
        rows = rows[1:]
        headers = slug_headers(header_row)
        transactions = build_transactions(headers, rows)

    if args.attribute:
        items = [extract_attribute(t, args.attribute) for t in transactions]
        items = filter(lambda x: x is not None, items)
        print ('\n'.join(set(items)))
    elif args.first:
        print (json.dumps(transactions["transactions"][130], indent=4))
    elif args.dump:
        print (json.dumps(transactions["transactions"], indent=4))
    elif args.relax:
        transactions = transactions['transactions']

        for t in transactions: 
            turl = 'http://127.0.0.1:5984/transactions/' + t['transaction_id']
            print ("Storing Transaction: " + turl)

            requests.put(turl, data=json.dumps(t), headers={'content-type': 'application/json'})

        print ("DONE!")
    elif args.db:
        skills_to_db(args.filename)
        print ("DONE!")
