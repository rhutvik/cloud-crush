import uvicorn
import crush
import json
import jenkins

from fastapi import FastAPI, Form
from zkClient import zkClient

app = FastAPI()

zkc = zkClient()

def get_current_map():
    device_lists = zkc.get_nodes_list()
    children_list = []
    i = 0
    for device in device_lists:
        child = {}
        child['id'] = i
        child['name'] = device
        child['weight'] = 65536
        children_list.append(child)
        i += 1
    crush_map = {}
    crush_map['trees'] = []
    crush_map['trees'].append({})
    crush_map['trees'][0]['type'] = "root"
    crush_map['trees'][0]['name'] = "root"
    crush_map['trees'][0]['id'] = -1
    crush_map['trees'][0]['children'] = children_list
    crush_map['rules'] = {}
    crush_map['rules']['data'] = [["take", "root"],
                                  ["chooseleaf", "firstn", 0, "type", "root"],
                                  ["emit"]]
    dumped = json.dumps(crush_map)
    print(dumped)
    return dumped


@app.get('/', status_code=200)
def hello_world():
    return {'Hello': 'Hello World!'}
    

@app.post('/nodes')
async def calculate_crush(key: str = Form(...)):
    c = crush.Crush()
    c.parse(json.loads(get_current_map()))
    hashed_val = jenkins.hashlittle(key)%2147483647
    print(hashed_val)
    ans = c.map(rule="data", value=hashed_val, replication_count=3)
    return {'device_list': ans}


if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=5000,
                log_level="info", reload=True)
