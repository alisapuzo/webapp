import os
from flask import Flask, render_template, redirect, url_for, request, abort, flash
from flask_bootstrap import Bootstrap5
import db, forms

app = Flask(__name__)

app.config.from_mapping(
    SECRET_KEY='secret_key_just_for_dev_environment',
    DATABASE=os.path.join(app.instance_path, 'todos.sqlite'),
    BOOTSTRAP_BOOTSWATCH_THEME = 'pulse'
)
app.cli.add_command(db.init_db)
app.teardown_appcontext(db.close_db_con)

bootstrap = Bootstrap5(app)

@app.route('/')
def index():
    return redirect(url_for('todos')) #vorher war da 'lists'

@app.route('/lists/')
def lists():
    db_con = db.get_db_con()
    sql_query = 'SELECT * from list ORDER BY name'
    lists_temp = db_con.execute(sql_query).fetchall()
    lists = []
    for list_temp in lists_temp:
        list = dict(list_temp)
        sql_query = (
            'SELECT COUNT(complete) = SUM(complete) '
            'AS complete FROM todo '
            f'JOIN todo_list ON list_id={list["id"]} '
                'AND todo_id=todo.id; '
        )
        complete = db_con.execute(sql_query).fetchone()['complete']
        list['complete'] = complete
        lists.append(list)
    return render_template('lists.html', lists=lists)

@app.route('/lists/<int:id>')
def list(id):
    db_con = db.get_db_con()
    sql_query_1 = f'SELECT name FROM list WHERE id={id}'
    sql_query_2 = (
        'SELECT id, complete, description FROM todo '
        f'JOIN todo_list ON todo_id=todo.id AND list_id={id} '
        'ORDER BY id;'
    )
    list = {}
    list['name'] = db_con.execute(sql_query_1).fetchone()['name']
    list['todos'] = db_con.execute(sql_query_2).fetchall()
    return render_template('list.html', list=list)

@app.route('/insert/sample')
def run_insert_sample():
    db.insert_sample()
    return 'Database flushed and populated with some sample data.'

#instanziieren von CreateToDoForm in der Funktion todos() 
@app.route('/todos/<int:id>', methods=['GET', 'POST'])
def todo(id):
    db_con = db.get_db_con()
    if request.method == 'GET':
        sql_query = (
            'SELECT * FROM '
            '( SELECT * FROM todo '
                'LEFT JOIN todo_list '
                'ON todo.id=? AND todo_id=todo.id ) '
            'WHERE id=?;'
        )
        todo = db_con.execute(sql_query, [id, id]).fetchone()
        if todo:
            form = forms.TodoForm(data=todo)  # (1.)
            sql_query = 'SELECT id, name FROM list ORDER BY name;'
            choices = db_con.execute(sql_query).fetchall()  # (2.)
            form.list_id.choices = [(0, 'List?')] + [(c['id'], c['name']) for c in choices]
            return render_template('todo.html', form=form)  # (3.)
        else:
            abort(404)
    else:  # request.method == 'POST'
        form = forms.TodoForm()
        if form.method.data == 'PATCH':  # (4.)
            if form.validate():  # (5.)
                sql_query = 'UPDATE todo SET complete = ?, description = ? WHERE id = ?;'
                db_con.execute(sql_query, [form.complete.data, form.description.data, id])
                sql_query = 'DELETE FROM todo_list WHERE todo_id = ?;'
                db_con.execute(sql_query, [id])
                if form.list_id.data:
                    sql_query = 'INSERT INTO todo_list (todo_id, list_id) VALUES (?, ?);'
                    db_con.execute(sql_query, [id, form.list_id.data])
                db_con.commit()
                flash('Todo has been updated.', 'success')
            else:
                flash('No todo update: validation error.', 'warning')
            return redirect(url_for('todo', id=id))
        elif form.method.data == 'DELETE':
            sql_query = 'DELETE FROM todo WHERE id = ?;'
            db_con.execute(sql_query, [id])
            db_con.commit()
            flash('Todo has been deleted.', 'success')
            return redirect(url_for('todos'), 303)
        else:
            flash('Nothing happened.', 'info')
            return redirect(url_for('todo', id=id))
        
@app.route('/todos/', methods=['GET', 'POST'])
def todos():
    db_con = db.get_db_con()
    form = forms.CreateTodoForm()  # Formular für neues Todo
    if request.method == 'POST':
        if form.validate():
            db_con.execute('INSERT INTO todo (description) VALUES (?)', [form.description.data])
            db_con.commit()
            flash('Todo created!', 'success')
        else:
            flash('Validation error!', 'warning')
        return redirect(url_for('todos'))

    todos_list = db_con.execute('SELECT * FROM todo ORDER BY id').fetchall()
    return render_template('todos.html', todos=todos_list, form=form)