from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User2.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return "User "+self.username+" "+self.email+" "+self.image_file+""

class User2(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    level = db.Column(db.Integer, nullable=False, default='2')
    rotation = db.Column(db.String(50), nullable =False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
        
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User3.query.get(user_id)
    
    def __repr__(self):
        return "User2 "+self.username+" "+self.email+" "+self.image_file+" "
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100),nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Post3(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100),nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable = False)
    author = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    image_file = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Competancy_rec(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement="auto")
    mark = db.Column(db.Boolean, nullable = True )
    comp_id = db.Column(db.String, db.ForeignKey('comp.descrip'), nullable=False)
    clinician_id = db.Column(db.Integer, db.ForeignKey('user2.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
   
    def __repr__(self):
        return f"Comp_rec('{self.id}', '{self.mark}', '{self.comp_id}', '{self.clinician_id}', '{self.student_id}', '{self.timestamp}')"

class Comp(db.Model):
    descrip = db.Column(db.String, primary_key = True)
    id = db.Column(db.String)
    rot_name = db.Column(db.String(50))
    
    def __init__(self, descrip, code="", rot_name=""):
        self.descrip = descrip
        self.id = code
        self.rot_name = rot_name

    def __repr__(self):
        return f"Comp('{self.descrip}', '{self.id}', '{self.rot_name}')"

class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=False)
    name = db.Column(db.String(100),nullable=False)
    date_enrolled = db.Column(db.String(100),nullable=False)#(db.DateTime, nullable=False, default=datetime.utcnow)
    email = db.Column(db.String(100),nullable=False)
    
    def __init__(self, id, name=' ', date_enrolled=' ', email=' '):
        self.id = id
        self.name = name
        self.date_enrolled = date_enrolled
        self.email = email
    
    def __repr__(self):
        return f"Student('{self.id}','{self.name}', '{self.date_enrolled}', '{self.email}', {self.competancy_rec}')"

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    activityType = db.Column(db.String(10))
    actionID = db.Column(db.Integer)
    clincianID = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    
    def __init__(self, activityType='', actionID='', clincianID=''):
        self.activityType = activityType
        self.actionID= actionID
        self.clincianID = clincianID

    def __repr__(self):
        return f"Activity('{self.id}', '{self.activityType}', '{self.actionID}', '{self.clincianID}')"