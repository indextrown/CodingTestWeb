from flask import Flask, redirect, url_for, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import click
from flask.cli import with_appcontext
import docker
import tempfile
import os
from flask_migrate import Migrate
import json
import time
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import sys
from io import StringIO
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # 실제 운영 시 안전한 키로 변경하세요
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///codingtest.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

try:
    docker_client = docker.from_env()
except docker.errors.DockerException as e:
    print(f"Docker 연결 중 오류 발생: {e}")
    docker_client = None

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    submissions = db.relationship('Submission', backref='user', lazy=True)

class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    time_limit = db.Column(db.Float, nullable=False)
    memory_limit = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    input_description = db.Column(db.Text, nullable=False)
    output_description = db.Column(db.Text, nullable=False)
    input_format = db.Column(db.Text, nullable=False)
    output_format = db.Column(db.Text, nullable=False)
    example_input = db.Column(db.Text, nullable=False)
    example_output = db.Column(db.Text, nullable=False)
    test_cases = db.Column(db.Text, nullable=False)
    submissions = db.Column(db.Integer, default=0)
    correct_submissions = db.Column(db.Integer, default=0)
    supported_languages = db.Column(db.String(100), nullable=False, default='python,c,cpp,java,swift')

    problem_submissions = db.relationship('Submission', backref='problem', lazy=True)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    passed = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    language = db.Column(db.String(100), nullable=False)

    # problem relationship is not defined here

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('이미 존재하는 사용자명입니다.', 'error')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        
        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('로그인 성공!', 'success')
            return redirect(url_for('dashboard'))
        flash('잘못된 사용자명 또는 비밀번호입니다.', 'error')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    problems = Problem.query.all()
    user_submissions = {s.problem_id: s.passed for s in current_user.submissions}
    return render_template('dashboard.html', problems=problems, user_submissions=user_submissions)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/problem/<int:problem_id>')
