#    from app import db, Problem
   
#    new_problem = Problem(
#        title="A+B",
#        difficulty="쉬움",
#        time_limit=1.0,
#        memory_limit=128,
#        description="두 정수 A와 B를 입력받은 다음, A+B를 출력하는 프로그램을 작성하시오.",
#        input_description="첫째 줄에 A와 B가 주어진다. (0 < A, B < 10)",
#        output_description="첫째 줄에 A+B를 출력한다.",
#        input_format="두 정수 A와 B가 공백으로 구분되어 주어집니다.",
#        output_format="A+B의 결과를 출력합니다.",
#        example_input="1 2",
#        example_output="3",
#        test_cases='[{"input": "1 2", "output": "3"}, {"input": "5 7", "output": "12"}]'
#    )
   
#    db.session.add(new_problem)
#    db.session.commit()
   
#    print("새로운 문제가 추가되었습니다.")



# flash sheel

from app import db, Problem

new_problem = Problem(
    title="A/B",
    difficulty="쉬움",
    time_limit=1.0,
    memory_limit=128,
    description="두 정수 A와 B를 입력받은 다음, A/B를 출력하는 프로그램을 작성하시오.",
    input_description="첫째 줄에 A와 B가 주어진다. (0 < A, B < 10)",
    output_description="첫째 줄에 A/B를 출력한다. 실제 정답과 출력값의 절대오차 또는 상대오차가 10^-9 이하이면 정답이다.",
    input_format="두 정수 A와 B가 공백으로 구분되어 주어집니다.",
    output_format="A/B의 결과를 출력합니다. 소수점 아래 9자리까지 출력하세요.",
    example_input="1 3",
    example_output="0.333333333",
    test_cases='[{"input": "1 3", "output": "0.333333333"}, {"input": "4 5", "output": "0.800000000"}]'
)

db.session.add(new_problem)
db.session.commit()

print("새로운 문제가 추가되었습니다.")

# 추가된 문제 확인
problems = Problem.query.all()
print(f"총 문제 수: {len(problems)}")
for problem in problems:
    print(f"ID: {problem.id}, 제목: {problem.title}, 난이도: {problem.difficulty}")