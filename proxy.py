from flask import Flask, request, url_for, redirect, Response
from flask.ext.mysql import MySQL
import requests, json, random, string
from flask.ext.cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app, methods=['GET', 'PROPFIND', 'MKCOL', 'MOVE', 'COPY', 'HEAD', 'POST', 'OPTIONS', 'PUT', 'PATCH', 'DELETE'])
mysql=MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'ismail'
app.config['MYSQL_DATABASE_PASSWORD'] = 'webdav'
app.config['MYSQL_DATABASE_DB'] = 'Webdav'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


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
        "url": "http://localhost:6002/"
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
    print("###############################################")
    if request.method == "OPTIONS":
        return "sth"
    ##############################

    else:
        print(request.headers)

        davUrl = USERS.get(username).get('url') + fileOrDir
        app.logger.debug("Sending " + request.method + " request to: " + davUrl)

        r = requests.Request( request.method, davUrl, data=request.data )
        s = requests.Session()
        resp = s.send(r.prepare())
        ##############################
         
        print("resp H: ", resp.headers)

        _resourcePath = fileOrDir
        _resourceUploader = username
        
        if request.method == "PUT":
            _resourceType = 'file'
            _resourceKey = request.headers.get("file-key") #json.loads(request.data.decode("utf-8")).get("file_key")

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addResource',(_resourcePath,_resourceUploader,_resourceType, _resourceKey))
            data = cursor.fetchall()
     
            if len(data) is 0:
                conn.commit()
                print "Resource " + _resourcePath + " stored with key : " + _resourceKey

            else:
                print 'An error occurred!'
            cursor.close()
            conn.close()
        
        if request. method == "MKCOL":
            _resourceType = 'collection'
            _resourceKey = request.headers.get("dir-key")

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addResource',(_resourcePath,_resourceUploader,_resourceType, _resourceKey))
            data = cursor.fetchall()
     
            if len(data) is 0:
                conn.commit()
                print "Resource " + _resourcePath + " stored with key : " + _resourceKey

            else:
                print 'An error occurred!'
            cursor.close()
            conn.close()

        if request.method == "POST":
            _resourceKey = _resourceKey = request.headers.get("resource-key");

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_accessresource',(_resourcePath,))
            data = cursor.fetchall() 

            if len(data) > 0:
                if str(data[0][4]) == _resourceKey: 
                    return 'Good password'
            else:
                return 'Wrong password'
            cursor.close()
            conn.close()                  

        if request.method == "GET":
            response = Response(resp.content)
            response.headers['Content-Type'] = resp.headers['Content-Type']
            for k in resp.headers.keys():
                response.headers[k] = resp.headers[k]

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_accessresource',(_resourcePath,))
            data = cursor.fetchall()

            if (str(data[0][4])=='null'):
                return 'Not encrypted'
            else:
                return 'Encrypted'

        if request.method == "DELETE":
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_deleteResource',(_resourcePath,))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
            
            cursor.close()
            conn.close()
            return 'OK resource deleted'

        else:
            response = Response(resp.text)
            response.headers['Content-Type'] = 'application/xml'
        print("response H: ", response.headers)
        return response
    print("###############################################")


@app.route('/proxy/login', methods=['GET', 'POST', 'OPTIONS'])
def login():
    if request.method == "POST":
        app.logger.debug(request.data)
        _username = json.loads(request.data.decode("utf-8")).get("username") #bytes -> str -> dict
        _password = json.loads(request.data.decode("utf-8")).get("password")

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall() 
 
 
        if len(data) > 0:
            if check_password_hash(str(data[0][2]),_password):
                return 'login success'
            else:
                return 'wrong password'
        else:
            return 'no such user'
    else: 
        return 'sth'

@app.route('/proxy/signup', methods=['GET', 'POST', 'OPTIONS'])
def signup():
    if request.method == "POST":
        app.logger.debug(request.data)
        #get token + discard token + signing up 

        #signing up
        try:
            _username = json.loads(request.data.decode("utf-8")).get("username")
            _password = json.loads(request.data.decode("utf-8")).get("password")
            _pw_hash = generate_password_hash(_password)
            _type = json.loads(request.data.decode("utf-8")).get("type")
            _webdavServer = json.loads(request.data.decode("utf-8")).get("webdavServer")
         
            # validate the received values
            if _username and _password and _type:
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.callproc('sp_createUser',(_username,_pw_hash, _type, _webdavServer))
                data = cursor.fetchall()               
                if len(data) is 0:
                    conn.commit()
                    return "signup success"
                else:
                    return "user already exists"
                cursor.close() 
                conn.close()
        
        except Exception as e:
            return json.dumps({'error':str(e)})
        #finally:
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
        #store this token in the database with type (B or C)  
        return token
    else: 
        return 'sth'

@app.route('/index')
def index():
    app.logger.debug("looking for home page")
    return redirect(url_for('static', filename='startbootstrap-stylish-portfolio-1.0.4/index.html'))


if __name__ == '__main__':
    app.run(debug = True)