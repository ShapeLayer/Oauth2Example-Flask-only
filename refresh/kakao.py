import flask
import urllib.request
import json
import os
import time

app = flask.Flask(__name__)
app.secret_key = 'SECRET_KEY'

kakao_client_id = '57175777b88feeb43fb11aa13f8d87f7'
kakao_client_secret = 'a9A5FpG7FRiOp6jaIX3qUa1Eghrg6j3j'

if os.path.exists('kakao.user.json'):
    user_json = json.loads(open('kakao.user.json', encoding='utf-8').read())
else:
    user_json = {}

def get_user_info(token_json = None):
    if token_json == None:
        token_json = user_json[flask.session['username']]['token_json']
    headers = {
        'User-Agent'    : 'Mozilla/5.0',
        'Authorization' : 'Bearer ' + token_json['access_token']
    }
    profile_exchange = urllib.request.Request(
        'https://kapi.kakao.com/v2/user/me',
        headers = headers
    )
    profile_result =  urllib.request.urlopen(profile_exchange).read().decode('utf-8')
    profile_json = json.loads(profile_result)

    # Save User Data
    user_json[flask.session['username']] = {
        'token_json' : token_json,
        'now' : time.time(),
        'api_id' : profile_json['id'],
        'api_username' : profile_json['properties']['nickname'],
        'api_profile_img' : profile_json['properties']['profile_image']
    }
    with open('kakao.user.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(user_json, sort_keys=True, indent=1))
    return profile_json



@app.route('/', methods=['GET', 'POST'])
def flask_main():
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        flask.session['username'] = username

        data = {
            'client_id' : kakao_client_id,
            'redirect_uri' : 'http://localhost:2500/oauth'
        }
        url = 'https://kauth.kakao.com/oauth/authorize?client_id={}&redirect_uri={}&response_type=code'.format(
            data['client_id'], data['redirect_uri']
        )

        if username in user_json.keys():
            if float(user_json[username]['token_json']['expires_in']) + float(user_json[username]['now']) < time.time():
                data = {
                    'grant_type' : 'refresh_token',
                    'client_id' : kakao_client_id,
                    'client_secret' : kakao_client_secret,
                    'refresh_token' : user_json[username]['token_json']['refresh_token']
                }
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
                    'User-Agent': 'Mozilla/5.0'
                }
                token_exchange = urllib.request.Request(
                    'https://kauth.kakao.com/oauth/token',
                    data = bytes(urllib.parse.urlencode(data).encode()),
                    headers = headers
                )
                token_result = urllib.request.urlopen(token_exchange).read()
                token_json = json.loads(token_result)
                user_json[username]['token_json']['access_token'] = token_json['access_token']
                user_json[username]['token_json']['expires_in'] = token_json['expires_in']
                if 'refresh_token' in token_json:
                    user_json[username]['token_json']['refresh_token'] = token_json['expires_in']
                user_json[username]['now'] = time.time()
                return flask.redirect('/oauth?token-alive=true')

            elif float(user_json[username]['token_json']['refresh_token_expires_in']) + float(user_json[username]['now']) < time.time():
                return flask.redirect(url)
            else:
                return flask.redirect('/oauth?token-alive=true')
        else:
            
            return flask.redirect(url)
    
    body = '''
    <form action="" accept-charset="utf-8" method="post">
        <input type="text" name="username" placeholder="username">
        <input type="submit">
    </form>
    '''
    return body

@app.route('/oauth', methods=['GET', 'POST'])
def flask_oauth_callback():
    code = flask.request.args.get('code')
    alive = flask.request.args.get('token-alive')

    if alive != 'true':
        data = {
            'client_id'     : kakao_client_id,
            'client_secret' : kakao_client_secret,
            'grant_type'    : 'authorization_code',
            'redirect_uri'  : 'http://localhost:2500/oauth',
            'code'          : code
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0'
        }
        token_exchange = urllib.request.Request(
            'https://kauth.kakao.com/oauth/token',
            data = bytes(urllib.parse.urlencode(data).encode()),
            headers = headers
        )
        token_result = urllib.request.urlopen(token_exchange).read()
        token_json = json.loads(token_result)
        return str(get_user_info(token_json))

    return str(get_user_info())
    

app.run('localhost', 2500, debug=True)
