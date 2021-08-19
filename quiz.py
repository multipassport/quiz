import os


def read_koi8r_file(filepath):
    with open(filepath, 'r', encoding='KOI8-R') as file:
        return file.read()


def get_quiz_content(folder):
    files = os.listdir(folder)
    for file in files:
        filepath = os.path.join(folder, file)
        file_content = read_koi8r_file(filepath)
        paragraphs = file_content.split('\n\n')
        questions = [
            paragraph.split('\n', 1)[-1] for paragraph in paragraphs
            if paragraph.startswith('Вопрос')
        ]
        answers = [
            paragraph.split('\n', 1)[-1].split('.')[0] for paragraph in paragraphs
            if paragraph.startswith('Ответ')
        ]
        yield from zip(questions, answers)
