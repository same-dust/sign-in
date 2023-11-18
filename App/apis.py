from flask import jsonify,request
from flask_restful import Resource, fields, marshal_with, reqparse
from .models import *
import json

class loginResource(Resource):
    def post(self):
        data = request.get_json()
        print(data)
        # print(type(data))
        print('username:'+data['username'])
        user = User.query.filter_by(username=data['username']).first() # 找寻此用户
        print(user)
        if user: # 如果用户存在
            if user.check_password(data['password']): # 如果密码正确
                print(user.userpwd)
                print(data['password'])
                return {'msg': '登录成功','data':{'username':user.username,'id':user.id,'type':user.user_type},'status':'success'}
            else:
                print(2)
                return {'msg': '用户名或密码错误','status':'fail'}
        else: # 用户不存在，即第一次登录，将把信息存入数据库
            
            new_user = User(username=data['username'],userpwd=data['password'],user_type=data['type'])
            db.session.add(new_user)
            db.session.commit()
            return {'msg': '登录成功','data':{'username':new_user.username,'id':new_user.id,'type':new_user.user_type},'status':'success'}




class gradeResource(Resource):
    def get(self):
        grades=Grade.query.all()
        grade_data=[{'id':grade.id,'name':grade.name} for grade in grades]
        return jsonify({'msg': 'get请求','data':grade_data})


class linkResource(Resource):
    def post(self):
        data=request.get_json()
        # print(data)
        print(type(data)) # <class 'dict'>
        user_id=data.get('id') # 获取用户id，与课程老师表关联
        teacher=data.get('teachername') # 老师姓名
        course=data.get('classname') # 课程名，可重复，ke班软工!=cheng班软工
        classroom=data.get('classroom') # 教室 eg：东三305
        week=data.get('time1') # 周几，eg：周五
        time_period=data.get('time2') # 时间段，eg：一二节
        print(type(classroom)) # <class 'str'>
        building=classroom[0:2]
        classroom=classroom[2:]
        # print(building)
        # print(classroom)
        new_ct=CourseTeacher(teacher=teacher,course=course,user_id=user_id) # 创建课程教师对象
        new_tp=TimePlace(building=building,classroom=classroom,week_name=week,time_period=time_period) # 创建时间地点对象
        db.session.add(new_ct)
        db.session.add(new_tp)
        db.session.commit() # 上传到数据库

        ct_id=new_ct.id
        tp_id=new_tp.id
        print(ct_id)
        print(tp_id)
        # 往（scheduling表）中间表添加数据，建立课程教室和时间地点的关联
        new_scheduling=Scheduling(course_teacher_id=ct_id,time_place_id=tp_id)
        db.session.add(new_scheduling)
        db.session.commit()

        jsonData = data.get('jsonData')
        # print(type(jsonData)) # <class 'str'>
        Data = json.loads(jsonData).get('Sheet1')
        # print(type(Data)) # <class 'list'>
        msg=list() # 空列表，用于返回消息
        flag=True
        for item in Data: # 每个学生的学号与姓名
            stu_no=item.get('学号')
            student=Student.query.filter_by(stu_no=stu_no).first() # 找寻对应学号的学生
            if student: # 如果该学生存在,拿到其id与课程老师表通过学生选课表进行绑定
                stu_id=student.id
                new_ct_s=CourseTeacher_Student(student_id=stu_id,course_teacher_id=ct_id) 
                db.session.add(new_ct_s)
                db.session.commit()
            else:
                flag=False # 有学生没有关联上（数据库不存在此学生）
                msg.append(f'数据库中没有存储学号为{stu_no}的学生')

        if flag:
            msg.append('所有学生信息导入成功')
            return {'msg':msg,'course_id':ct_id}
        return {'msg':msg,'course_id':ct_id}
        
class rosterForTeacher(Resource):
    def get(self):
        ct_id=request.args.get('course_id')
        ct_stus=CourseTeacher_Student.query.filter_by(course_teacher_id=ct_id).all()
        stu_informations=list()
        for ct_stu in ct_stus:
            stu=Student.query.filter_by(id=ct_stu.student_id).first()
            stu_informations.append({'stu_no':stu.stu_no,'stu_name':stu.name})
        return {'stu_informations':stu_informations}


