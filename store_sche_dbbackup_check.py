#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
ZBX 监控脚本
    说明：餐厅数据备份计划任务巡检
    版本说明
    V0.5    20161219    1,检查备份任务的状态；2,检查备份文件是否有检查当天的；
"""

import commands
import sys
import os
import datetime

def execute_sql(v_sql):
    cmd = ("export PGPASSWORD='Yum!P0werFul' ;"
           "psql -U postgres -h localhost -d BOH2G_STORE_WORK -t -c \"" + v_sql + "\" ")
    (status, output) = commands.getstatusoutput(cmd)
    list_ret = [x.strip() for x in output.strip().split("|")]
    if len(list_ret) > 1:
        return list_ret
    else:
        return output.strip()

def sche_dbbackup_check():
    """
        餐厅端数据库备份计划   is_excute (0,1就是运行中，-1已暂停)
    """
    selectsql = ("select is_excute from fnd_t_sch_schedule where sch_name = '餐厅端数据库备份' and del_flag='N';")
    v_result = execute_sql(selectsql)
    return v_result

def file_dbbcakup_check():
    """
        检查数据库备份文件是否产生
        PATH： /home/BOH/YUM/BOH2G/BACKUP/BMP/pgBackUpdir
        文件名称：BOH2G_STORE_DB_20161217001500293.boh(待确认)
    """
    PATH = "/home/BOH/YUM/BOH2G/BACKUP/BMP/pgBackUpdir/"
    last_backup_file_time = ''
    """
    (status, output) = commands.getstatusoutput("ls -lhtr /home/BOH/YUM/BOH2G/BACKUP/BMP/pgBackUpdir/ | grep ^[^Dd] | awk '{print $9}' | sort -r | head -1")
    fname = output.strip()
    fnames = fname.split('.')
    fname_splits = fnames[0].split('_')
    if len(fname_splits) is 4 and fname_splits[len(fname_splits)-1][0:8] > last_backup_file_time:
        last_backup_file_time = fname_splits[len(fname_splits)-1][0:8]
    """
    if os.path.exists(PATH):
        backup_list = os.listdir(PATH)
        for backup_file in backup_list:
            fname = backup_file
            fnames = fname.split('.')
            fname_splits = fnames[0].split('_')
            if len(fname_splits) is 4 and fname_splits[len(fname_splits)-1][0:8] > last_backup_file_time:
                last_backup_file_time = fname_splits[len(fname_splits)-1][0:8]
    
    today = datetime.date.today()
    str_today = today.strftime("%Y%m%d")
    if str_today <= last_backup_file_time:
        return "1"
    else:
        return "0"

def main():
    """
    返回值 0 备份状态异常
           1 当前备份文件不存在
           2 正常
    1,检查备份任务的状态；
    2,检查备份文件是否有检查当天的；
    """
    result = os.system("ping -c 1 101.1.1.200 >/dev/null")  
    if(result == 256):
        print '3001'
    else:
        sche_status = sche_dbbackup_check()
	if sche_status is not "-1" and not sche_status:
            print '0'
	else:
            file_exists = file_dbbcakup_check()
	    if file_exists is "1":
                print '2'
            else:
                print '1'
    
			

if __name__ == "__main__":
    main()
