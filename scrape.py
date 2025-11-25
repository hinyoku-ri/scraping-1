import requests
from bs4 import BeautifulSoup
import sqlite3
import time

url = "https://github.com/torvalds?tab=repositories"

db_name = "repos.db"

try:
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    sql = """
    CREATE TABLE IF NOT EXISTS repos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        language TEXT,
        stars INTEGER
    );
    """
    cur.execute(sql)
    conn.commit()

except sqlite3.Error as e:
    print("DB 接続またはテーブル作成でエラーが発生しました:", e)
    exit()


print("スクレイピングを開始します...\n")

try:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    repo_items = soup.select("li.source")

    for item in repo_items:

        name_tag = item.select_one("a[itemprop='name codeRepository']")
        if name_tag:
            name = name_tag.text.strip()
        else:
            name = ""

        lang_tag = item.select_one("span[itemprop='programmingLanguage']")
        if lang_tag:
            language = lang_tag.text.strip()
        else:
            language = "不明"

        star_tag = item.select_one("a[href$='/stargazers']")
        if star_tag:
            stars_text = star_tag.text.strip().replace(",", "")
        
            try:
                stars = int(stars_text)
            except:
                stars = 0
        else:
            stars = 0

        try:
            sql = "INSERT INTO repos (name, language, stars) VALUES (?, ?, ?);"
            cur.execute(sql, (name, language, stars))
            conn.commit()
            print(name, "を保存しました。")

        except sqlite3.Error as e:
            print("INSERT 時にエラーが発生:", e)

        time.sleep(1)

except requests.exceptions.RequestException as e:
    print("HTTP エラーが発生しました:", e)

finally:
    conn.close()
    print("\n処理が終了しました。")

    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        rows = cur.execute("SELECT name, language, stars FROM repos;").fetchall()

        print("\n--- DB に保存されたデータ ---")
        for r in rows:
            print(r)

    except sqlite3.Error as e:
        print("SELECT 時にエラーが発生:", e)

    finally:
        conn.close()