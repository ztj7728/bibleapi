import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

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
    search_text: str = None       # 新增：用于模糊搜索的文本

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
    search_text = request.search_text  # 获取搜索文本

    # 如果提供了搜索文本，执行模糊搜索
    if search_text:
        return await search_bible_text(search_text, content_version, request.footnotes)

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

# 新增：模糊搜索圣经经文的函数
async def search_bible_text(search_text: str, content_version: str = "rev_cn", include_footnotes: bool = False):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 确定要搜索的内容列
    content_column = "content_rev_cn"  # 默认搜索中文恢复本
    if content_version == "rev_eng":
        content_column = "content_rev_eng"
    elif content_version == "cuv_cn":
        content_column = "content_cuv_cn"
    
    # 使用正则表达式移除搜索文本中可能存在的上标字符
    clean_search_text = re.sub(r'[¹²³⁴⁵⁶⁷⁸⁹⁰]', '', search_text)
    
    # 构建搜索条件：使用递归替换处理所有可能的上标组合
    search_terms = clean_search_text.split()
    conditions = []
    params = []
    
    for term in search_terms:
        # 创建一个基本的模糊匹配条件
        # 使用递归替换的方式处理文本中的上标
        condition = f"""
        {content_column} LIKE ? OR
        REPLACE(
            REPLACE(
                REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(
                                    REPLACE(
                                        REPLACE(
                                            REPLACE(
                                                {content_column},
                                                '¹', ''
                                            ),
                                            '²', ''
                                        ),
                                        '³', ''
                                    ),
                                    '⁴', ''
                                ),
                                '⁵', ''
                            ),
                            '⁶', ''
                        ),
                        '⁷', ''
                    ),
                    '⁸', ''
                ),
                '⁹', ''
            ),
            '⁰', ''
        ) LIKE ?
        """
        
        # 添加两个参数：一个用于原始匹配，一个用于移除所有上标后的匹配
        params.extend([f'%{term}%', f'%{term}%'])
        conditions.append(f"({condition})")
    
    # 组合所有搜索词的条件（使用AND连接，表示所有词都必须匹配）
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
    SELECT book_eng, book_cn, chapter, verse, {content_column} as content,
           footnotes_1, footnotes_2, footnotes_3, footnotes_4, footnotes_5, footnotes_6, 
           footnotes_7, footnotes_8, footnotes_9, footnotes_10, footnotes_11, footnotes_12
    FROM bible
    WHERE {where_clause}
    ORDER BY book_eng, chapter, verse
    LIMIT 100;  -- 限制结果数量，避免返回过多数据
    """
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return {"message": "No matching verses found", "verses": []}
    
    # 对结果进行相关性排序
    results = []
    for row in rows:
        content = row["content"]
        # 计算匹配分数（简单实现：完全匹配的排在前面）
        score = 1
        clean_content = re.sub(r'[¹²³⁴⁵⁶⁷⁸⁹⁰]', '', content)
        if clean_search_text in clean_content:
            score += 10  # 完全匹配加分
        
        result = {
            "book_eng": row["book_eng"],
            "book_cn": row["book_cn"],
            "chapter": row["chapter"],
            "verse": row["verse"],
            "content": content,
            "reference": f"{row['book_cn']} {row['chapter']}:{row['verse']}",
            "score": score
        }
        
        # 如果需要包含脚注
        if include_footnotes:
            footnotes = {}
            for i in range(1, 13):
                footnote_key = f"footnotes_{i}"
                footnote_value = row[footnote_key]
                if footnote_value:
                    footnotes[footnote_key] = footnote_value
            
            if footnotes:
                result.update(footnotes)
        
        results.append(result)
    
    # 按相关性分数排序
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "message": f"Found {len(results)} matching verses",
        "search_text": search_text,
        "verses": results
    }

# 新增：单独的搜索路由，方便直接通过 GET 请求进行搜索
@app.get("/search/")
async def search_bible(
    search_text: str, 
    version: str = "rev_cn", 
    footnotes: bool = False
):
    return await search_bible_text(search_text, version, footnotes)
