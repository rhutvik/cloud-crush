
import copy
import json
import jsonpickle
import random
import requests
import uvicorn

from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates

from clock import VectorClock
from orset import ORSet
from zkClient import zkClient

import sqlalchemy
from sqlalchemy.sql import select
from sqlalchemy import create_engine, Table, MetaData, update

zkc = zkClient()
zkc.register()

app = FastAPI()

#Template Directory
templates = Jinja2Templates(directory="templates")

engine = create_engine('mysql+pymysql://root:admin@10.0.0.24:3306/store',
                       pool_recycle=3600)

connection = engine.connect()

metadata = MetaData()

N = 3
W = 1
R = 3

crush_url = 'http://10.0.0.23:5000/nodes'

async def make_add_request(url: str, key: str, value: tuple, tag: str):
    resp = requests.post(url+'/add',
                         data={'user_id': key, 'item': value, 'tag': tag},
                         timeout=0.8)
    return resp.json()

async def make_delete_request(url: str, key: str, value: tuple):
    resp = requests.post(url+'/delete',
                         data={'user_id': key, 'item': value}, timeout=0.8)
    return resp.json()

async def make_list_request(url: str, key: str):
    resp = requests.post(url+'/list', data={'user_id': key}, timeout=0.8)
    return resp.json()

async def make_get_ind_request(url: str, key: str, value: str):
    resp = requests.post(url+'/get_ind',
                         data={'key': key, 'value': value}, timeout=0.8)
    return resp.json()

def get_data():
    customer = Table('customer', metadata, autoload=True, autoload_with=engine)
    stmt_cst = select([customer])
    res_cst = connection.execute(stmt_cst).fetchall()
    
    product = Table('product', metadata, autoload=True, autoload_with=engine)
    stmt_pdt = select([product.c.pid, product.c.pname, product.c.price])\
        .where(product.c.qty > 0)
    res_pdt = connection.execute(stmt_pdt).fetchall()
    return res_cst,res_pdt

def update_product_qty(oper, product_id):
    product = Table('product', metadata,
                    autoload=True, autoload_with=engine)
    if oper == 'incr':
        stmt_pdt = product.update().values(qty=(product.c.qty + 1))\
                                   .where(product.c.pid == product_id)
    elif oper == 'decr':
        stmt_pdt = product.update().values(qty=(product.c.qty - 1))\
                                   .where(product.c.pid == product_id)
    res_pdt = connection.execute(stmt_pdt)
    return res_pdt.rowcount
    
@app.get('/', status_code=200)
def home_page(request: Request):
    res_cst,res_pdt = get_data()
    return templates.TemplateResponse('hello.html',
                                      context={'request': request,
                                               'products': res_pdt,
                                               'customers': res_cst})

@app.post('/add')
async def add_item(key: str = Form(...), value: str = Form(...)):
    result = ""
    value = tuple(value.split(","))
    response_count = 0
    tag = str(random.randint(0, 100000000000))
    reply = requests.post(crush_url,
                          data={'key': key}, timeout=0.8).json()
    nodes_ips = zkc.get_nodes_ips(reply['device_list'])
    device_urls = [str('http://'+ip+':5000') for ip in nodes_ips]
    random.shuffle(device_urls)
    for url in device_urls:
        try:
            serial_cart, serial_vc = await make_add_request(url, key,
                                                            value, tag)
            vc = jsonpickle.decode(serial_vc)
            cart = jsonpickle.decode(serial_cart)
            res = {'cart': cart.display(), 'vc': vc.clock}
            result += str(res)
            #result = result + str(await make_add_request(url, key, value, tag))
            response_count += 1
            if response_count >= W:
                #return result
                break
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
    rowcount = update_product_qty('decr', value[0])
    return result

