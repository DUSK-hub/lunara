def grade_quiz(answers, correct_answers):
    """
    Grade a quiz by comparing user answers with correct answers.
    
    Args:
        answers: dict of question_id: user_answer
        correct_answers: dict of question_id: correct_answer
    
    Returns:
        tuple: (score, total, percentage)
    """
    if not answers or not correct_answers:
        return 0, 0, 0
    
    score = 0
    total = len(correct_answers)
    
    for question_id, correct_answer in correct_answers.items():
        user_answer = answers.get(question_id, '').strip().lower()
        if user_answer == str(correct_answer).strip().lower():
            score += 1
    
    percentage = (score / total * 100) if total > 0 else 0
    return score, total, percentage

def parse_quiz_html(html_content):
    """
    Parse quiz HTML to extract questions and answers.
    Returns a structured dict of quiz data.
    """
    import re
    
    questions = []
    question_pattern = r'<div class="question">(.*?)</div>'
    matches = re.findall(question_pattern, html_content, re.DOTALL)
    
    for idx, match in enumerate(matches):
        questions.append({
            'id': idx + 1,
            'content': match.strip()
        })
    
    return questions