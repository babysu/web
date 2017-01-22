#http://docs.python-requests.org/zh_CN/latest/user/advanced.html requests的用法
'''
from flask import Flask
app = Flask(__name__)

#route()装饰器告诉Flask什么样的url能触发函数
@app.route('/')  
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run() #run函数让应用运行在本地服务器上
#虽然run()方法适用于启动本地的开发服务器,


from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')#使用render_template()方法来渲染模板。

@app.route('/signin', methods=['GET'])
def signin_form():
    return render_template('form.html')

@app.route('/signin', methods=['POST'])
def signin():
    username = request.form['username']
    password = request.form['password']
    if username=='admin' and password=='password':
        return render_template('signin-ok.html', username=username)
    return render_template('form.html', message='Bad username or password', username=username)

if __name__ == '__main__':
    app.run()


'''
#http://blog.csdn.net/lovedied/article/details/30127657 基于flask的访客留言簿实现

# -*- coding: utf-8 -*-  
# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort,render_template, flash
from contextlib import closing  
import time

# configuration  
DATABASE = 'E:\\PythonWork\\flaskr.db'#数据库存储路径  
DEBUG = True  
SECRET_KEY = 'development key'  
USERNAME = 'admin'  
PASSWORD = 'default'  
  
#create our little application :)  
app = Flask(__name__)  
app.config.from_object(__name__)  
#app.config.from_envvar('FLASKR_SETTINGS', silent=True)  
  
def connect_db():#快速连接到指定数据库的方法  

    return sqlite3.connect(app.config['DATABASE'])  
  
  
def init_db():#初始化数据库  
    print('init')
    conn=sqlite3.connect(DATABASE)
    cu = conn.cursor()    
    with closing(connect_db()) as db:  
        with app.open_resource('schema.sql','r') as f:  
            db.cursor().executescript(f.read())  
            db.commit()  
 
 #flask中有两种context，application context和request context
 #这里的before,teardown明显都是request的上下文，当HTTP请求过来的时候，进入这个上下文
@app.before_request  #在请求收到之前绑定一个函数做一些事情
def before_request():  
    g.db = connect_db()  
 
 
@app.teardown_request  #每一个请求之后绑定一个函数，即使遇到了异常
def teardown_request(exception):  
    g.db.close()  
 
 
 #显示条目,这个试图显示数据库中存储的所有条目.它帮定在应用的根地址,并从数据库查询出文章的标题和正文.id 值最大的条目与(最新的条目)
 #会显示在最上方.
 
@app.route('/')  
def show_entries():#输出函数,会将条目作为字典传递给 show_entries.html 模板，并返回之后的渲染结果  
    flash('be show_entries??')
    cur = g.db.execute('select title, text,timet from entries order by id desc limit 10')  
    entries = [dict(title=row[0], text=row[1],timet=row[2]) for row in cur.fetchall()]  

    return render_template('show_entries.html', entries=entries)  
	
 
 #添加条目,这个视图允许已登入的用户添加新条目,并只响应POST请求,实际的表单显示在show_entries页,flash()向下一次请求发送提示消息
 #并重定向show_entries页
 
@app.route('/add', methods=['POST'])  
def add_entry():#用户添加新的留言信息函数，并只响应 POST 请求，表单显示在 show_entries   
    if not session.get('logged_in'):  
        abort(401)
    		
    if len(request.form['text']) >5 and len(request.form['text'])<500:#使用问号标记来构建 SQL 语句,使用格式化字符串构建 SQL 语句时，你的应用容易遭受 SQL 注入
        
        localt=time.asctime(time.localtime(time.time()))
        #flash(localt)
        g.db.execute('insert into entries (title,text,timet) values (?,?,?)',  
                 [request.form['title'],request.form['text'],localt])  
        
        g.db.commit()  
        flash('New entry was successfully posted')
        print('be add entry')
    else:  
        flash('The input range must be between 50 and 500 characters ')#如果留言信息不在范围内作出提示  
    return redirect(url_for('show_entries'))  
 
 
@app.route('/login', methods=['GET', 'POST'])  
def login():#登入函数  
    error = None  
    if request.method == 'POST':  
        if request.form['username'] != app.config['USERNAME']:  
            error = 'name error'  
        elif request.form['password'] != app.config['PASSWORD']:  
            error = 'password error'  
        else:  
            session['logged_in'] = True  
            #flash('log in')  
            return redirect(url_for('show_entries'))  
    return render_template('login.html', error=error) 
    #return redirect(url_for('show_entries'))  	
 
 #从会话中删除logged_in键，用字典的pop方法,并传入第二个参数，这个方法会从字典中
 #删除这个键，如果这个键不存在则什么都不作。
@app.route('/logout')  
def logout():#退出登录函数  
    session.pop('logged_in', None)  
    flash('log out')  
    return redirect(url_for('show_entries'))  
  
  
if __name__ == '__main__':  
    init_db()  
    app.run(debug=True)  