from flask import Flask, render_template
import io
import base64
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import pymysql

app = Flask(__name__)

@app.route('/')
def show_graph():
    # 데이터베이스 연결 설정
    connection = pymysql.connect(host='localhost',  # 데이터베이스 서버 주소
                                user='root',  # 데이터베이스 접속 사용자명
                                password='1234',  # 데이터베이스 접속 비밀번호
                                db='diarysys',  # 데이터베이스 이름
                                charset='utf8')  # 문자 인코딩 설정

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

        # 그래프 그리기, 마커는 제거함
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

         # 그래프를 이미지 버퍼로 저장
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        plt.close()  # 열린 그래프 창 자동 닫기
        img.seek(0)
        
        # 이미지를 base64 인코딩하여 HTML에 직접 표시 가능한 문자열로 변환
        plot_url = base64.b64encode(img.getvalue()).decode()
    
    # HTML 템플릿에 데이터를 전달
    return render_template('graph.html', plot_url=plot_url)


if __name__ == '__main__':
    app.run(debug=True)
