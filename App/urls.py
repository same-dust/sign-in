# urls.py  路由文件

from .exts import api
from .apis import *

# # 路由
# api.add_resource(HelloResouce, '/hello/')
# api.add_resource(UserResource, '/user/', endpoint='id')

api.add_resource(loginResource,'/apis/login/')  # 用于用户登录
api.add_resource(gradeResource,'/apis/grade/')  # 用于获取自然班
api.add_resource(linkResource,'/apis/link/')  # 导入信息，将时间地点，课程老师，还有学生关联起来
api.add_resource(renderCourse,'/apis/tRender/') # 老师的课程
api.add_resource(rosterForTeacher,'/apis/cRoster/') # 课程的花名册