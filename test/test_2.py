import json

from flask import jsonify
from requests import get, post, delete

# get requests
print(get('http://localhost:8080/api/v2/news').json())
print(get('http://localhost:8080/api/v2/news/1').json())

# post requests

print(post('http://localhost:8080/api/v2/news', json={'title':'fdasdf', 'content':'dafds', 'is_private':'False', 'is_published':'True', 'user_id' : '1'}).json())
print(post('http://localhost:8080/api/v2/news/1', json=json.dumps({'title':'fdasdf', 'content':'dafds'})).json())



print(delete('http://localhost:8080/api/v2/news/').json())
print(delete('http://localhost:8080/api/v2/news/1').json())