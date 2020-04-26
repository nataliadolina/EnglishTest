import os

from flask import Flask, render_template, request, session, url_for
from werkzeug.utils import redirect, secure_filename
from DB import DB, UsersModel, TasksModel, ProgresssModel, TaskUser, CategoryModel
from wtf_forms import RegistrateForm, LoginForm, AddTaskForm
import webbrowser
import copy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

base = DB()
users_base = UsersModel(base)
users_base.init_table()
progress = ProgresssModel(base)
progress.init_table()
tasks_model = TasksModel(base)
tasks_model.init_table()
all_users = users_base.get_all()
task_user = TaskUser(base)
task_user.init_table()
cat_model = CategoryModel(base)
cat_model.init_table()


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrateForm()
    if form.validate_on_submit():
        f1, f2 = form.username.data, form.password.data
        exists = users_base.exists(f1, f2)
        if exists[0]:
            form.username.data = ''
            return render_template('registration.html',
                                   text='Пользователь с таким именем уже существует. Пожалуйста, смените логин',
                                   form=form)
        elif f2 != form.repeatpassword.data:
            form.password.data = ''
            return render_template('registration.html',
                                   text='Введённые вами пароли различаются. Пожалуйста, проверьте написание', form=form)
        else:
            session['username'] = form.username.data
            users_base.insert(form.username.data, form.password.data, form.email.data)
            session['user_id'] = users_base.exists(form.username.data, form.password.data)[1]
            return redirect('/homepage')
    return render_template('registration.html', text='', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        exists = users_base.exists(request.form['username'], request.form['password'])
        if exists[0]:
            session['username'] = request.form['username']
            session['user_id'] = exists[1]
            return redirect('/homepage')
        return render_template('login.html', title='Authorization', text='invalid login or password', form=form)
    return render_template('login.html', title='Authorization', text='', form=form)


@app.route('/homepage1', methods=['GET', 'POST'])
def popp():
    session.pop('list_id')
    return redirect('/homepage')


@app.route('/return_to_mainpage', methods=['GET', 'POST'])
def return_to_mainpage():
    all_tasks = tasks_model.get_all()
    all = len(all_tasks)
    return render_template('all_tasks.html', all=range(0, all),
                           text="Перед тем, как добавлять себе задания, пожалуйста, авторизуйтесь.")


@app.route('/', methods=['GET', 'POST'])
@app.route('/mainpage', methods=['GET', 'POST'])
def show_all():
    session["warning"] = 'Вы не можете повторно добавить задание, которое у вас уже есть.'
    all_tasks = tasks_model.get_all()
    all_cats = cat_model.get_all()
    all_tasks.reverse()
    session["all_titles"] = []
    session['all_cats'] = []
    session["unique_cats"] = list(set([i[1] for i in cat_model.get_all()]))
    session['all_contents'] = []
    session['all_ides'] = []
    all = len(all_tasks)
    for task in all_tasks:
        id, text, picture, links, hints, title, content, choices, correct_choices = task
        session['all_titles'].append(title)
        cats = cat_model.get(id)
        if cats:
            cat = cats[1]
        else:
            cat = None
        if cat:
            session["all_cats"].append(cat)
        else:
            session['all_cats'].append("")
        if content:
            session['all_contents'].append(content.split("\n")[0])
        else:
            session['all_contents'].append("")
        session['all_ides'].append(id)
    return render_template('all_tasks.html', all=range(0, all), text='')


@app.route('/warning', methods=['GET', 'POST'])
def warning():
    all_tasks = tasks_model.get_all()
    all = len(all_tasks)
    return render_template('all_tasks.html', all=range(0, all),
                           text="Вы не можете добавлять одно и то же задание несколько раз")


@app.route('/add_to_user/<int:id>', methods=['GET', 'POST'])
def add_to_user(id):
    if session["user_id"] not in [i[-1] for i in task_user.get_by_task(id)]:
        task_user.insert(id, session['user_id'])
    else:
        return redirect("/warning")
    return redirect('/mainpage')


@app.route('/homepage', methods=['GET', 'POST'])
def tasks():
    if 'username' in session:
        if 'list_id' not in session:
            session['list_id'] = 0
        return redirect('/all_tasks/{}'.format(session['user_id']))
    else:
        return redirect('/login')


@app.route('/add_task/<string:title>/<string:id>', methods=['GET', 'POST'])
def add_task(title, id):
    if 'username' not in session:
        return redirect('/login')
    form = AddTaskForm()
    users = []
    title = int(title)
    users_ides = []
    text, links, hints, title1, content, choices, correct_choice = "", "", "", "", "", "", ""
    if request.method == 'GET':
        if title != -1 or title == -2:
            if title != -1 and title != -2:
                text, picture, links, hints, title1, content, choices, correct_choice = tasks_model.get(
                    session['task_id'][title])[1:]
                users_ides = [i[-1] for i in task_user.get_by_task(session['task_id'][title])]
            elif title == -2:
                text, picture, links, hints, title1, content, choices, correct_choice = tasks_model.get(id)[1:]
                users_ides = [i[-1] for i in task_user.get_by_task(id)]
            for i in users_ides:
                users.append(users_base.get(i)[1])
            form.text.data = text
            # form.picture.data = picture
            form.links.data = links
            form.hints.data = hints
            form.title.data = title1
            form.sentence.data = content
            form.choice.data = choices
            form.correct.data = correct_choice
    elif request.method == 'POST':
        text = form.text.data
        picture = None
        '''
        if allowed_file(f.filename):
            filename = secure_filename(f.filename)
            save_path = "{}/{}".format(app.config["UPLOAD_FOLDER"], filename)
            f.save(save_path)

        with open('static/' + f, 'w') as rf:
            rf.write(f.read().decode('utf-8'))
        '''
        links = form.links.data
        title1 = form.title.data
        sentence = form.sentence.data
        choice = form.choice.data.strip()
        correct = form.correct.data.strip()
        hints = form.hints.data.strip()
        '''
        if (len(sentence.split('\n')) != len(choice.split('\n')) or len(correct.split('\n')) != len(
                choice.split('\n'))) and choice != '':
            return render_template('add_task.html', form=form, username=session['username'], users=all_users,
                                   text='invalid task. Number of strings in labels "sentences",'
                                        ' "answer choice", "correct answer" must be the same')
                                        '''
        if not title and title1 in [i[1] for i in tasks_model.get_all()]:
            return render_template('add_task.html', form=form, username=session['username'], users=all_users,
                                   text='задание с таким названием уже существует.')
        else:
            if title != -2 and title != -1:
                not_title_index, title_index = session['task_id'][title], session['task_id'][title]
            elif title == -1:
                not_title_index, title_index = -1, -1
            else:
                not_title_index, title_index = id, id
            inserted = False
            if not title == -1 and id == -1:
                tasks_model.insert(text, picture, links, hints, title1, sentence, choice, correct)
                inserted = True
                not_title_index = tasks_model.index()
            ides = [j[0] for j in all_users]
            checked = []
            flag = False
            f = ''
            try:
                f = request.files('file')
            except Exception as e:
                pass
            else:
                with open('static/' + f, 'w') as rf:
                    rf.write(f.read().decode('utf-8'))
            for i in ides:
                if request.form.get(str(i)):
                    checked.append(i)
            else:
                if session['list_id'] not in checked and not inserted and title != -2:
                    tasks_model.insert(text, picture, links, hints, title1, sentence, choice, correct)
                    inserted = True
                    title_index = tasks_model.index()
                    flag = True
                elif title != -2:
                    tasks_model.update(text, picture, links, hints, title1, sentence, choice, correct,
                                       session['task_id'][title])
                elif title == -2:
                    tasks_model.update(text, picture, links, hints, title1, sentence, choice, correct, id)
            for i in checked:
                if title == -1 and id == -1:
                    task_user.insert(not_title_index, i)
                elif i not in [j[1] for j in task_user.get_by_task(not_title_index)]:
                    task_user.insert(title_index, i)
                    '''
                    if flag and title_index not in [i[1] for i in task_user.get_all(i)]:
                        task_user.insert(title_index, i)
                    elif not flag and not_title_index not in [i[1] for i in task_user.get_all(i)]:
                        task_user.insert(not_title_index, i)s
                        '''
            return redirect("/homepage")
    return render_template('add_task.html', form=form, checked=users, username=session['username'], users=all_users)


@app.route('/all_tasks/<int:id>', methods=['GET', 'POST'])
def all_tasks(id):
    all, username = '', ''
    if 'username' not in session:
        return redirect('/login')
    if id != 0 and session['user_id'] in [1, 2]:
        all = [i[1] for i in task_user.get_all(id)]
        # print(users_base.get_all())
        username = users_base.get(id)[1]
        session['list_id'] = id
    else:
        id = 0
    if id == 0:
        session['list_id'] = session['user_id']
        all = [i[1] for i in task_user.get_all(session['list_id'])]
        username = ''
    else:
        all = [i[1] for i in task_user.get_all(id)]
    # print(tasks_model.get_all())
    session['text'] = []
    session['picture'] = []
    session['titles'] = []
    session['contents'] = []
    session['choices'] = []
    session['correct'] = []
    session['task_id'] = all
    session['hints'] = []
    session['links'] = []
    session['whattounderline'] = []
    session['splitedcontents'] = []
    session['cat'] = []
    arr1 = []
    all1 = set()
    for i in all:
        try:
            text, picture, links, hints, title, content, choices, correct_choices = tasks_model.get(i)[1:]
            session['text'].append(text)
            session['picture'].append(picture)
            session['titles'].append(title)
            arr1 = []
            arr = []
            arr3 = []
            session['contents'].append(content.split('\n'))
            for i in session['contents'][-1]:
                arr3.append(i.split())
                if '[' in i and ']' in i:
                    index_start = i.index("[")
                    index_finish = i.index("]") - 1
                    arr = [index_start, index_finish]
                else:
                    arr = []
                i.replace('[', '')
                i.replace(']', '')
                arr1.append(arr)
            session['whattounderline'].append(arr1)
            session['correct'].append(correct_choices.split('\n'))
            session['splitedcontents'].append(arr3)
            if choices:
                choices = [i.split("//") for i in choices.split('\n')]
                session['choices'].append(choices)
            else:
                session['choices'].append([])
            if hints:
                session['hints'].append(hints.split('\n'))
            else:
                session['hints'].append([])
            if links:
                session['links'].append(links.split('\n'))
            else:
                session['links'].append([])
        except Exception as e:
            all1.add(i)
    sc = progress.get_all(session['list_id'])
    scores_id = [i[-2] for i in sc]
    scores1 = []
    n_all = 0
    all = set(all)
    all = list(all - all1)
    for i in all:
        if i in scores_id:
            n_correct = sc[scores_id.index(i)][3]
            n_all = len(session['contents'][all.index(i)])
        else:
            n_correct = 0
            try:
                n_all = len(session['contents'][all.index(i)])
            except IndexError:
                all.pop(all.index(i))
        scores1.append(str(n_correct) + '/' + str(n_all))
    session['scores'] = scores1
    n = list(range(0, len(all), 3))
    return render_template('tasks.html', flag=True, n=n, all=all, n_all=len(all), name=username)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_tasks(id):
    if 'username' not in session:
        return redirect('/login')
    # if id not in [i[1] for i in task_user.get_all()]:
    # tasks_model.delete(id)
    progress.delete(session["task_id"][id], session['list_id'])
    if task_user.get_by_task(session['task_id'][id]):
        task_user.delete(session['task_id'][id], session['list_id'])
    return redirect('/all_tasks/{}'.format(session['list_id']))


@app.route('/deletefromdb/<int:id>', methods=['GET', 'POST'])
def delete_from_db(id):
    tasks_model.delete(id)
    progress.delete_by_task_id(id)
    if task_user.get_by_task(id):
        task_user.delete_by_task(id)
    return redirect("/mainpage")


@app.route('/task/<int:id>', methods=['GET', 'POST'])
def task(id):
    if 'username' not in session:
        return redirect('/login')
    num_correct = 0
    l = len(session['contents'][id])
    length = list(range(l))
    answer = ''
    correctness = ''
    correct_answers = session['correct'][id]
    choices = []
    task_id = session['task_id'][id]
    correct = progress.get_all(session['list_id'], task_id)
    c = []
    ides = []
    k = -1
    length_of_choices = []
    values = []
    hint_given = []
    if session['links']:
        links = session['links'][id]
    else:
        links = []
    picture = session['picture'][id]
    text = session["text"][id]
    if correct:
        answer = correct[0][4].split("//")
        c = correct[0][-3].split()  # получили прогресс
        hint_given = list(map(int, correct[0][1].split()))
    if session['choices'][id]:
        choices = session['choices'][id]
        values = copy.deepcopy(choices)
        for i in range(len(choices)):
            length_of_choices.append(list(range(0, len(choices[i]))))
            for j in range(len(choices[i])):
                choices[i][j] = choices[i][j].strip()
                choices[i][j] = choices[i][j].replace("\r", '')
                values[i][j] = values[i][j].replace("\r", '')
                values[i][j] = values[i][j].replace(" ", "==")
    if request.method == 'POST':
        answer = ''
        try:
            ides = [i[-2] for i in correct]
        except IndexError:
            pass
        session['scores'] = []
        ans1 = ''
        hints = session['hints'][id]
        flag = False
        hint = ''
        for i in length:
            ans = str(request.form[str(i)]).replace("==", " ").lower().strip()
            if answer:
                answer += "//" + ans
            else:
                answer += ans
            try:
                ans1 = correct_answers[i].strip()  # получили правильный ответ
            except Exception as e:
                correctness += ' ' + 'false'
                if not flag and hints:
                    flag = True
                    hint = hints[i]
            else:
                correct_answer = [i.strip().lower() for i in ans1.split("//")]
                if ans in correct_answer:
                    num_correct += 1
                    correctness += ' ' + 'true'
                else:
                    if not flag and hints:
                        flag = True
                        if len(hints) >= i + 1:
                            hint = hints[i]
                    correctness += ' ' + 'false'
        corr = correctness.split()
        num_incor = []
        for i in range(len(corr)):
            if corr[i].strip() == 'false':
                num_incor.append(str(i))
        if task_id in ides:
            progress.update(l, num_correct, answer, correctness, task_id, session['list_id'])
            current = set(progress.get_all(session['list_id'], task_id)[0][1].split())
            hint_given1 = list(current | set(num_incor))
            progress.set_hint(task_id, session['list_id'], ' '.join(hint_given1))
        else:
            progress.insert(l, num_correct, answer, correctness, task_id, session['list_id'])
            progress.set_hint(task_id, session['list_id'], ' '.join(num_incor))
        correct = progress.get_all(session['list_id'], task_id)
        # c = correct[0][-3]  # правильность выполнения
        hint_given = list(map(int, correct[0][1].split()))  # все задания не выполненные с первого раза
        if correct:
            c = correct[0][-3].split()
            answer = [i.strip() for i in correct[0][4].split("//")]
        else:
            answer = []
        if hint:
            webbrowser.open_new_tab(hint.strip())
    return render_template('task.html', i=id, text=text, picture=picture, links=links, hint_given=hint_given,
                           length=length, correct=c, l_correct=len(c), answer=answer, choices=choices, k=k,
                           length_of_choices=length_of_choices, values=values)


@app.route('/all_users')
def users():
    l = list(range(len(all_users)))
    return render_template('all_users.html', length=l, users=all_users)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
