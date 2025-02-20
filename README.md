# bibleapi
api

# system environment in Development(theoretically supports arm release version)
Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-205-generic x86_64)

# pre-environment python
```
pip install fastapi uvicorn
```
# Install
```
git clone https://github.com/ztj7728/bibleapi.git
```

```
cd bibleapi
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
  "verse": "1",            //value can be 1-5, and value 0 for full output of chapter 1.
  "content": "rev_eng"     //value rev_cn for zh-cn output.
}
```

# feedback
```
{
    "verses": [
        {
            "book_eng": "Genesis",
            "book_cn": "创世记",
            "chapter": 1,
            "verse": 1,
            "content": "In the beginning God created the heavens and the earth."
        }
    ]
}
```

# body:

```
{
  "book_eng": "Genesis",
  "chapters_check": true
}

```
# feedback
```
{
  "book_eng": "Genesis",
  "chapters_number": 50
}
```

# body:

```
{
  "book_eng": "Genesis",
  "chapter": "1",
  "verses_check": true
}

```
# feedback
```
{
  "book_eng": "Genesis",
  "chapter": 1,
  "verses_number": 31
}
```

#
[buymeacoffee](https://buymeacoffee.com/ztj7728)