@login_required
def problem(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    return render_template('problem.html', problem=problem)

@app.route('/problem/<int:problem_id>/submit', methods=['POST'])
@login_required
def submit(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    user_code = request.form['code']
    language = request.form['language']
    test_cases = json.loads(problem.test_cases)
    test_results = []

    docker_images = {
        'python': 'python:3.9-slim',
        'c': 'gcc:latest',
        'cpp': 'gcc:latest',
        'java': 'openjdk:latest',
        'swift': 'swift:latest'
    }

    file_names = {
        'python': 'source.py',
        'c': 'source.c',
        'cpp': 'source.cpp',
        'java': 'Main.java',
        'swift': 'source.swift'
    }

    compile_commands = {
        'python': None,
        'c': 'gcc -o /app/program /app/source.c',
        'cpp': 'g++ -o /app/program /app/source.cpp',
        'java': 'javac /app/Main.java',
        'swift': 'swiftc -o /app/program /app/source.swift'
    }

    run_commands = {
        'python': 'python /app/source.py',
        'c': '/app/program',
        'cpp': '/app/program',
        'java': 'java -cp /app Main',
        'swift': '/app/program'
    }

    try:
        # 임시 디렉토리 생성
        with tempfile.TemporaryDirectory() as temp_dir:
            # 소스 파일 생성
            source_file_path = os.path.join(temp_dir, file_names[language])
            with open(source_file_path, 'w') as source_file:
                source_file.write(user_code)

            app.logger.info(f"임시 파일 경로: {source_file_path}")

            volumes = {temp_dir: {'bind': '/app', 'mode': 'rw'}}
            
            app.logger.info(f"Docker 볼륨 설정: {volumes}")

            if compile_commands[language]:
                docker_client.containers.run(
                    docker_images[language],
                    command=compile_commands[language],
                    volumes=volumes,
                    working_dir='/app',
                    remove=True
                )

            for test_case in test_cases:
                input_data = test_case['input']
                expected_output = test_case['output'].strip()

                container = docker_client.containers.run(
                    docker_images[language],
                    command=f'sh -c "echo \'{input_data}\' | {run_commands[language]}"',
                    volumes=volumes,
                    working_dir='/app',
                    remove=True,
                    stdout=True,
                    stderr=True
                )

                actual_output = container.decode('utf-8').strip()

                passed = actual_output == expected_output
                test_results.append({
                    'input': input_data,
                    'expected': expected_output,
                    'actual': actual_output,
                    'passed': passed
                })

    except Exception as e:
        app.logger.error(f"제출 처리 중 오류 발생: {str(e)}", exc_info=True)
        return render_template('problem.html', problem=problem, error=str(e)), 500

    all_passed = all(result['passed'] for result in test_results)
    
    submission = Submission(user_id=current_user.id, problem_id=problem_id, passed=all_passed, language=language)
    db.session.add(submission)
    
    if all_passed:
        problem.correct_submissions += 1
    problem.submissions += 1
    db.session.commit()

    return render_template('result.html', problem=problem, test_results=test_results)

def run_code(language, code, input_data):
    if docker_client is None:
        return "Docker 연결 오류"

    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()

    try:
        container = docker_client.containers.run(
            'python:3.9',
            f'python {f.name}',
            volumes={os.path.dirname(f.name): {'bind': '/code', 'mode': 'ro'}},
            working_dir='/code',
            stdin_open=True,
            detach=True,
            remove=True
        )

        container.exec_run(f'echo "{input_data}" > input.txt')
        result = container.exec_run(f'python {os.path.basename(f.name)} < input.txt')
        output = result.output.decode('utf-8')

        container.stop()
    except Exception as e:
        output = f"실행 중 오류 발생: {str(e)}"
    finally:
        os.unlink(f.name)

    return output

def get_file_extension(language):
    extensions = {
        'python': '.py',
        'c': '.c',
        'cpp': '.cpp',
        'java': '.java',
        'swift': '.swift'
    }
    return extensions.get(language, '')

@click.command('init-db')
@with_appcontext
def init_db_command():
    db.create_all()
    
    # 기존 문제가 없을 경우에만 새 문제 추가
    if Problem.query.count() == 0:
        problems = [
            Problem(
                title="A+B",
                difficulty="쉬움",
                time_limit=1.0,
                memory_limit=128,
                description="두 정수 A와 B를 입력받은 다음, A+B를 출력하는 프로그램을 작성하시오.",
                input_description="첫째 줄에 A와 B가 주어진다. (0 < A, B < 10)",
                output_description="첫째 줄에 A+B를 출력한다.",
                input_format="두 정수 A와 B가 공백으로 구분되어 주어집니다.",
                output_format="A+B의 결과를 출력합니다.",
                example_input="1 2",
                example_output="3",
                test_cases='[{"input": "1 2", "output": "3"}, {"input": "5 7", "output": "12"}]'
            ),
            Problem(
                title="A-B",
                difficulty="쉬움",
                time_limit=1.0,
                memory_limit=128,
                description="두 정수 A와 B를 입력받은 다음, A-B를 출력하는 프로그램을 작성��시오.",
                input_description="첫째 줄에 A와 B가 주어진다. (0 < A, B < 100)",
                output_description="첫째 줄에 A-B를 출력한다.",
                input_format="두 정수 A와 B가 공백으로 구분되어 주어집니다.",
                output_format="A-B의 결과를 출력합니다.",
                example_input="3 2",
                example_output="1",
                test_cases='[{"input": "3 2", "output": "1"}, {"input": "5 2", "output": "3"}]'
            ),
            Problem(
                title="A×B",
                difficulty="쉬움",
                time_limit=1.0,
                memory_limit=128,
                description="두 정수 A와 B를 입력받은 다음, A×B를 출력하는 프로그램을 작성하시오.",
                input_description="첫째 줄에 A와 B가 주어진다. (0 < A, B < 10)",
                output_description="첫째 줄에 A×B를 출력한다.",
                input_format="두 정수 A와 B가 공백으로 구분되어 주어집니다.",
                output_format="A×B의 결과를 출력합니다.",
                example_input="3 4",
                example_output="12",
                test_cases='[{"input": "3 4", "output": "12"}, {"input": "5 2", "output": "10"}]'
            ),
            Problem(
                title="A/B",
                difficulty="쉬움",
                time_limit=1.0,
                memory_limit=128,
                description="두 정수 A와 B를 입력받은 다음, A/B를 출력하는 프로그램을 작성하시오.",
                input_description="첫째 줄에 A와 B가 주어진다. (0 < A, B < 10)",
                output_description="첫째 줄에 A/B를 출력한다. 실제 정답과 출력값의 절대오차 또는 상대오차가 10^-9 이하이면 정답이다.",
                input_format="두 정수 A와 B가 공백으로 구분되어 주어집니다.",
                output_format="A/B의 결과 출력합니다. 소수 아래 9자리까지 출력하세요.",
                example_input="1 3",
                example_output="0.333333333",
                test_cases='[{"input": "1 3", "output": "0.333333333"}, {"input": "4 5", "output": "0.800000000"}]'
            )
        ]
        
        db.session.add_all(problems)
        db.session.commit()
        
        print(f"{len(problems)}개의 새로운 문제가 추가되었습니다.")
    else:
        print("이미 문제가 존재합니다. 초기화를 건너뜁니다.")

# 애플리케이션에 명령어 등록
app.cli.add_command(init_db_command)

@app.route('/admin/problem/new', methods=['GET', 'POST'])
@login_required
def new_problem():
    if request.method == 'POST':
        problem = Problem(
            title=request.form['title'],
            difficulty=request.form['difficulty'],
            time_limit=float(request.form['time_limit']),
            memory_limit=int(request.form['memory_limit']),
            description=request.form['description'],
            input_description=request.form['input_description'],
            output_description=request.form['output_description'],
            input_format=request.form['input_format'],
            output_format=request.form['output_format'],
            example_input=request.form['example_input'],
            example_output=request.form['example_output'],
            test_cases=request.form['test_cases']
        )
        db.session.add(problem)
        db.session.commit()
        flash('새 문제가 추가되었습니다.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('new_problem.html')

@app.route('/ranking')
def ranking():
    # 사용자별 정답 제출 수 계산
    user_scores = db.session.query(
        User.id,
        User.username,
        func.count(Submission.id).label('correct_submissions')
    ).join(Submission).filter(Submission.passed == True).group_by(User.id).order_by(func.count(Submission.id).desc()).all()

    # 랭킹 정보 생성
    rankings = []
    for rank, (user_id, username, correct_submissions) in enumerate(user_scores, start=1):
        rankings.append({
            'rank': rank,
            'username': username,
            'score': correct_submissions
        })

    return render_template('ranking.html', rankings=rankings)

if __name__ == '__main__':
    app.run(debug=True)
