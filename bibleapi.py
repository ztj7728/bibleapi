import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# FastAPI 实例
app = FastAPI()

# 定义请求体模型
class BibleRequest(BaseModel):
    book_eng: str = None  # 英文书名
    book_cn: str = None   # 中文书名
    chapter: int = None   # 章数可以为空（针对节数查询时）
    verse: str = None     # 经文数可以为空（针对节数查询时，支持范围）
    content: str = None   # 使用 content 字段来指定版本，如 rev_eng 或 rev_cn 或 cuv_cn
    chapters_check: bool = False  # 是否查询章数
    verses_check: bool = False    # 是否查询节数
    footnotes: bool = False       # 是否查询脚注

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
    book_cn = request.book_cn
    chapter = request.chapter
    verse = request.verse
    content_version = request.content  # 获取内容版本（rev_eng 或 rev_cn 或 cuv_cn）

    # 如果指定了 book_cn，优先使用 book_cn 查找 book_eng
    if book_cn:
        # 根据 book_cn 查找对应的 book_eng
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT DISTINCT book_eng
        FROM bible
        WHERE book_cn = ?;
        """
        cursor.execute(query, (book_cn,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            raise HTTPException(status_code=404, detail="Book not found with the provided book_cn.")

        book_eng = row["book_eng"]  # 将找到的 book_eng 更新为查询的 book_cn 对应的英文书名

    # 查询章数功能
    if request.chapters_check:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT MAX(chapter) as last_chapter
        FROM bible
        WHERE book_eng = ?;
        """
        cursor.execute(query, (book_eng,))
        row = cursor.fetchone()
        conn.close()

        if row is None or row["last_chapter"] is None:
            raise HTTPException(status_code=404, detail="Chapters not found for the book.")
        
        return {"book_eng": book_eng, "chapters_number": row["last_chapter"]}

    # 查询节数功能
    if request.verses_check:
        if chapter is None:
            raise HTTPException(status_code=400, detail="Chapter must be provided when querying for verses.")
        
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT MAX(verse) as last_verse
        FROM bible
        WHERE book_eng = ? AND chapter = ?;
        """
        cursor.execute(query, (book_eng, chapter))
        row = cursor.fetchone()
        conn.close()

        if row is None or row["last_verse"] is None:
            raise HTTPException(status_code=404, detail="Verses not found for the chapter.")
        
        return {"book_eng": book_eng, "chapter": chapter, "verses_number": row["last_verse"]}

    # 如果不是章数或节数查询，继续原有的经文查询功能
    if verse == "0":
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        SELECT book_eng, book_cn, chapter, verse, content_rev_eng, content_rev_cn, content_cuv_cn,
               footnotes_1, footnotes_2, footnotes_3, footnotes_4, footnotes_5, footnotes_6, footnotes_7, footnotes_8,
               footnotes_9, footnotes_10, footnotes_11, footnotes_12
        FROM bible
        WHERE book_eng = ? AND chapter = ?
        ORDER BY id;
        """
        cursor.execute(query, (book_eng, chapter))
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            result = {
                "book_eng": row["book_eng"],
                "book_cn": row["book_cn"],
                "chapter": row["chapter"],  # 确保返回的是数值类型
                "verse": row["verse"]       # 确保返回的是数值类型
            }

            # 根据请求的版本返回不同的内容
            if content_version == "rev_eng":
                result["content"] = row["content_rev_eng"]
            elif content_version == "rev_cn":
                result["content"] = row["content_rev_cn"]
            elif content_version == "cuv_cn":
                result["content"] = row["content_cuv_cn"]
            else:
                result["content"] = "Invalid version specified"

            # 如果 footnotes 为 True，则附加脚注内容
            if request.footnotes:
                footnotes = {}
                for i in range(1, 13):  # 检查 footnotes_1 到 footnotes_12
                    footnote_key = f"footnotes_{i}"
                    footnote_value = row[footnote_key]
                    if footnote_value:
                        footnotes[f"footnotes_{i}"] = footnote_value
                
                # 将脚注添加到返回结果中
                result.update(footnotes)

            results.append(result)

        return {"verses": results}

    # 解析经文范围并返回相应的经文
    verses = parse_verse_range(verse)

    conn = get_db_connection()
    cursor = conn.cursor()

    results = []

    for v in verses:
        query = """
        SELECT book_eng, book_cn, chapter, verse, content_rev_eng, content_rev_cn, content_cuv_cn,
               footnotes_1, footnotes_2, footnotes_3, footnotes_4, footnotes_5, footnotes_6, footnotes_7, footnotes_8,
               footnotes_9, footnotes_10, footnotes_11, footnotes_12
        FROM bible
        WHERE book_eng = ? AND chapter = ? AND verse = ?;
        """
        cursor.execute(query, (book_eng, chapter, v))
        row = cursor.fetchone()

        if row is None:
            results.append({"verse": v, "content": "Verse not found"})
        else:
            result = {
                "book_eng": row["book_eng"],
                "book_cn": row["book_cn"],
                "chapter": row["chapter"],  # 确保返回的是数值类型
                "verse": v                  # 确保返回的是数值类型
            }

            # 根据请求的版本返回不同的内容
            if content_version == "rev_eng":
                result["content"] = row["content_rev_eng"]
            elif content_version == "rev_cn":
                result["content"] = row["content_rev_cn"]
            elif content_version == "cuv_cn":
                result["content"] = row["content_cuv_cn"]
            else:
                result["content"] = "Invalid version specified"

            # 如果 footnotes 为 True，则附加脚注内容
            if request.footnotes:
                footnotes = {}
                for i in range(1, 13):  # 检查 footnotes_1 到 footnotes_12
                    footnote_key = f"footnotes_{i}"
                    footnote_value = row[footnote_key]
                    if footnote_value:
                        footnotes[f"footnotes_{i}"] = footnote_value
                
                # 将脚注添加到返回结果中
                result.update(footnotes)

            results.append(result)

    conn.close()
    
    return {"verses": results}

# 解析经文范围（支持范围解析）
def parse_verse_range(verse: str):
    # 如果是范围格式 (例如 "1-5")
    if '-' in verse:
        start_verse, end_verse = verse.split('-')
        return list(range(int(start_verse), int(end_verse) + 1))
    # 如果是单个节数，直接返回一个列表
    else:
        return [int(verse)]
