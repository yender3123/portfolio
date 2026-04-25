from flask import Flask, url_for, render_template, request, redirect
from werkzeug.utils import secure_filename
import sqlite3
import uuid
import requests

app = Flask(__name__)

connection = sqlite3.connect("sqlite.db", check_same_thread=False)
cursor = connection.cursor()


# Инициализация базы данных (закомментировано после первого запуска)
# cursor.execute('''
#     CREATE TABLE portfolios (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         uuid TEXT NOT NULL,
#         name TEXT NOT NULL,
#         bio TEXT NOT NULL,
#         github TEXT NOT NULL,
#         telegram TEXT NOT NULL,
#         avatar TEXT NOT NULL,
#         skills TEXT NOT NULL)''')
# connection.commit()

@app.route("/")
def index():
    cursor.execute('SELECT * FROM portfolios')
    result = cursor.fetchall()
    portfolios = []
    for portfolio in reversed(result):
        portfolios.append({
            'id': portfolio[0],
            'uuid': portfolio[1],
            'name': portfolio[2],
            'bio': portfolio[3],
            'github': portfolio[4],
            'telegram': portfolio[5],
            'avatar': portfolio[6],
            'skills': portfolio[7],
            'tools': portfolio[8]
        })
    context = {'portfolios': portfolios}
    return render_template("all_portfolios.html", **context)


@app.route("/form")
def form():
    return render_template("form.html")


@app.route('/generate', methods=['POST'])
def generate():
    formData = request.form
    name = formData['name']
    bio = formData['bio']
    github = formData['github'].strip().replace('https://github.com/', '').replace('/', '')
    telegram = formData['telegram']
    skills = formData['skills']
    avatar = request.files.get('avatar')
    uid = str(uuid.uuid4())
    avatar_filename = ""
    tools = formData["tools"]

    if avatar and avatar.filename:
        filename = secure_filename(f"{uid}_{avatar.filename}")
        avatar_path = f"static/uploads/{filename}"
        avatar.save(avatar_path)
        avatar_filename = avatar_path.replace("static/", "")

    cursor.execute(
        'INSERT INTO portfolios (uuid, name, bio, github, telegram, avatar, skills, tools) VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
        (uid, name, bio, github, telegram, avatar_filename, skills, tools)
    )
    connection.commit()
    return redirect(url_for('index'))


@app.route('/portfolio/<uuid>')
def view_portfolio(uuid):
    cursor.execute('SELECT * FROM portfolios WHERE uuid = ?', (uuid,))
    result = cursor.fetchall()
    tools = []
    if len(result) == 0:
        return "Портфолио не найдено", 404
    for tool in result[0][8].split(","):
        if "C++" in tool.upper():
            tools.append('🎨C++')
        elif 'PYTHON' in tool.upper():
            tools.append('🐍Python')
        elif 'HTML' in tool.upper():
            tools.append('📄HTML')
        elif 'GIT' in tool.upper():
            tools.append('🔧Git')
        elif 'GITHUB' in tool.upper():
            tools.append('🐙GitHub')
        elif 'TELEGRAM' in tool.upper():
            tools.append('🗣telegram')
        else:
            tools.append(tool)
    skills = []
    for skill in result[0][7].split(","):
        if 'C++' in skill.upper():
            skills.append('🎨C++')
        elif 'ИИ' in skill.upper():
            skills.append('ИИ')
    portfolio = {
        'id': result[0][0],
        'uuid': result[0][1],
        'name': result[0][2],
        'bio': result[0][3],
        'github': result[0][4],
        'telegram': result[0][5],
        'avatar': result[0][6],
        'skills': result[0][7].split(","),
        'tools': tools
    }



    projects = []
    github_username = portfolio['github']

    if github_username:
        try:
            url = f"https://api.github.com/users/{github_username}/repos"
            response = requests.get(url)

            if response.status_code == 200:
                repos = response.json()
                for repo in repos[:6]:
                    projects.append({
                        'title': repo.get('name', 'Без названия'),
                        'description': repo.get('description', 'Без описания') or 'Без описания',
                        'link': repo.get('html_url', '#')
                    })
            else:
                projects = []
        except Exception as e:
            print(f"Ошибка при получении данных из GitHub: {e}")
            projects = []
    print(projects)
    context = {
        'portfolio': portfolio,
        'projects': projects
    }

    return render_template("portfolio_template.html", **context)


if __name__ == '__main__':
    app.run(debug=True)