@app.post('/delete')
async def delete_item(key: str = Form(...), value: str = Form(...)):
    result = ""
    value = tuple(value.split(","))
    response_count = 0
    reply = requests.post(crush_url,
                          data={'key': key}, timeout=0.8).json()
    nodes_ips = zkc.get_nodes_ips(reply['device_list'])
    device_urls = [str('http://'+ip+':5000') for ip in nodes_ips]
    random.shuffle(device_urls)
    for url in device_urls:
        try:
            serial_cart, serial_vc = await make_delete_request(url, key,value)
            vc = jsonpickle.decode(serial_vc)
            cart = jsonpickle.decode(serial_cart)
            res = {'cart': cart.display(), 'vc': vc.clock}
            result += str(res)
            #result = result + str(await make_delete_request(url, key, value))
            response_count += 1
            if response_count >= W:
                rowcount = update_product_qty('incr', value[0])
                return result
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
    return result

@app.post('/listall')
async def listall(key: str = Form(...), value: str = Form(...)):
    result = ""
    cust_set = set()
    all_kvs_ips = zkc.get_kvs_ips()
    device_urls = [str('http://'+ip+':5000') for ip in all_kvs_ips]
    for url in device_urls:
        try:
            cust_set.update(list(await make_get_ind_request(url, key, value)))
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
    for cust in cust_set:
        resp = await list_cart_items(cust)
        result += str({'cust_id': cust, 'cart': resp['cart'], 'vc': resp['vc'].clock})
    return result

def converge(vcs):
    """Return a single VectorClock that subsumes all of the input VectorClocks"""
    result = VectorClock()
    for vcp in vcs:
        vc = vcp[1]
        if vc is None:
            continue
        for node, counter in vc.clock.items():
            if node in result.clock:
                if result.clock[node] < counter:
                    result.clock[node] = counter
            else:
                result.clock[node] = counter
    return result


def resolve_conflict(cv_list: list):
    # compares the version vectors and detect concurrect writes
    # takes appropriate action to get a consistent value for the key
    # returns the updated value and version vector
    results = []
    for cvc in cv_list:
        vc = cvc[1]
        subsumed = False
        for ii, cartv in enumerate(results):
            result = cartv[1]
            if vc <= result:  # subsumed by existing answer
                subsumed = True
                break
            if result < vc:  # subsumes existing answer so replace it
                results[ii] = (cvc[0], copy.deepcopy(vc))
                subsumed = True
                break
        if not subsumed:
            results.append((cvc[0], copy.deepcopy(vc)))
    r_i = ORSet(id=results[0][0].id)
    for r in results:
        r_i.merge(r[0])
    final_vc = converge(results)
    return r_i, final_vc

async def repair_request(url, key, cart, vc):
    serial_cart = jsonpickle.encode(cart)
    serial_vc = jsonpickle.encode(vc)
    resp = requests.post(url+'/write',
                         data={'user_id': key, 'sz_cart': serial_cart,
                               'sz_vc': serial_vc}, timeout=0.8)
    return resp.json(), resp.status_code

async def read_repair(key, cart, vc):
    # sends write request to all the replicas holding the key-value pair
    result = ""
    success = 0
    reply = requests.post(crush_url,
                          data={'key': key}, timeout=0.8).json()
    nodes = zkc.get_nodes_ips(reply['device_list'])
    #assert len(res) >= R
    for ip in nodes:
        url = str('http://'+ip+':5000')
        reply, code = await repair_request(url, key, cart, vc)
        if code in [200, '200']:
            success += 1
        result += str(reply)
    #assert success >= N
    return result

@app.post('/list')
async def list_cart_items(key: str = Form(...)):
    result = []
    r_success = 0
    reply = requests.post(crush_url,
                          data={'key': key}, timeout=0.8).json()
    nodes = zkc.get_nodes_ips(reply['device_list'])
    random.shuffle(nodes)
    for ip in nodes:
        try:
            url = str('http://'+ip+':5000')
            serial_cart, serial_vc = await make_list_request(url, key)
            r_success += 1
            vv = jsonpickle.decode(serial_vc)
            cc = jsonpickle.decode(serial_cart)
            print((cc.A, cc.R, vv))
            result.append((cc, vv))
            #if r_success >= R:
            #    break
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
    upd_cart, final_vc = resolve_conflict(result)
    await read_repair(key, upd_cart, final_vc)
    return {'cart': upd_cart.display(), 'vc': final_vc}

if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=5000,
                log_level="info", reload=True)
