from flask import jsonify,request
from flask_restful import Resource, fields, marshal_with, reqparse
from .models import *
import json

class loginResource(Resource):
    def post(self): # 登录
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
    def get(self): # 获取用户管理的自然班信息
        user_id=request.args.get('user_id')
        grades=Grade.query.filter_by(user_id=user_id).all()
        grade_data=[{'id':grade.id,'name':grade.name,'admission_year':grade.admission_year} for grade in grades]
        return jsonify({'gradeData':grade_data})
    
    def post(self): # 创建自然班，绑定用户，绑定学生
        data=request.get_json()
        user_id=data.get('user_id') # 获取辅导员用户的id
        jsonData=data.get('jsonData')
        stu_roster=json.loads(jsonData)
        for stu in stu_roster:
            grade=stu.get('班级')
            stu_no=stu.get('学号')
            stu_name=stu.get('姓名')
            admission_year=grade[:5] # 2021级
            gradename=grade[5:] # 计算机类01班
            grade=Grade.query.filter_by(name=gradename,admission_year=admission_year,user_id=user_id).first() # 找到该班级
            if not grade: # 如果该班级不存在，就创建该班级
                grade=Grade(name=gradename,admission_year=admission_year,user_id=user_id)
                db.session.add(grade)
                db.session.commit()
            student=Student.query.filter_by(stu_no=stu_no).first()
            if student:
                student.grade_id=grade.id # 绑定自然班
            else:
                new_student=Student(stu_no=stu_no,name=stu_name,grade_id=grade.id)
                db.session.add(new_student)
                db.session.commit()

        return jsonify({'status':'success'})


class linkResource(Resource):
    def get(self): # 获取所有已创建的课程
        cts=CourseTeacher.query.all()
        informations=list() # 存储课程相关信息，例如：课程名，上课的时间和地点
        for ct in cts:
            tp_id=Scheduling.query.filter_by(course_teacher_id=ct.id).first().time_place_id
            tp=TimePlace.query.filter_by(id=tp_id).first()
            information={'course_id':ct.id,'course':ct.course,'building':tp.building,'classroom':tp.classroom,'week':tp.week_name,'time_period':tp.time_period}
            informations.append(information)
        return {'Course_informations':informations}


    def post(self): # 创建课程，进行一系列的绑定
        data=request.get_json()
        user_id=data.get('id') # 获取用户id，与课程老师表关联
        usertype=data.get('usertype') # 督导队or老师
        if usertype: # 老师的用户类型为0，如果if条件成立，说明不是老师
            user_id=None
        building=data.get('building') # 教学楼,eg:东三
        week=data.get('time1') # 周几，eg：周五
        time_period=data.get('time2') # 时间段，eg：一二节
        classroom=data.get('classroom') # 教室 eg：305
        jsonData = data.get('jsonData')
        # print(type(jsonData)) # <class 'str'>
        data=json.loads(jsonData)
        course=data.get('课程名称')
        teacher=data.get('任课教师')
        stu_roster=data.get('学生名单')
        
        # 先查询是否已经存在匹配的排课项
        schedule = Scheduling.query.join(CourseTeacher).join(TimePlace).filter(
            CourseTeacher.course == course,
            CourseTeacher.teacher == teacher,
            TimePlace.building == building,
            TimePlace.classroom == classroom,
            TimePlace.week_name == week,
            TimePlace.time_period == time_period
        ).first()
        if schedule: # 如果排课表有此信息，说明课程已经存在
            ct=CourseTeacher.query.filter_by(id=schedule.course_teacher_id).first() # 找到已存在的课程
            if user_id and ct.user_id==None: # 如果是老师打算创建已存在的课程(且该课程是督导队创建的，即user_id为空)
                ct.user_id=user_id
                db.session.commit()
                return {'msg':'课程被督导队创建,现在已经找回'}
            else: # 如果是督导队，无需做任何操作
                return {'msg':'课程已经存在'}

        new_ct=CourseTeacher(teacher=teacher,course=course,user_id=user_id) # 创建课程教师对象
        new_tp=TimePlace(building=building,classroom=classroom,week_name=week,time_period=time_period) # 创建时间地点对象
        db.session.add(new_ct)
        db.session.add(new_tp)
        db.session.commit() # 上传到数据库

        ct_id=new_ct.id
        tp_id=new_tp.id
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
        
        return {'msg':'课程创建成功'}

        
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
        leave_list=data.get('leave_list') # 获取请假名单
        date=data.get('date') # 获取当前日期:yyyy-mm-dd 格式
        place=data.get('place') # 缺勤地点：东三305
        ab_time=data.get('time') # 缺勤时间：周五三四节
        usertype=data.get('usertype') # int型，0是教师
        print(f'usertype:{usertype}')

        msg=list()
        flag=True

        if not leave_list and not stu_list:
            return {'msg':'无学生请假和缺勤'}
        
        if not leave_list:
            msg.append('无学生请假')
        else:
            for leave in leave_list:
                leave_stu_no=leave.get('学号')
                student=Student.query.filter_by(stu_no=leave_stu_no).first() # 找到该名学生
                if student:
                    new_lea_msg=Leave_msg(leave_date=date,student_id=student.id,course_id=ct_id) # 将请假消息添加到数据库中
                    db.session.add(new_lea_msg)
                    db.session.commit()
                else:
                    msg.append('学号为'+leave_stu_no+'的学生不存在')
        if not stu_list:
            msg.append('无学生缺勤')
        else:            
            for stu in stu_list:
                stu_no=stu.get('学号')
                student=Student.query.filter_by(stu_no=stu_no).first() # 找到该名学生
                if student:
                    if not usertype: # 如果用户类型是老师
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
                    else: # 类型不是老师，就是督导队
                        stu_id=student.id
                        student.Absence+=1 # 缺勤次数加1
                        new_stu_absence=Student_Absences(ab_date=date,student_id=stu_id,course_id=ct_id,place=place,ab_time=ab_time)
                        db.session.add(new_stu_absence)
                        db.session.commit()
                else:
                    msg.append('学号为'+stu_no+'的学生不存在')
                    flag=False
            if flag:
                msg.append('缺勤信息导入成功')
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
            if not tp_id:
                informations.append(f'{ct.course}找不到相关的排课信息')
                continue
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


