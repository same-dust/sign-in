# urls.py  路由文件

from .exts import api
from .apis import *

# # 路由

api.add_resource(loginResource,'/apis/login/')  # 用于用户登录
api.add_resource(gradeResource,'/apis/grade/')  # 用于获取辅导员所管理的自然班，辅导员端导入创建自然班，并导入自然班学生名单
api.add_resource(linkResource,'/apis/link/')  # 创建课程信息，将时间地点，课程老师，还有学生关联起来，查询所有课程
api.add_resource(renderHomeCourse,'/apis/tHome/') # 老师首页显示的课程(根据时间显示)
api.add_resource(renderMineCourse,'/apis/tMine/') # 老师我的显示的课程，所有课程
api.add_resource(rosterForTeacher,'/apis/cRoster/') # 课程的花名册
api.add_resource(courseAbsences,'/apis/cAbsencesForT/') # 老师端的基于课程的缺勤名单
api.add_resource(leaveResource,'/apis/leave/') # 请假消息消息的推送与确认
api.add_resource(TodayAbsencePush,'/apis/absencePush/') # 缺勤消息推送
api.add_resource(test,'/apis/test/')


