from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysite'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql://{user}:{password}@{host}/{db_name}?charset=utf8'.format(**{
    'user': "todo_user",
    'password': "MySQL_DB_Pass",
    'host': "localhost",
    'db_name': "ToDo_DB"
    })
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)

# Userテーブルの定義
class User(db.Model):
    __tablename__ = 'users' #テーブル名の設定
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True) #カラムの定義

    def __init__(self, username):
        self.username = username

#データベースに書き込むためのロジック
@app.route('/', methods=['GET', 'POST'])
def write_db():
    #POSTリクエストの場合
    if request.method == 'POST':
        username = request.form.get('username') #入力された項目を取得する
        user = User(
            username = username
            )                       #取得した項目をデータベースのカラム名に紐付ける
        
        #データベースへの書き込みを行う
        try:
            with db.session.begin(subtransactions=True): #データベースの接続を開始
                db.session.add(user)    #データベースに書き込むデータを用意する
            db.session.commit()     #データベースへの書き込みを実行する
        except:     #書き込みがうまくいかない場合
            db.session.rollback()       #ロールバック処理
            raise
        finally:        #データベースとの接続を終了する
            db.session.close()
        return redirect(url_for('read_db'))     #成功したらread_dbに遷移する
    return render_template('insert.html')

#データベースから読み込むためのロジック
@app.route('/read_db')
def read_db():
    users = db.session.query(User).order_by(User.id.desc()).first()     #Userテーブルのidを降順で並べて一番最初のデータを取得する
    return render_template('user.html', users=users) #user.htmlにusersデータを渡すために引数で設定している

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
