import os


def read_file(filepath):
    with open(filepath, 'r', encoding='KOI8-R') as file:
        return file.read()


def get_quiz_content(folder):
    files = os.listdir(folder)
    for file in files:
        filepath = os.path.join(folder, file)
        file_content = read_file(filepath)
        paragraphs = file_content.split('\n\n')
        questions = [paragraph for paragraph in paragraphs if paragraph.startswith('Вопрос')]
        answers = [paragraph for paragraph in paragraphs if paragraph.startswith('Ответ')]
        yield from zip(questions, answers)


if __name__ == '__main__':
    folder = 'questions'
    quiz_content = dict(get_quiz_content(folder))
