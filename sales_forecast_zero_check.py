#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
ZBX 监控脚本
    说明：预估为0检查 需要判断预估和拆分是否正常
    版本说明
    V0.5    20161210    Xiong 预估为 0 的产品检查；
            对如下的计划进行的检查，MPC计划、日排程计划、鸡类解冻计划、半成品制备计划、常规解冻计划、快速解冻计划
"""

import commands
import sys

#传入参数 预估百分比
F_Percent = float(sys.argv[1])
#传入参数 拆分百分比
S_Percent = float(sys.argv[2])

def execute_sql(v_sql):
    cmd = ("export PGPASSWORD='Yum!P0werFul' ;"
           "psql -U postgres -h localhost -d BOH2G_STORE_WORK -t -c \"" + v_sql + "\" ")
    (status, output) = commands.getstatusoutput(cmd)
    list_ret = [x.strip() for x in output.strip().split("|")]
    if len(list_ret) > 1:
        return list_ret
    else:
        return output.strip()

def forecast_batch_status_check():
    """
        forecast_execute_status_code  预估状态(1;预估开始，2：预估成功，3：预估失败)
    """
    selectsql = ("select forecast_execute_status_code from epqc_t_fcst_forecast_batch_info"
                 " where execute_forecast_date = CURRENT_DATE;")
    v_result = execute_sql(selectsql)
    return v_result

def forecast_initial_zero_check():
    """
        查询当日预估的总数，预估初始值为0的数量；
        initial_forecast_sr 预估千次初始值
    """
    selectsql = ("select count(1) num,count(case when initial_forecast_sr = 0 then 1 end) initial_zero_num "
                 "  from epqc_t_fcst_product_forecast_sr s where s.forecast_date = CURRENT_DATE ;")
    v_result = execute_sql(selectsql)
    return v_result

def split_batch_status_check():
    """
        查询当日拆分状态
        basic_material_split_status  1：未拆分，2：已拆分
    """
    selectsql = ("select basic_material_split_status from epqc_t_fcst_forecast_batch_info "
                 " WHERE execute_forecast_date = CURRENT_DATE;")
    #print selectsql
    v_result = execute_sql(selectsql)
    return v_result

def mpc_plan_check():
    """
    MPC计划
    """
    selectsql = ("select count(1),count( case when forecast_req_stock_amount = 0 then 1 end) "
                 "  from epqc_t_mpc_fried_plan where del_flag = 'N' "
                 "   and plan_code like '%' || to_char(CURRENT_DATE,'YYYYMMDD')|| '%';")
    v_result = execute_sql(selectsql)
    return v_result

def mpc_daily_cook_plan_check():
    """
    日排程计划
    """
    selectsql = ("select count(1),count( case when forecast_req_stock_amount = 0 then 1 end) "
                 "  from epqc_t_mpc_daily_cook_plan where del_flag = 'N' "
                 "   and plan_code like '%' || to_char(CURRENT_DATE,'YYYYMMDD')|| '%';")
    v_result = execute_sql(selectsql)
    return v_result

def mpc_chicken_thaw_plan_check():
    """
    鸡类解冻计划
    """
    selectsql = ("select count(1),count( case when req_stock_amount = 0 then 1 end) "
                 "  from epqc_t_mpc_chicken_thaw_plan_detail where del_flag = 'N' "
                 "   and plan_code like '%' || to_char(CURRENT_DATE,'YYYYMMDD')|| '%';")
    v_result = execute_sql(selectsql)
    return v_result

def mpc_preparat_plan_work_check():
    """
    半成品制备计划
    """
    selectsql = ("select count(1),count( case when req_stock_amount = 0 then 1 end) "
                 "  from epqc_t_mpc_preparat_plan_work_area_detail where del_flag = 'N' "
                 "   and plan_code like '%' || to_char(CURRENT_DATE,'YYYYMMDD')|| '%';")
    v_result = execute_sql(selectsql)
    return v_result

def mpc_nomal_thaw_plan_check():
    """
    常规解冻计划
    """
    selectsql = ("select count(1),count( case when req_stock_amount = 0 then 1 end) "
                 "  from epqc_t_mpc_nomal_thaw_plan_detail where del_flag = 'N' "
                 "   and plan_code like '%' || to_char(CURRENT_DATE,'YYYYMMDD')|| '%';")
    v_result = execute_sql(selectsql)
    return v_result

def mpc_fast_thaw_plan_check():
    """
    快速解冻计划
    """
    selectsql = ("select count(1),count( case when req_stock_amount = 0 then 1 end) "
                 "  from epqc_t_mpc_fast_thaw_plan_detail where del_flag = 'N' "
                 "   and plan_code like '%' || to_char(CURRENT_DATE,'YYYYMMDD')|| '%';")
    v_result = execute_sql(selectsql)
    return v_result

def main():
    """
    返回值 0 预估异常
           1 拆分异常
           2 正常
    """
    #预估检查
    #预估返回值 0 预估异常 1 预估正常
    f_check_ret = 0
    f_status = forecast_batch_status_check()
    if f_status is not "2":
        #预估异常
        f_check_ret = 0
    else:
        num, f_zero_num = forecast_initial_zero_check()
        if int(num)*F_Percent <= int(f_zero_num):
            #预估异常
            f_check_ret = 0
        else:
            #预估正常
            f_check_ret = 1
    #预估异常直接返回
    if f_check_ret is 0:
        print 0
        return
    #拆分返回值 1 拆分异常 2 拆分正常
    s_check_ret = 1
    s_status = split_batch_status_check()
    if s_status is not "2":
        #拆分异常
        s_check_ret = 1
    else:
        #拆分正常，检查制备计划中的物料需求量
        m_num, m_zeros = mpc_plan_check()
        d_num, d_zeros = mpc_daily_cook_plan_check()
        c_num, c_zeros = mpc_chicken_thaw_plan_check()
        p_num, p_zeros = mpc_preparat_plan_work_check()
        n_num, n_zeros = mpc_nomal_thaw_plan_check()
        f_num, f_zeros = mpc_fast_thaw_plan_check()
        split_num = int(m_num) + int(d_num) + int(c_num) + int(p_num) + int(n_num) + int(f_num)
        split_zero_num = int(m_zeros) + int(d_zeros) + int(c_zeros) + int(p_zeros) + int(n_zeros) + int(f_zeros)
        if int(split_num)*S_Percent <= split_zero_num:
            #拆分异常
            s_check_ret = 1
        else:
            #拆分正常
            s_check_ret = 2
    if s_check_ret is 1:
        print 1
    else:
        print 2

if __name__ == "__main__":
    main()
