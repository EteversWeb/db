from flask import Flask, render_template, request, session, redirect
from werkzeug.security import generate_password_hash
from function import error, login_required
from flask_session import Session
from flask_mysqldb import MySQL
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import pymysql


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "1111"
app.config["MYSQL_DB"] = "new"

mysql = MySQL(app)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        button = request.form["button"]
        if button == "login":
            redirect("/login")
        elif button == "register":
            redirect("register")
        else:
            error("idk")
    else:
        return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if request.form.get("button"):
            # 로그인에 대한 기능
            pass
        if request.form.get("회원가입버튼"):
            # 회원가입에 대한 기능
            pass
        if request.form.get("아이디_비밀번호버튼"):
            # 비밀번호 찾기에 대한 기능
            pass
        return redirect("/mypage")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # db에 업데이트 하는 로직
        # 아이디 중복여부
        # 비밀번호 두개가 일치하는지 여부
        # 전부 확인되면 db에 입력
        pass
    else:
        return render_template("register.html")


@app.route("/deregister", methods=["GET", "POST"])
@login_required
def deregister():
    if request.method == "POST":
        # db에 탈퇴사유 업데이트 하는 로직

        return redirect("/")
    else:
        return render_template("deregister.html")


@app.route("/mypage", methods=["GET", "POST"])
@login_required
def mypage():
    if request.method == "POST":
        if request.form.get("일기작성"):

            pass
    else:
        딕셔너리 = {}
        # db에서 받은 글을 딕셔너리 형태로 저장해서? 올리는 로직
        return render_template("mypage.html", 딕셔너리=딕셔너리)


@app.route("/password-find", methods=["GET", "POST"])
def password_find():
    if request.method == "POST":
        # 폼에서 받는 정보와 db에 있는 정보가 일치하는지 확인 후
        return render_template("password-reset.html")
    else:
        return render_template("password-find.html")


@app.route("/password-reset", methods=["GET", "POST"])
def password_reset():
    if request.method == "POST":
        # db에 비밀번호 업데이트 후 재설정

        return redirect("/")
    else:
        return render_template("password-reset.html")


@app.route("/statistics")
@login_required
def statistics():
    # 데이터베이스 연결 설정
    connection = pymysql.connect(host='localhost',  # 데이터베이스 서버 주소
                                user='root',  # 데이터베이스 접속 사용자명
                                password='1234',  # 데이터베이스 접속 비밀번호
                                db='diarysys',  # 데이터베이스 이름
                                charset='utf8')  # 문자 인코딩 설정

    try:
        # SQL 쿼리 실행을 위한 커서 생성
        with connection.cursor() as cursor:
            # 실행할 쿼리 작성
            sql = "SELECT feeling_date, feeling FROM feeling"
            cursor.execute(sql)
            
            # 결과를 가져와서 DataFrame 객체로 변환
            result = cursor.fetchall()
            df = pd.DataFrame(result, columns=['date', 'feeling'])
            
            # 'date' 컬럼을 datetime 형식으로 변환
            # 날짜 형식이 'YYYYMMDDHH'인 경우 아래와 같이 format을 지정합니다.
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d%H')

        # 원본 데이터를 기반으로 보간 함수 생성
        f = interp1d(df['date'].astype(np.int64), df['feeling'], kind='cubic')

        # 더 많은 포인트를 생성하여 부드러운 곡선을 그리기 위한 x값 준비
        xnew = np.linspace(df['date'].astype(np.int64).min(), df['date'].astype(np.int64).max(), 1000)

        # 보간 함수를 사용하여 y값 생성
        ynew = f(xnew)

        # 그래프 그리기, 마커는 제거
        plt.plot(xnew.astype('datetime64[ns]'), ynew, '-')

        plt.xlabel('date')
        plt.ylabel('feeling')
        plt.title('Feeling', fontsize=16)

        # y축 눈금과 레이블을 사용자 정의 값으로 설정
        plt.yticks([-2, -1, 0, 1, 2], ['very bad', 'bad', 'normal', 'good', 'very good'])

        # 0을 기준으로 하는 x 축 표현
        plt.axhline(0, color='black', linewidth=0.8)

        # 그래프 테두리 제거
        for spine in plt.gca().spines.values():
            spine.set_visible(False)

        plt.gcf().autofmt_xdate()

        fig, ax = plt.subplots()
        ax.plot(...)  # 그래프 그리기 코드
        plt.tight_layout()
        image_path = 'static/images/statistics.png'  # 저장할 경로와 파일명
        plt.savefig(image_path)
        plt.close(fig) 

    finally:
        # 데이터베이스 연결 종료
        connection.close()

    return render_template("statistics.html", image_path=image_path)


@app.route("/read-post", methods=["GET", "POST"])
@login_required
def read_post():

    if request.method == "POST":
        current_diary_id = request.form["button"]
    else:
        current_diary_id = request.form["diary_id"]

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT diary_id, diary_title, diary_cont, diray_date FROM diary WHERE user_id = ? ORDER BY diary_id;",
        session["user_email"],
    )
    diary_list = cur.fetchall()
    cur.close()
    diary = {}
    prev_diary_id, next_diary_id = 0, 0

    for diary_id, diary_title, diary_cont, diary_date in diary_list:
        if diary_id < current_diary_id:
            prev_diary_id = diary_id
        elif current_diary_id < diary_id:
            next_diary_id = diary_id
            break
        else:
            diary["title"] = diary_title
            diary["cont"] = diary_cont
            diary["date"] = diary_date

    return render_template(
        "read-post.html",
        prev_diary_id=prev_diary_id,
        next_diary_id=next_diary_id,
        diary=diary,
    )


@app.route("/write-post", methods=["GET", "POST"])
@login_required
def write_post():
    # 글의 정보를 받아서 포스
    if request.method == "POST":

        title = request.form["title"]
        content = request.form["content"]

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO 'diary' (diary_title, diary_cont, user_id, diray_date) VALUES (?, ?, ?, NOW())",
            title,
            content,
            session["user_email"],
        )
        mysql.connection.commit()
        cur.close()

        return redirect("/mypage")
    else:
        return render_template("write-post.html")
