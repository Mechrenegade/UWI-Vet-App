import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import (RegistrationForm, LoginForm, EvaluateForm, StudentSearchForm, 
                            RotationForm, UpdateAccountForm, ChangePasswordForm, PostForm,
                            RequestResetForm, ResetPasswordForm, NewCompForm, EditCompForm,
                            SearchbyNameForm, NewStudentForm, SearchbyIDForm)
from flaskblog.models import User, Post3, Comp, Student, Competancy_rec, User2, Activity
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from datetime import datetime
import flask_excel as excel
import json


@app.before_first_request
def setup():
    db.Model.metadata.create_all(bind=db.engine)

@app.route("/")

@app.route("/home")
def home():
    page= request.args.get('page', 1, type=int)
    posts = Post3.query.order_by(Post3.date_posted.desc()).paginate(page=page, per_page=3)
    
    return render_template('home.html', posts=posts)

@app.route("/about", methods=['GET', 'POST'])
def about():
    if request.method == 'POST':
        def comp_init_func(row):
            c = Comp(row['Description'], row['Code'], row['Rotation Name'])
            return c
            
        request.save_to_database(
            field_name ='file', session=db.session,
            table=Comp,
            initializer=comp_init_func)
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
@login_required
def register():
    if current_user.level == 1:
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User2(username=form.username.data, email=form.email.data, level=form.level.data, rotation1=form.rotation1.data, rotation2=form.rotation2.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            activity = Activity(activityType='AC', actionID=user.id, clincianID=current_user.id)
            db.session.add(activity)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        
    else:
        flash('You did not have privilages to view that page', 'danger')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User2.query.filter_by(email=form.email.data).first()
        email_timer()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful, Please check email and Password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    image_file = url_for('static', filename='profilepics/'+current_user.image_file)
    percent=0
    if current_user.level == 3:
        percent=calc_percent(current_user.username)
    return render_template('account.html', title='Account.html', image_file=image_file, percent=percent)

@app.route("/usersreg")
@login_required
def competancy():
    if current_user.level == 1:    
        records= User2.query.all()
        return render_template('usersreg.html', title='usersreg.html', User2=records)
    else:
        flash('ONLY ADMINS CAN ACCESS THIS PAGE','danger')
        return redirect(url_for('home'))

@app.route("/rotations", methods=['GET'])
@login_required
def rotations():
    if current_user.level == 1 or current_user.level == 2:
        records = Comp.query.all()
        return render_template('rotations.html', title='Rotations.html', Comp=records)
    else:
        flash('ONLY CLINICIANS CAN ACCESS THIS PAGE','danger')
    return redirect(url_for('home'))

@app.route("/evaluate", methods=['GET', 'POST'])
@login_required
def evaluate():
    if current_user.level == 1 or current_user.level == 2:
        form = SearchbyIDForm()
        if form.validate_on_submit():
            return redirect(url_for('comp_rec2', student_id=form.studentid.data))

        return render_template('evaluate.html', title='Evaluate.html', form=form)
    else:
        flash('ONLY ADMINS CAN ACCESS THIS PAGE','danger')
    return redirect(url_for('home'))

@app.route("/student/<id>", methods=['GET'])
@login_required
def getstudent(id):
    if current_user.level == 1 or current_user.level == 2:
        s_rec= Student.query.filter_by(studentid = id).first()
        if s_rec == None:
            return jsonify({"error":"No Student Exists"})
        s_rec = s_rec.__dict__
        s_rec.pop('_sa_instance_state')
        return jsonify(s_rec)
    else:
        flash('ONLY ADMINS CAN ACCESS THIS PAGE','danger')
    return redirect(url_for('home'))

@app.route("/students", methods=['GET', 'POST'])
@login_required
def students():
    if current_user.level == 1 or current_user.level == 2:
        form2 = SearchbyNameForm()
        
        if request.method == 'POST':
            def stu_init_func(row):
                s = Student(row['id'],row['Student Name'], row['Date Enrolled'], row['Email'])
                return s
                
            request.save_to_database(
                field_name ='file', session=db.session,
                table=Student,
                initializer=stu_init_func)
            
            record = Student.query.all()
            comp_tbl = Comp.query.all()
            p = bcrypt.generate_password_hash('password').decode('utf-8')
            for r in record:
                
                s = User2(username=r.studentid, email=r.email, password=p, level=3, rotation1='Student', rotation2=r.studentid) # automatically adding students user accounts
                db.session.add(s)
                db.session.commit()
                # test=r.id
                for c in comp_tbl:
                    d = Competancy_rec(mark=0, comp_id=c.descrip, comp_name=c.rot_name, clinician_id=current_user.id, student_id=r.studentid) #automatically building comp rec table for each student
                    db.session.add(d)
                db.session.commit()

        records = Student.query.all()
        return render_template('students.html', title='Students.html', Student=records, records=records, form2=form2)
    else:
        flash('ONLY CLINICIANS CAN ACCESS THIS PAGE','danger')
    return redirect(url_for('home'))

@app.route("/students/<string:studentname>", methods=['GET', 'POST'])
@login_required
def searchbyname(studentname):

    name = request.form[studentname]
    search = "%{}%".format(name)
    s_rec= Student.query.filter(Student.name.like(search)).first()
    if s_rec == None:
        return jsonify({"error":"No Student Exists"})
    s_rec = s_rec.__dict__
    s_rec.pop('_sa_instance_state')
    return jsonify(s_rec)
    

@app.route("/reports")
@login_required
def reports():
    if current_user.level == 1 or current_user.level == 2:
        return render_template('reports.html', title='Reports.html')
    else:
        flash('ONLY CLINICINS CAN ACCESS THIS PAGE','danger')
    return redirect(url_for('home'))

@app.route("/manageusers")
@login_required
def managerusers():
    if current_user.level == 1:
        return render_template('manageusers.html', title='ManagerUsers.html')
    else:
        flash('ONLY ADMINS CAN ACCESS THIS PAGE','danger')
    return redirect(url_for('home'))

@app.route("/reminders")
@login_required
def reminders():
    if current_user.level == 1 or current_user.level == 2:
        return render_template('reminders.html', title='Reminders.html')
    else:
        flash('ONLY CLINICANS CAN ACCESS THIS PAGE','danger')
    return redirect(url_for('home'))

@app.route("/studentRecord")
@login_required
def studentRecord():
    if current_user.level == 1:
        return render_template('studentRecord.html', title='studentRecord.html')
    else:
        flash('ONLY CLINICIANS CAN ACCESS THIS PAGE','danger')
    return redirect(url_for('home'))

@app.route("/searchstudent/<s_id>")
def searchstudent(s_id):
    record = Student.query.filter_by(id=s_id).first().__dict__
    record.pop('_sa_instance_state')
    return json.dumps(record)

@app.route("/comp_rec/<student_id>", methods=['GET'])
@login_required
def comp_rec(student_id): #searching comp_rec for a student's record
    if current_user.level == 1:
        records= Competancy_rec.query.filter_by(student_id=student_id).all()
        # records = Competancy_rec.query.join(
        print (records)
        output = {"data":[]}
        for r in records:
            print (r)
            r2 = r.__dict__
            r2.pop('_sa_instance_state')
            output["data"].append(r2)
        return jsonify(output)
    else:
        flash('ONLY ADMINS CAN ACCESS THIS PAGE','danger')
    return redirect(url_for('home'))
    

@app.route("/comp_rec2/<string:student_id>", methods=['GET', 'POST'])
@login_required
def comp_rec2(student_id): #searching comp_rec for a student's record
    
    form = SearchbyIDForm()
    count = 0 
    records= Competancy_rec.query.filter_by(student_id=student_id).all()
    student= Student.query.filter_by(studentid=student_id).first()
    return render_template('evaluate.html', title="Evaluate Student", records=records, form=form, student=student, count=count)

@app.route("/update_rec/<comp_rec>/<mark>")
@login_required
def update_rec(comp_rec, mark):
    if current_user.level == 1 or current_user.level == 2:
        try:
            print(mark)
            if mark == "false":
                mark = 0
            else:
                mark = 1
            record= Competancy_rec.query.filter_by(id=int(comp_rec)).first()
            record.mark = int(mark)
            print(record.mark)
            db.session.commit()
            activity = Activity(activityType='MS', actionID=record.student_id, clincianID=current_user.id)
            db.session.add(activity)
            db.session.commit()
            return jsonify({"success":"record updated"})
        except Exception as e:
            print(e)
            return jsonify({"error":"Error has occured"})
    else:
        flash('ONLY ADMINS CAN ACCESS THIS PAGE','danger')
    return redirect(url_for('home'))

@app.route("/update_rec2/<int:comp_rec>")
@login_required
def update_rec2(comp_rec):
      
        record= Competancy_rec.query.filter_by(id=comp_rec).first()
        if record.mark == 0:
            record.mark = 1
        else:
            record.mark = 0
        
        db.session.commit()
        activity = Activity(activityType='MS', actionID=record.student_id, clincianID=current_user.id)
        db.session.add(activity)
        db.session.commit()
        flash('Mark Updated', 'success')
        return redirect(url_for('comp_rec2', student_id=record.student_id))

       

@app.route("/activity", methods=['GET'])
@login_required
def activity():
    if current_user.level == 1 or current_user.level == 2:
        records = Activity.query.all()
        return render_template('activity.html', title='Activity.html', Activity=records)
    else:
        flash('ONLY CLINICIANS CAN ACCESS THIS PAGE','danger')
    return redirect(url_for('home'))

@app.route("/export", methods=['POST', 'GET'])
@login_required
def export():
    return render_template('export.html', title='Export.html')
    

@app.route("/handson_view", methods=['GET'])
def handson_table():
    return excel.make_response_from_tables(db.session, [Competancy_rec], 'handsontable.html')

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext 
    picture_path = os.path.join(app.root_path, 'static/profilepics', picture_fn)

    output_size =(125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn

@app.route("/accmgmt", methods=['GET', 'POST'])
@login_required
def accmgmt():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file =save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('accmgmt'))
        
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profilepics/'+current_user.image_file)
    return render_template('accmgmt.html', title='Account Management', image_file=image_file, form=form)

@app.route("/chngpw", methods=['GET', 'POST'])
@login_required
def chngpw():
    form = ChangePasswordForm()
    if form.validate_on_submit():
           
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        flash('Your password has been changed', 'success')
        return redirect(url_for('accmgmt'))

    image_file = url_for('static', filename='profilepics/'+current_user.image_file)
    return render_template('chngpw.html', title='PasswordChangehtml', form=form, image_file=image_file)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    if current_user.level == 1 or current_user.level == 2:
        form = PostForm()
        if form.validate_on_submit():
            post = Post3(title=form.title.data, content=form.content.data, author=current_user.username, user_id=current_user.id, image_file=current_user.image_file)
            db.session.add(post)
            db.session.commit()
            flash('Your Post has been created', 'success')
            return redirect(url_for('home'))
        return render_template('create_post.html', title='New Post', form=form, legend='New Notification')
    else:
        flash('ONLY CLINICIANS CAN POST NOTIFICATIONS','danger')
    return redirect(url_for('home'))

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post3.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post3.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)
    
    form= PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your Notification has been Updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', 
                          form=form, legend='Update Notification')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    if current_user.level == 1 or current_user.level == 2:
        post = Post3.query.get_or_404(post_id)
        if post.user_id != current_user.id:
            abort(403)
        db.session.delete(post)
        db.session.commit()
        flash('Your Notification has been Deleted', 'success')
        return redirect(url_for('home'))
    else:
        flash('ONLY CLINICIANS HAVE THE ABILITY TO DELETE NOTIFICATIONS','danger')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):
    page= request.args.get('page', 1, type=int)
    user = User2.query.filter_by(username=username).first_or_404()
    posts = Post3.query.filter_by(author=user.username)\
        .order_by(Post3.date_posted.desc())\
        .paginate(page=page, per_page=4)
    
    return render_template('user_posts.html', posts=posts, user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])

    msg.body = f'''To reset your password visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then ignore this email and no changes will be made
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User2.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title="Reset Password", form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User2.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your Password has been reset', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title="Reset Password", form=form)

@app.route("/comp/new", methods=['GET', 'POST'])
@login_required
def new_comp():
    if current_user.level == 1:
        form = NewCompForm()
        if form.validate_on_submit():
            comp = Comp(descrip=form.content.data, code=form.compid.data, rot_name=form.rotation.data)
            db.session.add(comp)
            db.session.commit()
            activity = Activity(activityType='ACP', actionID=form.compid.data, clincianID=current_user.id)
            db.session.add(activity)
            db.session.commit()
            flash('The Competancy has been added to the Database', 'success')
            return redirect(url_for('rotations'))
        return render_template('new_comp.html', title="New Competancy", form=form, legend='Add a new Competancy to the Database')
    else:
        flash('ONLY ADMINS CAN ADD NEW COMPETENCIES','danger')
    return redirect(url_for('home'))


@app.route("/comp/<comp_id>/update", methods=['GET', 'POST'])
@login_required
def update_comp(comp_id):
    if current_user.level == 1:
        comp = Comp.query.filter_by(id=comp_id).first()
    
        form= EditCompForm()
        if form.validate_on_submit():
            comp.descrip = form.content.data
        
            db.session.commit()
            activity = Activity(activityType='UCP', actionID=comp_id, clincianID=current_user.id)
            db.session.add(activity)
            db.session.commit()

            flash('The Competancy has been updated', 'success')
            return redirect(url_for('rotations', comp_id=comp.id))
        elif request.method == 'GET':
        
            form.content.data = comp.descrip
        
        return render_template('editcomp.html', title='Update Competancy', 
                            form=form, legend='Edit a Competancy')
    else:
        flash('ONLY ADMINS CAN UPDATE COMPETENCIES','danger')
    return redirect(url_for('home'))

@app.route("/comp/<comp_id>/delete", methods=['POST'])
@login_required
def delete_comp(comp_id):
    if current_user.level == 1:
        comp = Comp.query.filter_by(id=comp_id).first()
        db.session.delete(comp)
        db.session.commit()
        activity = Activity(activityType='DCP', actionID=comp_id, clincianID=current_user.id)
        db.session.add(activity)
        db.session.commit()
        flash('The Competancy has been Deleted', 'success')
        return redirect(url_for('rotations'))
    else:
        flash('ONLY ADMINS CAN DELETE COMPETENCIES','danger')
    return redirect(url_for('home'))

@app.route("/user/<int:user_id>/delete", methods=['POST'])
@login_required
def delete_user(user_id):
    user = User2.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    activity = Activity(activityType='DU', actionID=user.id, clincianID=current_user.id)
    db.session.add(activity)
    db.session.commit()
    flash('The User Account has been Deleted', 'success')
    return redirect(url_for('competancy'))

@app.route("/student/new", methods=['GET', 'POST'])
@login_required
def new_student():
    if current_user.level == 1:
        form = NewStudentForm()
        if form.validate_on_submit():
            student = Student(studentid=form.studentid.data, name=form.name.data, date_enrolled=form.dateenrolled.data, email=form.email.data)
            hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
            comp_tbl = Comp.query.all()
            s = User2(username=form.studentid.data, email=form.email.data, level=3, rotation1='Student', rotation2=form.studentid.data, password=hashed_password) # automatically adding students user accounts
            db.session.add(s)
            db.session.commit()
            for c in comp_tbl:
                d = Competancy_rec(mark=0, comp_id=c.descrip, comp_name=c.rot_name, clinician_id=current_user.id, student_id=form.studentid.data) #automatically building comp rec table for each student
                db.session.add(d)
            db.session.commit()
            db.session.add(student)
            db.session.commit()
            activity = Activity(activityType='ASS', actionID=form.studentid.data, clincianID=current_user.id)
            db.session.add(activity)
            db.session.commit()
            flash('The Student has been added to the Database', 'success')
            return redirect(url_for('students'))
        return render_template('new_student.html', title="New Student", form=form, legend='Add a new Student to the Database')
    else:
        flash('ONLY CLINICIANS CAN VIEW THIS PAGE','danger')
        return redirect(url_for('home'))

def calc_percent(studentid):

    records= Competancy_rec.query.filter_by(student_id=studentid).all()
    tcount = 0 #total count
    mcount = 0 #mark count
    percent = 0 #percentage

    for val in records:
        tcount=tcount+1
        if val.mark == 1:
            mcount = mcount+1

    percent = (mcount/tcount) * 100         
    percent = round(percent, 2)

    return percent 


def email_blast():

    students = Student.query.all()
    
    percent = 0
    for val in students:
        percent = calc_percent(val.studentid)
        if percent < 100:

            msg = Message('Outstanding competancies not signed', sender='noreply@uwivetapp.com', recipients=[val.email])
            msg.body = f'''This message serves as a reminder that there are outstanding compentacies on your record that have not been signed
you are currently {percent}% complete please log in the UWI vet app to view your progress in detail
Please try to complete these competencies before the term ends.
'''
            mail.send(msg)

def email_timer():
    now = datetime.utcnow
    limit = datetime(2019, 9, 1, 16, 26, 0)
    if now == limit:
        email_blast()
