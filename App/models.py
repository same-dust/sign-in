from .exts import db


class Absence_Details(db.Model):
    __tablename__ = 'absence_details'
    id = db.Column(db.Integer, primary_key=True, comment='Primary Key')
    Specific_dates = db.Column(db.String(42), nullable=False, comment='具体日期')
    ct_s_id = db.Column(db.Integer, db.ForeignKey('courseteacher_student.id'), nullable=False, comment='外键,关联学生选课表的id')


class StudentAbsences(db.Model):
    __tablename__ = 'student_absences'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='Primary Key')
    ab_date = db.Column(db.String(20), nullable=False, comment='缺勤日期')
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False, comment='外键')
    course_id = db.Column(db.Integer, db.ForeignKey('courseteacher.id'), nullable=False, comment='外键')
    ab_time = db.Column(db.String(20), nullable=False, comment='具体时间')
    place = db.Column(db.String(20), nullable=False, comment='地点')

    student = db.relationship('Student', backref='absences')  # 学生和缺勤表的关系
    course_teacher = db.relationship('CourseTeacher', backref='absences')  # 课程和缺勤表的关系


class CourseTeacher_Student(db.Model):
    __tablename__ = 'courseteacher_student'
    id = db.Column(db.Integer, primary_key=True)
    absence_count = db.Column(db.Integer,default=0)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    course_teacher_id = db.Column(db.Integer, db.ForeignKey('courseteacher.id'))
    absence_details = db.relationship('Absence_Details', backref='courseteacher_student', lazy=True)

class Scheduling(db.Model):
    __tablename__ = 'scheduling'
    id = db.Column(db.Integer, primary_key=True)
    time_place_id = db.Column(db.Integer, db.ForeignKey('timeplace.id'))
    course_teacher_id = db.Column(db.Integer, db.ForeignKey('courseteacher.id'))


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username=db.Column(db.String(30))
    userpwd=db.Column(db.String(30))
    user_type=db.Column(db.Integer)
    courses=db.relationship('CourseTeacher',backref='user',lazy=True)
    grades=db.relationship('Grade',backref='user',lazy=True)
    def check_password(self, password):
        return self.userpwd == password

class Grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(30),unique=True)
    admission_year=db.Column(db.String(11),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    students = db.relationship('Student', backref='grade', lazy=True)

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(30))
    stu_no=db.Column(db.String(20),unique=True)
    Absence=db.Column(db.Integer,default=0)
    # 外键：跟Grade表中的id字段关联
    grade_id = db.Column(db.Integer, db.ForeignKey(Grade.id))


class Leave_msg(db.Model):
    __tablename__ = 'leave_msg'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    leave_date = db.Column(db.String(42), nullable=False)  # 对应请假日期字段
    student_id = db.Column(db.Integer, db.ForeignKey(Student.id), nullable=False)  # 对应外键字段，关联学生表
    course_id=db.Column(db.Integer,db.ForeignKey('courseteacher.id'),nullable=False) # 关联课程老师表
    student = db.relationship('Student', backref='leave_messages')  # 声明与Student表的关系，可以通过leave_messages访问请假学生的信息



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



    





