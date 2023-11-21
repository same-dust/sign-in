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
        # # print(type(data)) # <class 'dict'>
        user_id=data.get('id') # 获取用户id，与课程老师表关联
        print(user_id)
        building=data.get('building') # 教学楼,eg:东三
        week=data.get('time1') # 周几，eg：周五
        time_period=data.get('time2') # 时间段，eg：一二节
        classroom=data.get('classroom') # 教室 eg：305
        # print(building)
        # print(week)
        # print(time_period)
        # print(classroom)
        jsonData = data.get('jsonData')
        # print(type(jsonData)) # <class 'str'>
        data=json.loads(jsonData)
        print(data)
        course=data.get('课程名称')
        teacher=data.get('任课教师')
        stu_roster=data.get('学生名单')
        print(course)
        print(teacher)
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

        for stu in stu_roster:
            print(stu.get('学号'))
            print(stu.get('姓名'))
            student=Student.query.filter_by(stu_no=stu.get('学号')).first()
            if student: # 如果该学生存在,拿到其id与课程老师表通过学生选课表进行绑定
                stu_id=student.id
                new_ct_s=CourseTeacher_Student(student_id=stu_id,course_teacher_id=ct_id) 
                db.session.add(new_ct_s)
                db.session.commit()
            else: # 不存在就添加这个学生的信息到数据库
                new_student=Student(stu_no=stu.get('学号'),name=stu.get('姓名'))
                db.session.add(new_student)
                db.session.commit()
                stu_id=new_student.id
                new_ct_s=CourseTeacher_Student(student_id=stu_id,course_teacher_id=ct_id)
                db.session.add(new_ct_s)
                db.session.commit()
        
        return {'course_id':ct_id,'msg':'课程创建成功'}

        
class rosterForTeacher(Resource):
    def get(self):
        ct_id=request.args.get('course_id')
        ct_stus=CourseTeacher_Student.query.filter_by(course_teacher_id=ct_id).all()
        stu_informations=list()
        for ct_stu in ct_stus:
            stu=Student.query.filter_by(id=ct_stu.student_id).first()
            stu_informations.append({'stu_no':stu.stu_no,'stu_name':stu.name})
        return {'stu_informations':stu_informations}
    
    def post(self): # 点完名后，需要传入课程id，缺勤学生名单（含学号），日期，更新缺勤信息，缺勤次数加一，缺勤表添加一条数据：缺勤日期，学生选课表id
        data=request.get_json()
        print(data)
        ct_id=data.get('course_id') # 获取课程id
        stu_list=data.get('stu_list') # 获取缺勤名单
        date=data.get('date') # 获取当前日期:yyyy-mm-dd 格式
        msg=list()
        flag=True
        for stu in stu_list:
            stu_no=stu.get('学号')
            student=Student.query.filter_by(stu_no=stu_no).first() # 找到该名学生
            if student:
                stu_id=student.id # 获取学生id
                ct_stu=CourseTeacher_Student.query.filter_by(course_teacher_id=ct_id,student_id=stu_id).first()
                if ct_stu:
                    ct_stu.absence_count+=1 # 该名学生本课程缺勤次数加1
                    new_ad=Absence_Details(Specific_dates=date,ct_s_id=ct_stu.id) # 在缺勤详情表添加一条数据，记录每次缺勤的日期
                    db.session.add(new_ad)
                    db.session.commit()
                else:
                    msg.append('学号为'+stu_no+'的学生不在该课程中')
                    flag=False
            else:
                msg.append('学号为'+stu_no+'的学生不存在')
                flag=False
        if flag:
            return {'msg':'缺勤信息已经成功导入'}
        return {'msg':msg}



class renderHomeCourse(Resource):
    def get(self):
        user_id=request.args.get('user_id')# 把用户的id传入进来
        week=request.args.get('week') # 周几
        cts=CourseTeacher.query.filter_by(user_id=user_id).all()
        informations=list() # 存储课程相关信息，例如：课程名，上课的时间和地点
        for ct in cts:
            tp_id=Scheduling.query.filter_by(course_teacher_id=ct.id).first().time_place_id
            tp=TimePlace.query.filter_by(id=tp_id).first()
            if tp.week_name!=week:  # 只返回指定时间(周几)的课程
                continue
            information={'course_id':ct.id,'course':ct.course,'building':tp.building,'classroom':tp.classroom,'week':tp.week_name,'time_period':tp.time_period}
            informations.append(information)
        return {'Course_informations':informations}
    
class renderMineCourse(Resource):
    def get(self):
        user_id=request.args.get('user_id')# 把用户的id传入进来
        cts=CourseTeacher.query.filter_by(user_id=user_id).all()
        informations=list() # 存储课程相关信息，例如：课程名，上课的时间和地点
        for ct in cts:
            tp_id=Scheduling.query.filter_by(course_teacher_id=ct.id).first().time_place_id
            tp=TimePlace.query.filter_by(id=tp_id).first()
            information={'course_id':ct.id,'course':ct.course,'building':tp.building,'classroom':tp.classroom,'week':tp.week_name,'time_period':tp.time_period}
            informations.append(information)
        return {'Course_informations':informations}
    
class courseAbsences(Resource):
    def get(self):
        ct_id=request.args.get('course_id')
        ct_stus=CourseTeacher_Student.query.filter_by(course_teacher_id=ct_id).all()
        stu_absences=list()
        for ct_stu in ct_stus:
            if ct_stu.absence_count==0: # 缺勤为0则跳过该名学生
                continue
            stu=Student.query.filter_by(id=ct_stu.student_id).first() 
            details=Absence_Details.query.filter_by(ct_s_id=ct_stu.id).all()
            dates=list()
            for detail in details:
                dates.append(detail.Specific_dates)

            stu_absence={'student_number':stu.stu_no,'student_name':stu.name,'absence_count':ct_stu.absence_count,'details':dates}
            stu_absences.append(stu_absence)
        return {'Student_absences':stu_absences}


