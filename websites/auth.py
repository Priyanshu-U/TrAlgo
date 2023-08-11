import time
from . import db
from flask import Blueprint,render_template,redirect,url_for,request
from flask.helpers import flash
auth = Blueprint('auth', __name__)
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
import re
from flask_login import login_user,login_required,current_user,logout_user	
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
def check(email):
	if(re.match(regex, email) ):
		return True
	else:
		return False

# validate password
def password_check(passwd):
	
	SpecialSym =['$', '@', '#', '%']
	val = True
	
	if len(passwd) < 6:
		flash('length should be at least 6 ', 'error')
		val = False
		
	if len(passwd) < 8:
		flash('Password Length should be greater than 8 ', 'error')
		val = False
		
	if not any(char.isdigit() for char in passwd):
		flash('Password should have at least one numeral ', 'error')
		val = False
		
	if not any(char.isupper() for char in passwd):
		flash('Password should have at least one uppercase letter ', 'error')
		val = False
		
	if not any(char.islower() for char in passwd):
		flash('Password should have at least one lowercase letter ', 'error')
		val = False
		
	if not any(char in SpecialSym for char in passwd):
		flash('Password should have at least one of the symbols " $ @ # " ', 'error')
		val = False
	if val:
		return val


@auth.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'POST':	
		email=request.form.get('logemail')
		password=request.form.get('logpass')
		print(email,password)
		username=request.form.get('signname')
		signemail=request.form.get('signemail')
		signpass=request.form.get('signpass')
		print(username,signemail,signpass)
		if email!=None and password!=None and username==None and signemail==None and signpass==None:
			if not check(email) :
				flash('Invalid email address', 'error')
				return redirect(url_for('auth.login'))
			elif not password_check(password):
				flash('Invalid password', 'error')
				return redirect(url_for('auth.login'))
			else:
				user =User.query.filter_by(email=email).first()
				if user:
					if check_password_hash(user.password, password):
						flash('You are logged in', 'success')
						login_user(user,remember=True)
						return redirect(url_for('views.index'))
					else:
						flash('Password is incorrect', 'error')
						return redirect(url_for('auth.login'))
				else:
					flash('User does not exist', 'error')
					return redirect(url_for('auth.login'))

		elif email==None and password==None and username!=None and signemail!=None and signpass!=None:
			user=User.query.filter_by(email=signemail).first()
			if user:
				flash('Username/Email already in use', 'error')
				return redirect(url_for('auth.login'))

			elif not check(signemail) :
				flash('Invalid email address', 'error')
				return redirect(url_for('auth.login'))
			elif not password_check(signpass):
				flash('Invalid password', 'error')
				return redirect(url_for('auth.login'))
			else:
				new_user = User(username=username,email=signemail,password=generate_password_hash(signpass, method='sha256'))
				db.session.add(new_user)
				db.session.commit()
				flash('User created successfully', 'success')
				login_user(new_user)
				return redirect(url_for('views.index'))


		# new_user = User(email=email, password=password)
	return render_template('login.html',user=current_user)


@auth.route('/logout')
@login_required
def logout():
	# render_template('logout.html')
	logout_user()
	return redirect(url_for('auth.login'))

