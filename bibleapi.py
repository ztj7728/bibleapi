import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# FastAPI 实例
app = FastAPI()

# 定义请求体模型
class BibleRequest(BaseModel):
    book_eng: str
    chapter: str
    verse: str
    content: str  # 使用 content 字段来指定版本，如 rev_eng 或 rev_cn

# 创建与 SQLite 数据库的连接
def get_db_connection():
    conn = sqlite3.connect('output.db')  # 这里请使用你的数据库路径
    conn.row_factory = sqlite3.Row  # 使得查询结果能够按列名访问
    return conn

# 定义API路由
@app.post("/get_verse/")
async def get_bible_verse(request: BibleRequest):
    # 获取传入的数据
    book_eng = request.book_eng
    chapter = request.chapter
    verse = request.verse
    content_version = request.content  # 获取内容版本（rev_eng 或 rev_cn）

    # 查询数据库
    conn = get_db_connection()
    cursor = conn.cursor()

    # 根据输入的书卷名、章节、经文和圣经版本进行查询
    query = """
    SELECT content_rev_eng, content_rev_cn 
    FROM bible 
    WHERE book_eng = ? AND chapter = ? AND verse = ?;
    """
    cursor.execute(query, (book_eng, chapter, verse))

    # 获取查询结果
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Verse not found")
    
    # 根据版本返回对应内容
    if content_version == "rev_eng":
        return {"content": row["content_rev_eng"]}
    elif content_version == "rev_cn":
        return {"content": row["content_rev_cn"]}
    else:
        raise HTTPException(status_code=400, detail="Invalid version specified")

