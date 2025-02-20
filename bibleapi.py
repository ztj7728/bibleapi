import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# FastAPI 实例
app = FastAPI()

# 定义请求体模型
class BibleRequest(BaseModel):
    book_eng: str
    chapter: str
    verse: str  # 这里接受单个或范围的经文
    content: str  # 使用 content 字段来指定版本，如 rev_eng 或 rev_cn

# 创建与 SQLite 数据库的连接
def get_db_connection():
    conn = sqlite3.connect('output.db')  # 这里请使用你的数据库路径
    conn.row_factory = sqlite3.Row  # 使得查询结果能够按列名访问
    return conn

# 解析经文范围
def parse_verse_range(verse: str):
    if '-' in verse:
        start_verse, end_verse = verse.split('-')
        return list(range(int(start_verse), int(end_verse) + 1))
    else:
        return [int(verse)]

# 定义API路由
@app.post("/get_verse/")
async def get_bible_verse(request: BibleRequest):
    # 获取传入的数据
    book_eng = request.book_eng
    chapter = request.chapter
    verse = request.verse
    content_version = request.content  # 获取内容版本（rev_eng 或 rev_cn）

    # 如果 verse 是 "0"，返回整个章节的所有经文
    if verse == "0":
        # 创建数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询整个章节的所有经文
        query = """
        SELECT verse, content_rev_eng, content_rev_cn
        FROM bible
        WHERE book_eng = ? AND chapter = ?
        ORDER BY id;
        """
        cursor.execute(query, (book_eng, chapter))
        rows = cursor.fetchall()
        conn.close()

        # 构建返回结果
        results = []
        for row in rows:
            if content_version == "rev_eng":
                results.append({"verse": row["verse"], "content": row["content_rev_eng"]})
            elif content_version == "rev_cn":
                results.append({"verse": row["verse"], "content": row["content_rev_cn"]})
            else:
                results.append({"verse": row["verse"], "content": "Invalid version specified"})

        return {"verses": results}

    # 否则按照之前的方式解析和返回指定的节数
    verses = parse_verse_range(verse)

    # 创建数据库连接
    conn = get_db_connection()
    cursor = conn.cursor()

    # 结果列表
    results = []

    # 遍历每个节数进行查询
    for v in verses:
        query = """
        SELECT content_rev_eng, content_rev_cn
        FROM bible
        WHERE book_eng = ? AND chapter = ? AND verse = ?;
        """
        cursor.execute(query, (book_eng, chapter, str(v)))
        row = cursor.fetchone()

        if row is None:
            results.append({"verse": str(v), "content": "Verse not found"})
        else:
            if content_version == "rev_eng":
                results.append({"verse": str(v), "content": row["content_rev_eng"]})
            elif content_version == "rev_cn":
                results.append({"verse": str(v), "content": row["content_rev_cn"]})
            else:
                results.append({"verse": str(v), "content": "Invalid version specified"})

    conn.close()
    
    return {"verses": results}
