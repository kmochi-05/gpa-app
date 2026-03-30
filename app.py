from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect('database.db')


@app.route('/')
def index():
    conn = get_db()

    # ソート機能
    sort = request.args.get('sort')
    if sort == "score":
        subjects = conn.execute("SELECT * FROM subjects ORDER BY score DESC").fetchall()
    elif sort == "credits":
        subjects = conn.execute("SELECT * FROM subjects ORDER BY credits DESC").fetchall()
    else:
        subjects = conn.execute("SELECT * FROM subjects").fetchall()

    conn.close()

    # 計算処理

    total_credits = sum(s[2] for s in subjects)

    # 加重平均
    total_score = sum(s[4] * s[2] for s in subjects)
    avg_score = total_score / total_credits if total_credits > 0 else 0

    # 卒業要件チェック 

    def sum_by(field_name, value):
        return sum(s[2] for s in subjects if s[field_name] == value)

    # field列（科目分類）
    liberal = sum(s[2] for s in subjects if s[7] == "教養・人文社会")
    global_edu = sum(s[2] for s in subjects if s[7] == "教養・グローバル")
    english = sum(s[2] for s in subjects if s[7] == "英語")
    foreign = sum(s[2] for s in subjects if s[7] == "初修外国語")
    basic_must = sum(s[2] for s in subjects if s[7] == "基礎必修")
    basic_select = sum(s[2] for s in subjects if s[7] == "基礎選択必修")
    it = sum(s[2] for s in subjects if s[7] == "情報技術者")
    major_must = sum(s[2] for s in subjects if s[7] == "専門必修")
    major_select = sum(s[2] for s in subjects if s[7] == "専門選択必修")

    language_total = english + foreign

    # 条件チェック
    grad_ok = total_credits >= 124
    conds = {
        "教養人文": liberal >= 6,
        "グローバル": global_edu >= 4,
        "英語": english >= 4,
        "初修外国語": foreign >= 2,
        "言語合計": language_total >= 8,
        "基礎必修": basic_must >= 36,
        "基礎選択必修": basic_select >= 2,
        "IT": it >= 2,
        "専門必修": major_must >= 32,
        "専門選択必修": major_select >= 16
    }

    return render_template("index.html",
                           subjects=subjects,
                           total_credits=total_credits,
                           avg_score=avg_score,
                           grad_ok=grad_ok,
                           conds=conds)


@app.route('/add', methods=['POST'])
def add():
    data = request.form

    conn = get_db()
    conn.execute("""
    INSERT INTO subjects
    (name, credits, gpa, score, term, category, field)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data['name'],
        int(data['credits']),
        float(data['gpa']),
        int(data['score']),
        data['term'],
        data['category'],
        data['field']
    ))

    conn.commit()
    conn.close()

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)