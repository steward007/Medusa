#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import HttpResponse,JsonResponse
from ClassCongregation import ErrorLog
import json
import base64
from Web.DatabaseHub import FishingData,UserInfo
from Web.Workbench.LogRelated import UserOperationLogRecord,RequestLogRecord
import re
"""
http://127.0.0.1:9999/b/aaaaaaaaaa/?dasd=dasd
"""
def Monitor(request,data):#用于接收信息的监控
    RequestLogRecord(request, request_api="email")
    GetRequestFragment=""
    try:
        GetRequestFragment = re.search(r'/[a-zA-Z0-9]{10}', str(request.get_full_path), re.I).group(0)  # 对URL进行提取处理
        #print(GetRequestFragment[1:11])
    except Exception as e:
        ErrorLog().Write("Web_Mail_FishingData_Monitor(def)-GetRequestFragment", e)

    if request.method == "POST":
        try:

            if request.headers["Content-Type"]=="application/json":
                DataPackInfo = request.body#获取post数据包信息
            else:
                DataPackInfo = str(request.POST.dict()).encode('utf-8')#转换成字典后再换装byte类型穿给加密函数
            HeadersInfo = str(request.headers).encode('utf-8')#获取头信息
            FishingData().Write(full_url=str(request.build_absolute_uri()),
                                request_method="POST",request_key=GetRequestFragment[1:11],headers_info=base64.b64encode(HeadersInfo).decode('utf-8'),data_pack_info=base64.b64encode(DataPackInfo).decode('utf-8'))
        except Exception as e:
            ErrorLog().Write("Web_Mail_FishingData_Monitor(def)-POST", e)
    elif request.method == "GET":
        try:
            ParameterInfo=str(request.GET.dict()).encode('utf-8')#获取参数信息
            HeadersInfo=str(request.headers).encode('utf-8')#获取头信息
            FishingData().Write(full_url=str(request.build_absolute_uri()),
                                request_method="GET",request_key=GetRequestFragment[1:11],headers_info=base64.b64encode(HeadersInfo).decode('utf-8'),data_pack_info=base64.b64encode(ParameterInfo).decode('utf-8'))

        except Exception as e:
            ErrorLog().Write("Web_Mail_FishingData_Monitor(def)-GET", e)

    return HttpResponse("")


"""mail_receive_data_statistics
{
	"token": "xxx",
	"request_key":"aaaaaaaaaa"
}
"""
def DataStatistics(request):#统计邮件获取到的数据
    RequestLogRecord(request, request_api="mail_receive_data_statistics")
    if request.method == "POST":
        try:
            Token=json.loads(request.body)["token"]
            RequestKey = json.loads(request.body)["request_key"]
            Uid = UserInfo().QueryUidWithToken(Token)  # 如果登录成功后就来查询UID
            if Uid != None:  # 查到了UID
                UserOperationLogRecord(request, request_api="mail_receive_data_statistics", uid=Uid)  # 查询到了在计入
                Result=FishingData().Quantity(request_key=RequestKey)
                return JsonResponse({'message': Result, 'code': 200, })
            else:
                return JsonResponse({'message': "小宝贝这是非法查询哦(๑•̀ㅂ•́)و✧", 'code': 403, })
        except Exception as e:
            ErrorLog().Write("Web_Mail_MailReceiveData_DataStatistics(def)", e)
            return JsonResponse({'message': '自己去看报错日志！', 'code': 169, })

    else:
        return JsonResponse({'message': '请使用Post请求', 'code': 500, })

"""mail_receive_data_details
{
	"token": "xxx",
	"request_key":"aaaaaaaaaa",
	"number_of_pages":"1"
}
"""
def DataDetails(request):#邮件获取的数据详情
    RequestLogRecord(request, request_api="mail_receive_data_details")
    if request.method == "POST":
        try:
            Token=json.loads(request.body)["token"]
            RequestKey = json.loads(request.body)["request_key"]
            NumberOfPages=json.loads(request.body)["number_of_pages"]
            Uid = UserInfo().QueryUidWithToken(Token)  # 如果登录成功后就来查询UID
            if Uid != None:  # 查到了UID
                UserOperationLogRecord(request, request_api="mail_receive_data_details", uid=Uid)  # 查询到了在计入
                if int(NumberOfPages)>0:
                    Result=FishingData().Query(request_key=RequestKey,number_of_pages=int(NumberOfPages))
                    return JsonResponse({'message': Result, 'code': 200, })
                else:
                    return JsonResponse({'message': "你家页数是负数的？？？？", 'code': 400, })
            else:
                return JsonResponse({'message': "小宝贝这是非法查询哦(๑•̀ㅂ•́)و✧", 'code': 403, })
        except Exception as e:
            ErrorLog().Write("Web_Mail_MailReceiveData_DataDetails(def)", e)
            return JsonResponse({'message': '自己去看报错日志！', 'code': 169, })

    else:
        return JsonResponse({'message': '请使用Post请求', 'code': 500, })
