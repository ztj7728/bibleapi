# bibleapi
api

# system environment in Development(theoretically supports arm release version)
Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-205-generic x86_64)

# pre-environment python
```
pip install fastapi uvicorn
```

# run
```
uvicorn bibleapi:app --reload
```

# run in background
```
nohup uvicorn bibleapi:app > output.log 2>&1 &
```

# use

POST http://127.0.0.1:8000/get_verse/

headers:
```
Content-Type: application/json
```

body:
```
{
  "book_eng": "Genesis",
  "chapter": "1",
  "verse": "1",//value can be 1-5, and value 0 for full out put of chapter 1.
  "content": "rev_eng"
}
```

# feedback
```
{
  "content": "In the beginning God created the heavens and the earth."
}
```
#
[buymeacoffee](https://buymeacoffee.com/ztj7728)