class leaveResource(Resource):
    def get(self):
        userid=request.args.get('userid') # 获取辅导员id
        grades=Grade.query.filter_by(user_id=userid).all() # 获取该名辅导员管理的所有班级
        grades_id=list() # 用来存储班级id
        message=list() # 返回的信息
        for grade in grades:
            grades_id.append(grade.id)

        leave_messages=Leave_msg.query.all() # 获取所有请假消息
        for msg in leave_messages:
            student=Student.query.filter_by(id=msg.student_id).first() # 找到请假的学生
            if student:
                if student.grade_id in grades_id: # 判断该名学生是否是用户（辅导员）所管理的
                    message.append({'student_number':student.stu_no,'student_name':student.name,'leave_date':msg.leave_date,'message_id':msg.id})

        return {'Leave_messages':message}
    
    def post(self):
        data=request.get_json()
        msg_id=data.get('message_id')
        flag=data.get('flag') # 标志，0为不属实，1为属实
        msg=Leave_msg.query.filter_by(id=msg_id).first()
        if not flag: # 如果不属实，则缺勤次数加1
            student=Student.query.filter_by(id=msg.student_id).first() # 找到该名学生
            ct=CourseTeacher.query.filter_by(id=msg.course_id).first() # 在哪个课程上请假
            if student and ct: # 都不为空
                ct_s=CourseTeacher_Student.query.filter_by(course_id=ct.id,student_id=student.id).first()
                ct_s.absence_count+=1
                new_ad=Absence_Details(Specific_dates=msg.leave_date,ct_s_id=ct_s.id) # 在缺勤详情表添加一条数据，记录每次缺勤的日期
                db.session.add(new_ad)
                db.session.commit()
        
        db.session.delete(msg)
        db.session.commit()
        return {'status':'success'}

class TodayAbsencePush(Resource):
    def get(self):
        user_id=request.args.get('user_id')
        today_date=request.args.get('today_date')
        grades=Grade.query.filter_by(user_id=user_id).all() # 获取该名辅导员管理的所有班级
        grades_id=list() # 用来存储班级id
        today_absence=list() # 用来存储今日缺勤
        for grade in grades:
            grades_id.append(grade.id)
        print(f'today_date:{today_date}')
        student_absences=Student_Absences.query.filter_by(ab_date=today_date).all() # 获取今天所有的缺勤名单
        print(student_absences)
        print(grades_id)
        for absence in student_absences:
            print(f'the student id of absence:{absence.student_id}')
            student=Student.query.filter_by(id=absence.student_id).first()
            print(f'student:{student},grade_id:{student.grade_id}')
            if student:
                if student.grade_id in grades_id:
                    print(student.name,student.stu_no)
                    ct=CourseTeacher.query.filter_by(id=absence.course_id).first() # 获取课程信息
                    today_absence.append({'student_name':student.name,'student_no':student.stu_no,'date':absence.ab_date,'teacher':ct.teacher,'course':ct.course,'place':absence.place,'detail_time':absence.ab_time})
        return {'status':'success','today_absence':today_absence}


class GradeAbsences(Resource):
    def get(self):
        grade_id=request.args.get('id') # 获取班级id
        students=Student.query.filter_by(grade_id=grade_id).all() # 获取该自然班所有学生
        grade_absence=list()  
        for student in students:
            if not student.Absence:
                continue
            absence_detail=list()
            student_absences=Student_Absences.query.filter_by(student_id=student.id).all()
            for absence in student_absences:
                ct=CourseTeacher.query.filter_by(id=absence.course_id).first()
                absence_detail.append({'date':absence.ab_date,'course':ct.course,'place':absence.place})
            grade_absence.append({'student_name':student.name,'student_no':student.stu_no,'absence_count':student.Absence,'absence_detail':absence_detail})
        return {'status':'success','grade_absence':grade_absence}