class renderCourse(Resource):
    def get(self):
        user_id=request.args.get('user_id')# 把用户的id传入进来
        cts=CourseTeacher.query.filter_by(user_id=user_id).all()
        informations=list() # 存储课程相关信息，例如：课程名，上课的时间和地点
        for ct in cts:
            tp_id=Scheduling.query.filter_by(course_teacher_id=ct.id).first().time_place_id
            tp=TimePlace.query.filter_by(id=tp_id).first()
            information={'course_id':ct.id,'course':ct.course,'building':tp.building,'classroom':tp.classroom,'week':tp.week_name,'time_period':tp.time_period}
            informations.append(information)
        return {'Course-informations':informations}
    
    
    
    
    # def post(self):
    #     data = request.get_json()

    #     # 获取用户输入的 classname
    #     classname = data.get('name')

    #     # 创建一个新的 Grade 对象并将其添加到数据库
    #     new_grade = Grade(name=classname)
    #     db.session.add(new_grade)
    #     db.session.commit()

    #     return jsonify({'msg': 'post请求', 'data': {'classname': classname}})























# # 类视图： CBV   Class Based View
# # 视图函数： FBV  Function Based View
# class HelloResouce(Resource):
#     def get(self):
#         return jsonify({'msg': 'get请求'})

#     def post(self):
#         return jsonify({'msg': 'post请求'})

# # --------------------------- 字段格式化 --------------------------- #

# # Flask-RESTful
# # 字段格式化：定义返回给前端的数据格式
# ret_fields = {
#     'status': fields.Integer,
#     'msg': fields.String,
#     # 'data': fields.String,
#     'like': fields.String(default='ball'),
#     'like2': fields.String(),
#     'data2': fields.String(attribute='data')  # 使用data的值
# }

# class UserResource(Resource):
#     @marshal_with(ret_fields)
#     def get(self):
#         return {
#             'status': 1,
#             'msg': 'ok',
#             'data': '千锋教育Python'
#         }


# # --------------------------- 字段格式化 --------------------------- #

# #
# user_fields = {
#     # 'id': fields.Integer,
#     'name': fields.String,
#     'age': fields.Integer,
#     # 绝对路径
#     'url': fields.Url(endpoint='id', absolute=True)
# }
# ret_fields2 = {
#     'status': fields.Integer,
#     'msg': fields.String,
#     # user对象
#     'data': fields.Nested(user_fields)
# }

# class User2Resource(Resource):
#     @marshal_with(ret_fields2)
#     def get(self):
#         user = User.query.first()
#         return {
#             'status': 1,
#             'msg': 'ok',
#             'data': user
#         }

# # --------------------------- 字段格式化 --------------------------- #
# user_fields2 = {
#     'name': fields.String,
#     'age': fields.Integer,
# }
# ret_fields3 = {
#     'status': fields.Integer,
#     'msg': fields.String,
#     'data': fields.List(fields.Nested(user_fields2))
# }

# class User3Resource(Resource):
#     @marshal_with(ret_fields3)
#     def get(self):
#         users = User.query.all()
#         return {
#             'status': 1,
#             'msg': 'ok',
#             'data': users
#         }


# # --------------------------- 参数解析 --------------------------- #
# # 参数解析：解析前端发送过来的数据
# parser = reqparse.RequestParser()
# parser.add_argument('name', type=str, required=True, help='name是必需的参数')
# parser.add_argument('age', type=int, action='append')  # 可以有多个age
# parser.add_argument('key', type=str, location='cookies')  # 可以有多个age

# class User4Resource(Resource):
#     def get(self):
#         # 获取参数
#         args = parser.parse_args()
#         name = args.get('name')
#         age = args.get('age')
#         key = args.get('key')

#         return jsonify({"name": name, 'age': age, 'key': key})



