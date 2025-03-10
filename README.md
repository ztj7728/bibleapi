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


# body:

```
{
  "search_text": "神爱世人",
  "content": "rev_cn",
  "footnotes": true
}

```
# feedback
```
{
    "message": "Found 1 matching verses",
    "search_text": "神爱世人",
    "verses": [
        {
            "book_eng": "John",
            "book_cn": "约翰福音",
            "chapter": 3,
            "verse": 16,
            "content": "¹神爱²世人，甚至将祂的独生子赐给他们，叫一切³信入祂的，不至灭亡，反得永远的生命。",
            "reference": "约翰福音 3:16",
            "score": 11,
            "footnotes_1": "直译，神是这样的爱世人。",
            "footnotes_2": "世人，原文与世界同字，指犯罪堕落而构成世界的人，不只有罪，且有古蛇魔鬼的毒素，成为他的蛇类，需要基督以蛇形替他们死，为他们受神审判，（14，）否则他们就必灭亡。（16。）世人虽这样堕落，但因他们是神照自己的形像，为盛装祂而造的器皿，（创一26，罗九21上，23，）神仍然以祂神圣的爱，就是祂自己，（约壹四8，16，）极其的爱他们，甚至将祂的独生子（就是祂的彰显）赐给他们，好叫他们得着祂永远的生命，成为祂的众子，作祂团体的彰显，以完成祂新约永远的经纶。因此，神就先借着祂的灵重生他们，（3～6，）叫他们有祂永远的生命，（15～16，36上，）再用祂无限量的灵充满他们，（34，）使他们成为祂那在万有之上，包罗万有之基督（31～35）的新妇，作祂的扩增和丰满。（28～30。）",
            "footnotes_3": "信入主与信主（六30）不同。信主乃是信祂是真的，是实的；信入主乃是接受祂，与祂联合为一。前者是客观的承认一个事实；后者是主观的接受一个生命。"
        }
    ]
}
```

#
[buymeacoffee](https://buymeacoffee.com/ztj7728)
