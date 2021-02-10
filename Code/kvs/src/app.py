import json
import jsonpickle
import uvicorn

from fastapi import FastAPI, Form
from zkClient import zkClient
from kvs import Store
from indexing import SecondaryIndex

zkc = zkClient()
zkc.register()

app = FastAPI()
store = Store()
si = SecondaryIndex()

@app.get('/')
def hello_world():
    return {'HELLO, WORLD!': 'Hello'}

@app.post('/add')
def add_item(user_id: str = Form(...), item: tuple = Form(...),
             tag: str = Form(...)):
    if not store.acc_exists(user_id):
        store.create(user_id)
    uc = store.update('ADD', user_id, item[0], tag)
    si.update('ADD', user_id, item)
    j1, j2 = jsonpickle.encode(uc[0]), jsonpickle.encode(uc[1])
    print((j1, j2))
    return (j1, j2)

@app.post('/delete')
def delete_item(user_id: str = Form(...), item: tuple = Form(...)):
    if not store.acc_exists(user_id):   
        store.create(user_id)
    uc = store.update('DELETE', user_id, item[0])
    si.update('DELETE', user_id, item)
    j1, j2 = jsonpickle.encode(uc[0]), jsonpickle.encode(uc[1])
    print((j1, j2))
    return (j1, j2)
    
@app.post('/write')
def write(user_id: str = Form(...), sz_cart: str = Form(...),
          sz_vc: str = Form(...)):
    kart = jsonpickle.decode(sz_cart)
    vc = jsonpickle.decode(sz_vc)
    store.overwrite(user_id, kart, vc)
    return {'msg': 'SUCCESS'}

@app.post('/list')
def list_items(user_id: str = Form(...)):
    if not store.acc_exists(user_id):
        store.create(user_id)
    uc = store.get(user_id)
    return (jsonpickle.encode(uc[0]),
            jsonpickle.encode(uc[1]))

@app.post('/get_ind')
def get_indices(key: str = Form(...), value: str = Form(...)):
    return si.get_sec_index(key, value)
    
if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=5000,
                log_level="info", reload=True)
