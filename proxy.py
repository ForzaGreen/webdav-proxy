from flask import Flask, request, url_for, redirect, Response
import requests, json, random, string
from flask.ext.cors import CORS

app = Flask(__name__)
CORS(app)

FILE = "sample.txt"
USERS = {
    "chikien": {
        "server":"apache2",
        "url":"http://localhost/webdav/",
        "permitted_files": [
            "/chikien/*",
            "/ismail/f1.jpeg"
        ]
    },
    "wael": {
        "server": "nginx",
        "url": "http://localhost:6002/",

    },
    "ismail": {
        "server": "lighttpd",
        "url": "http://localhost:6003/"
    }
}


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/proxy',  methods=['GET', 'POST'])
def proxy():
    if request.method == "GET":
        app.logger.debug("a proxy request")
        Username = request.headers.get('Username')
        app.logger.debug(Username)
        url = USERS.get(Username).get('url') + FILE
        r = requests.get(url)
        # #r = requests.Request('PROPFIND','http://localhost/webdav/sample.txt', auth=requests.auth.HTTPDigestAuth('alex', 'alex'))
        # r = requests.Request('PROPFIND','http://localhost/webdav/sample.txt')
        # s = requests.Session()
        # resp = s.send(r.prepare())
        # app.logger.debug(resp.text)
        # return Response(resp.text)
        app.logger.debug(r)
        return Response(r)
    if request.method == "POST":
        app.logger.debug(request.data)
        return 'ok data received'
    else:
        return 'sth'

@app.route('/proxy/dav/<username>', methods=['PROPFIND', 'MKCOL', 'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def myDav(username):
    if request.method == "OPTIONS":
        return "sth"


    else:
        ##############################
        davUrl = USERS.get(username).get('url')
        app.logger.debug("Sending " + request.method + " request to: " + davUrl)

        r = requests.Request( request.method, davUrl )
        s = requests.Session()
        resp = s.send(r.prepare())
        app.logger.debug(resp.text)
        app.logger.debug("")
        app.logger.debug(resp.headers)
        ##############################
        response = Response(resp.text)
        if request.method == "GET":
            response.headers['Content-Type'] = 'multipart/form-data'
        else:
            response.headers['Content-Type'] = 'application/xml'
        return response
        # return Response( response=resp.content, status=resp.status_code)
        

@app.route('/proxy/dav/<username>/<path:fileOrDir>', methods=['PROPFIND', 'MKCOL', 'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def dav(username, fileOrDir):
    ##############################

    davUrl = USERS.get(username).get('url') + fileOrDir
    app.logger.debug("Sending " + request.method + " request to: " + davUrl)

    print("form: ", request.form)
    print("args: ", request.args)
    print("values: ", request.values)
    print("length data: ", len(request.data))
    print("files: ", request.files)
    r = requests.Request( request.method, davUrl, data=request.data )
    s = requests.Session()
    resp = s.send(r.prepare())
    ##############################
     
    print("resp H: ", resp.headers)
    print("Type resp H: ", type(resp.headers))
    if request.method == "GET":
        response = Response(resp.content)
        response.headers['Content-Type'] = resp.headers['Content-Type']
        for k in resp.headers.keys():
            response.headers[k] = resp.headers[k]
    else:
        response = Response(resp.text)
        response.headers['Content-Type'] = 'application/xml'
    print("response H: ", response.headers)
    print("Type response H: ", type(response.headers))
    return response


@app.route('/proxy/login', methods=['GET', 'POST', 'OPTIONS'])
def login():
    if request.method == "POST":
        app.logger.debug(request.data)
        username = json.loads(request.data.decode("utf-8")).get("username") #bytes -> str -> dict
        return 'login success'
    else: 
        return 'sth'

@app.route('/proxy/signup', methods=['GET', 'POST', 'OPTIONS'])
def signup():
    if request.method == "POST":
        app.logger.debug(request.data)
        #get token + discard token + signing up 
        return 'signup success'
    else: 
        return 'sth'

@app.route('/proxy/token', methods=['GET', 'POST', 'OPTIONS'])
def token():
    if request.method == "POST":
        app.logger.debug(request.data)
        typeOfUser = json.loads(request.data.decode("utf-8")).get("type") #bytes -> str -> dict
        def generateToken(typeOfUser, N):
            return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(N))
        token = generateToken(typeOfUser, 10) 
        #store this token in the database   
        return token
    else: 
        return 'sth'

@app.route('/index')
def index():
    app.logger.debug("looking for home page")
    return redirect(url_for('static', filename='startbootstrap-stylish-portfolio-1.0.4/index.html'))


if __name__ == '__main__':
    app.run(debug = True)