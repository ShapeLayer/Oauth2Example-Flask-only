import flask
import urllib.request
import json

app = flask.Flask(__name__)
app.secret_key = 'SECRET_KEY'

discord_client_id = '547016401747968000'
discord_client_secret = 'd4ky295tkdZUOFG-SaBjSrk4Psd9Yvw0'

@app.route('/', methods=['GET', 'POST'])
def flask_main():
    data = {
        'client_id' : discord_client_id,
        'redirect_uri' : 'http://localhost:2500/oauth'
    }
    return flask.redirect('https://discordapp.com/api/oauth2/authorize?client_id={}&redirect_uri={}&response_type=code&scope=identify'.format(
        data['client_id'], data['redirect_uri']
    ))

@app.route('/oauth', methods=['GET', 'POST'])
def flask_oauth_callback():
    code = flask.request.args.get('code')

    data = {
        'client_id'     : discord_client_id,
        'client_secret' : discord_client_secret,
        'grant_type'    : 'authorization_code',
        'redirect_uri'  : 'http://localhost:2500/oauth',
        'scope'         : 'identify',
        'code'          : code
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0'
    }
    token_exchange = urllib.request.Request(
        'https://discordapp.com/api/oauth2/token',
        data = bytes(urllib.parse.urlencode(data).encode()),
        headers = headers
    )
    token_result = urllib.request.urlopen(token_exchange).read()
    token_json = json.loads(token_result)

    headers = {
        'User-Agent'    : 'Mozilla/5.0',
        'Authorization' : 'Bearer ' + token_json['access_token']
    }
    profile_exchange = urllib.request.Request(
        'https://discordapp.com/api/users/@me',
        headers = headers
    )
    profile_result =  urllib.request.urlopen(profile_exchange).read().decode('utf-8')
    profile_json = json.loads(profile_result)
    return str(profile_json)
    

app.run('localhost', 2500, debug=True)
