import requests, json

def get_list():
    url = 'http://52.90.217.13:8080/get'
    r = requests.get(url)
    co = json.loads(r.text)['result']

    rst = []
    cur = []
    idx = 0
    z = 1

    while idx < len(co):
        if co[idx]['zcoordinate'] == z:
            temp = []
            xco = co[idx]['xcoordinate']
            yco = co[idx]['ycoordinate']
            temp.append(xco)
            temp.append(yco)
            cur.append(temp)
            idx += 1
        else:
            # if z == 15 or z == 14:
            #     cur = []
            #     z = co[idx]['zcoordinate']
            #     continue
            rst.append(cur)
            cur = []
            if z == 25:
                print("------------------")
                print(rst)
                print(len(rst))
                
            z = co[idx]['zcoordinate']
            # if z == 1:
            #     rst = []

    rst.append(cur)
    print("-------------------")
    print(rst)
    print(len(rst))

get_list()