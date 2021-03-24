from requests import get, post, delete

print(get('http://localhost:5000/api/v2/news/').json())
print(delete('http://localhost:5000/api/v2/news/').json())
# новости с id = 999 нет в базе

print(delete('http://localhost:5000/api/v2/news/<int:news_id>').json())