# coding=utf-8
import os

from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from datetime import datetime
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required, DataRequired
from flask import Flask, render_template, session, redirect, url_for, flash
from flask.ext.sqlalchemy import SQLAlchemy

# 配置数据库
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
# sqlite:////absolute/path/to/database
app.config['SQLALCHEMY_DATABASE_URI'] = \
	'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'hard to guess string'
bootstrap = Bootstrap(app)
moment = Moment(app)


# 修改->如果最后一个请求是post,刷新会重新提交post请求
@app.route('/', methods=['GET', 'POST'])
def index():
	# name = None
	form = NameForm()
	if form.validate_on_submit():
		old_name = session.get('name')
		if old_name is not None and old_name != form.name.data:
			flash('Looks like you have changed your name')
		session['name'] = form.name.data
		# 路由的端点是相应视图函数的名字
		return redirect(url_for('index'))
	# name = form.name.data
	# form.name.data = ''
	# 对于不存在的键,get() 会返回默认值 None
	return render_template('index.html', form=form, name=session.get('name'), current_time=datetime.utcnow())


@app.route('/user/<name>')
def user(name):
	# 左边的“name”表示参数名,就是模板中使用的占位符;右 边的“name”是当前作用域中的变量,表示同名参数的值
	# 模板中使用的{{ name }}结构表示一个变量
	return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500


# 类继承自Form
class NameForm(Form):
	# StringField 类表示属性为 type="text" 的 <input> 元素。SubmitField 类表示属性为 type="submit" 的 <input> 元素。
	# 字段构造函数的第一个参数是把表单渲染成 HTML 时使用的标号
	name = StringField('What is your name', validators=[DataRequired()])
	password = PasswordField('Please enter password', validators=[DataRequired()])
	submit = SubmitField('Submit')


# Flask-SQLAlchemy 要求每个模型都要定义主键,这一列经常命名为 id
class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	# db.relationship() 的第一个参数表明这个关系的另一端是哪个模型
	# backref 参数向 User 模型中添加一个 role 属性,从而定义反向关系。这一属性可替代 role_id 访问 Role 模型,此时获取的是模型对象,而不是外键的值
	# 一对一关系要把 uselist 设为 False
	# 多对一把外键和 db.relationship() 都放在“多”这一侧
	users = db.relationship('User', backref='role')

	def __repr__(self):
		return '<Role %r>' % self.name


# 一个User对应多个Role
class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	# 添加到 User 模型中的 role_id 列 被定义为外键
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

	def __repr__(self):
		return '<User %r>' % self.username


if __name__ == '__main__':
	app.run(debug=True)
