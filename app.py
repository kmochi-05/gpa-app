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
    others = sum(s[2] for s in subjects if s[7] == "その他")

    humanities_total = liberal + global_edu
    language_total = english + foreign

    # 条件チェック
    grad_ok = total_credits >= 124
    conds = [
        {"name": "教養・人文社会", "current": liberal, "required": 6, "ok": liberal >= 6, "type": "normal"},
        {"name": "教養・グローバル", "current": global_edu, "required": 4, "ok": global_edu >= 4, "type": "normal"},

        {"name": "教養教育科目合計", "current": humanities_total, "required": 10, "ok": humanities_total >= 10, "type": "total"},

        {"name": "英語", "current": english, "required": 6, "ok": english >= 6, "type": "normal"},
        {"name": "初修外国語", "current": foreign, "required": 2, "ok": foreign >= 2, "type": "normal"},

        {"name": "言語合計", "current": language_total, "required": 10, "ok": language_total >= 10, "type": "total"},

        {"name": "基礎必修", "current": basic_must, "required": 36, "ok": basic_must >= 36, "type": "normal"},
        {"name": "基礎選択必修", "current": basic_select, "required": 2, "ok": basic_select >= 2, "type": "normal"},
        {"name": "情報技術者", "current": it, "required": 2, "ok": it >= 2, "type": "normal"},
        {"name": "専門必修", "current": major_must, "required": 32, "ok": major_must >= 32, "type": "normal"},
        {"name": "専門選択必修", "current": major_select, "required": 16, "ok": major_select >= 16, "type": "normal"},

       {"name": "その他", "current": others, "required": 0, "ok": True, "type": "other"}
    ]

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

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM subjects WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)