import flask
import urllib.request
import json

app = flask.Flask(__name__)
app.secret_key = 'SECRET_KEY'

facebook_client_id = '238625080166727'
facebook_client_secret = '8408d32248547292a9cdb48f3f2bc275'
state = 'non_blocking'

@app.route('/', methods=['GET', 'POST'])
def flask_main():
    data = {
        'client_id' : facebook_client_id,
        'redirect_uri' : 'http://localhost:2500/oauth',
        'state' : state
    }
    return flask.redirect('https://www.facebook.com/v3.1/dialog/oauth?client_id={}&redirect_uri={}&state={}'.format(
        data['client_id'], data['redirect_uri'], data['state']
    ))

@app.route('/oauth', methods=['GET', 'POST'])
def flask_oauth_callback():
    code = flask.request.args.get('code')
    state = flask.request.args.get('state')
    data = {
        'client_id' : facebook_client_id,
        'redirect_uri' : 'http://localhost:2500/oauth',
        'client_secret' : facebook_client_secret,
        'code' : code
    }
    target = 'https://graph.facebook.com/v3.1/oauth/access_token?client_id={}&redirect_uri={}&client_secret={}&code={}'.format(
        data['client_id'], data['redirect_uri'], data['client_secret'], data['code']
    )
    data_profile = '' #https://developers.facebook.com/docs/messenger-platform/identity/user-profile/?translation
    result = urllib.request.urlopen(target).read().decode('utf-8')
    result_json = json.loads(result)
    return result
    

app.run('localhost', 2500, debug=True)