from .exts import db


class CourseTeacher_Student(db.Model):
    __tablename__ = 'courseteacher_student'
    id = db.Column(db.Integer, primary_key=True)
    absence_count = db.Column(db.Integer)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    course_teacher_id = db.Column(db.Integer, db.ForeignKey('courseteacher.id'))

class Scheduling(db.Model):
    __tablename__ = 'scheduling'
    id = db.Column(db.Integer, primary_key=True)
    time_place_id = db.Column(db.Integer, db.ForeignKey('timeplace.id'))
    course_teacher_id = db.Column(db.Integer, db.ForeignKey('courseteacher.id'))


class Grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(30),unique=True)
    # 建立关联
    #   第1个参数：关联的模型名（表）
    #   第2个参数：反向引用的名称，grade对象，
    #             让student去反过来得到grade对象的名称： student.grade
    #   第3个参数：懒加载
    # 这里的students不是字段
    students = db.relationship('Student', backref='grade', lazy=True)

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(30))
    stu_no=db.Column(db.String(20),unique=True)
    Absence=db.Column(db.Integer)
    # 外键：跟Grade表中的id字段关联
    grade_id = db.Column(db.Integer, db.ForeignKey(Grade.id))

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username=db.Column(db.String(30))
    userpwd=db.Column(db.String(30))
    user_type=db.Column(db.Integer)
    courses=db.relationship('CourseTeacher',backref='user',lazy=True)
    def check_password(self, password):
        return self.userpwd == password

class CourseTeacher(db.Model):
    __tablename__ = 'courseteacher'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    teacher=db.Column(db.String(30))
    course=db.Column(db.String(42))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)

class TimePlace(db.Model):
    __tablename__ = 'timeplace'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    week_name=db.Column(db.String(11))
    time_period=db.Column(db.String(11))
    building=db.Column(db.String(11))
    classroom=db.Column(db.String(11))



    





