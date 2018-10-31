import socket, json, ast
from sklearn import svm
from sklearn.externals import joblib

print ("Server is starting" ) 
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', 8080))    
sock.listen(5)

while True:
    cl, addr = sock.accept()
    buf = cl.recv(4096)
    print(buf)
    buf = ast.literal_eval(bytes.decode(buf))

    clf = joblib.load("./train_model_forest_new.m")
    ans = clf.predict([buf])[0]
    print(str.encode(ans))
    cl.send(str.encode(ans))
    cl.close()


