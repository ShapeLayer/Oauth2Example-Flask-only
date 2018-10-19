import flask
import urllib.request
import json

app = flask.Flask(__name__)
app.secret_key = 'SECRET_KEY'

naver_client_id = ''
naver_client_secret = ''
state = 'non_blocking'

@app.route('/', methods=['GET', 'POST'])
def flask_main():
    data = {
        'client_id' : naver_client_id,
        'redirect_uri' : 'http://localhost:2500/oauth',
        'state' : state
    }
    return flask.redirect('https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={}&redirect_uri={}&state={}'.format(
        data['client_id'], data['redirect_uri'], data['state']
    ))

@app.route('/oauth', methods=['GET', 'POST'])
def flask_oauth_callback():
    code = flask.request.args.get('code')
    state = flask.request.args.get('state')
    data = {
        'client_id' : naver_client_id,
        'client_secret' : naver_client_secret,
        'code' : code
    }
    token_access = 'https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={}&client_secret={}&code={}&state={}'.format(
        data['client_id'], data['client_secret'], data['code'], state
    )
    token_result = urllib.request.urlopen(token_access).read().decode('utf-8')
    token_result_json = json.loads(token_result)

    headers = {'Authorization': 'Bearer {}'.format(token_result_json['access_token'])}
    profile_access = urllib.request.Request('https://openapi.naver.com/v1/nid/me', headers = headers)
    profile_result = urllib.request.urlopen(profile_access).read().decode('utf-8')
    profile_result_json = json.loads(profile_result)
    return str(profile_result_json)
    

app.run('localhost', 2500, debug=True)
