#引入库
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
#设置中文字体为宋体
config = {
"font.family": 'serif', 
"font.size": 12, 
"font.serif": ['SimSun'], 
"mathtext.fontset": 'stix', 
'axes.unicode_minus': False }
rcParams.update(config)
init_pro = np.array([1,0,0,0,0,0,0])

#马尔科夫模型
def markov_base(startAge:int, stage:int, interval:int, init_pro, baseline : bool,_pNoToMild = 0.07, _pMildToModerate = 0.19, _pModerateToVTDR = 0.17, _pVTDRToStable = 0.90, _pStableToBlindness = 0.02,_pVTDRToBlindness = 0.09, _muti_diabetes = 1.90, _muti_blindness = 2.34, _c_doctor = 3.213,_c_examination = 1.63, _c_laser = 347.177, _c_blindness_first = 8920, _c_blindness_follow = 3600, _discountRate = 0.03,_uNo = 0.94, _uMild = 0.87, _uModerate = 0.87, _uVTDR = 0.83, _uStable = 0.85, _uBlindness = 0.81):
    p_No = np.zeros(7)
    p_Mild = np.zeros(7)
    p_Moderate = np.zeros(7)
    p_VTDR = np.zeros(7)
    p_Stable = np.zeros(7)
    p_Blindness = np.zeros(7)
    p_Death = np.zeros(7)
    abosrb_rate = 0
    _utility = np.array([_uNo, _uMild, _uModerate, _uVTDR, _uStable, _uBlindness,0])
    effectiveness = np.sum(init_pro * _utility)
    _screen = _c_doctor + _c_examination
    c_screen = np.array([_screen, _screen, _screen, _screen, _screen,0 ,0])
    if not baseline:
        cost_screen = np.sum(init_pro * c_screen)
    else:
        cost_screen = 0
    cost_healthcare = 0
    stage_blindness_first = 0
    stage_blindness_follow = 0
    stage_laser = 0
    for _stage in range(startAge, startAge+stage):
        p_No[6] = get_death_rate(death_rate, _stage,'diabetes', _muti_diabetes, _muti_blindness)
        p_No[1] = _pNoToMild 
        p_No[0] = 1-p_No[1]-p_No[6]
        p_Mild[6] = get_death_rate(death_rate, _stage,'diabetes', _muti_diabetes, _muti_blindness)
        p_Mild[2] = _pMildToModerate
        p_Mild[1] = 1-p_Mild[2]-p_Mild[6]
        
        p_Moderate[6] = get_death_rate(death_rate, _stage,'diabetes', _muti_diabetes, _muti_blindness)
        p_Moderate[3] = _pModerateToVTDR
        p_Moderate[2] = 1-p_Moderate[3]-p_Moderate[6]
        if not baseline and (_stage % interval == startAge % interval):
            stage_laser = init_pro[2] * p_Moderate[3] * _c_laser /((1+_discountRate)**(_stage - startAge + 1))
        
        p_VTDR[6] = get_death_rate(death_rate, _stage,'diabetes', _muti_diabetes, _muti_blindness)
        if not baseline and (_stage % interval == startAge % interval):
            p_VTDR[4] = _pVTDRToStable * (1-p_VTDR[6])
        else:
            p_VTDR[4] = 0
        p_VTDR[5] = _pVTDRToBlindness * (1-p_VTDR[6])
        p_VTDR[3] = 1-p_VTDR[4]-p_VTDR[6]-p_VTDR[5]
        stage_blindness_first = init_pro[3] * p_VTDR[5] * _c_blindness_first /((1+_discountRate)**(_stage - startAge + 1))
               
        p_Stable[6] = get_death_rate(death_rate, _stage,'diabetes', _muti_diabetes, _muti_blindness)
        p_Stable[5] = _pStableToBlindness 
        p_Stable[4] = 1-p_Stable[5]-p_Stable[6]
        stage_blindness_first = init_pro[4] * p_Stable[5] * _c_blindness_first /((1+_discountRate)**(_stage - startAge + 1))
        
        p_Blindness[6] = get_death_rate(death_rate, _stage,'blindness', _muti_diabetes, _muti_blindness)
        p_Blindness[5] = 1-p_Blindness[6]
        stage_blindness_follow = init_pro[5] * _c_blindness_follow / ((1+_discountRate)**(_stage - startAge + 1))
        
        transfer_matrix=np.array([p_No,p_Mild,p_Moderate,p_VTDR,p_Stable,p_Blindness,p_Death])
        init_pro = np.dot(init_pro,transfer_matrix)
        init_pro[6] = init_pro[6] + abosrb_rate
        
        effectiveness = effectiveness + np.sum((init_pro * _utility)/((1+_discountRate)**(_stage - startAge + 1)))
        if not baseline and _stage % interval == startAge % interval:
            cost_screen = cost_screen + np.sum((init_pro * c_screen)/((1+_discountRate)**(_stage - startAge + 1)))
        
        cost_healthcare = cost_healthcare + stage_blindness_first + stage_blindness_follow + stage_laser 
        
        abosrb_rate = init_pro[6]
return cost_screen ,cost_healthcare, effectiveness


def markov(startAge:int, stage:int, interval:int, init_pro, baseline : bool, ):
    pNoToMild = 0.07
    pMildToModerate = 0.19
    pModerateToVTDR = 0.17
    pVTDRToStable = 0.9
    pStableToBlindness = 0.02
    pVTDRToBlindness = 0.09

    muti_diabetes = 1.9
    muti_blindness = 2.34
    c_doctor = 3.213
    c_examination = 1.63
    c_laser = 347.177
    c_blindness_first = 8920
    c_blindness_follow = 3600
    discountRate = 0.03
    
    u_No = 0.94
    u_Mild = 0.87
    u_Moderate = 0.87
    u_VTDR = 0.83
    u_Stable = 0.85
    u_Blindness = 0.81
    
    return markov_base(startAge, stage, interval, init_pro, baseline, pNoToMild, pMildToModerate,pModerateToVTDR,pVTDRToStable,pStableToBlindness,pVTDRToBlindness, muti_diabetes, muti_blindness, c_doctor,c_examination, c_laser, c_blindness_first, c_blindness_follow, discountRate, u_No, u_Mild, u_Moderate, u_VTDR, u_Stable, u_Blindness)

#得到各年龄组的筛查成本，健康护理成本，效果值。
### group 40
Baseline40 = markov(40, 30, 1, init_pro, True)
S40_1 = markov(40, 30, 1, init_pro, False)
S40_2 = markov(40, 30, 2, init_pro, False)
S40_3 = markov(40, 30, 3, init_pro, False)
S40_4 = markov(40, 30, 4, init_pro, False)
S40_5 = markov(40, 30, 5, init_pro, False)
print(Baseline40,S40_1,S40_2,S40_3,S40_4,S40_5)
group40 = pd.DataFrame([Baseline40,S40_1,S40_2,S40_3,S40_4,S40_5],index = ['Baseline40','S40_1','S40_2','S40_3','S40_4','S40_5'],columns = ['screen','healthcare','effectiveness'])

### group 45
Baseline45 = markov(45, 30, 1, init_pro, True)
S45_1 = markov(45, 30, 1, init_pro, False)
S45_2 = markov(45, 30, 2, init_pro, False)
S45_3 = markov(45, 30, 3, init_pro, False)
S45_4 = markov(45, 30, 4, init_pro, False)
S45_5 = markov(45, 30, 5, init_pro, False)
group45 = pd.DataFrame([Baseline45,S45_1,S45_2,S45_3,S45_4,S45_5],index = ['Baseline45','S45_1','S45_2','S45_3','S45_4','S45_5'],columns = ['screen','healthcare','effectiveness'])

### group 50
Baseline50 = markov(50, 30, 1, init_pro, True)
S50_1 = markov(50, 30, 1, init_pro, False)
S50_2 = markov(50, 30, 2, init_pro, False)
S50_3 = markov(50, 30, 3, init_pro, False)
S50_4 = markov(50, 30, 4, init_pro, False)
S50_5 = markov(50, 30, 5, init_pro, False)
group50 = pd.DataFrame([Baseline50,S50_1,S50_2,S50_3,S50_4,S50_5],index = ['Baseline50','S50_1','S50_2','S50_3','S50_4','S50_5'],columns = ['screen','healthcare','effectiveness'])


#计算总成本，成本增量，效果增量，ICER，BCR
def count_values(groupvalues):
    groupvalues.insert(2,'cost',value = groupvalues['screen'] + groupvalues['healthcare'])
    rows = groupvalues.shape[0]
    incr_screen = [0] * rows
    incr_healthcare =[0] * rows
    incr_effectiveness = [0] * rows
    incr_cost = [0] * rows
    for i in range(rows):
        incr_screen[i] = groupvalues['screen'][i] - groupvalues['screen'][0]
        incr_healthcare[i] = groupvalues['healthcare'][i] - groupvalues['healthcare'][0]
        incr_effectiveness[i] = groupvalues['effectiveness'][i] - groupvalues['effectiveness'][0]
        incr_cost[i] = groupvalues['cost'][i] - groupvalues['cost'][0]
    groupvalues['incr_screen'] = incr_screen
    groupvalues['incr_healthcare'] = incr_healthcare
    groupvalues['incr_cost'] = incr_cost
    groupvalues['incr_effectiveness'] = incr_effectiveness
    groupvalues['ICER'] = groupvalues['incr_cost'] / groupvalues['incr_effectiveness']
    groupvalues['CBR'] = groupvalues['incr_healthcare'] / groupvalues['incr_screen'] * (-1)
    return groupvalues

count_values(group40)
count_values(group45)
count_values(group50)


#绘制成本效果散点图
legend = ['不筛查', '每年一次', '每两年一次', '每三年一次', '每四年一次', '每五年一次']
marker = ['o','v','s','p','8','^']
linewidth = 1
hlinewidth = 0.5

fig_local ,(ax_local1,ax_local2,ax_local3) = plt.subplots(1, 3, figsize = (15,5), sharey=True)
fig_local.suptitle("成本效果图",fontsize = 20)
fig_local.supxlabel('效果增量, QALY',fontsize = 15)
fig_local.supylabel('成本增量, $',fontsize = 15)

for i in range(6):
    ax_local1.scatter(group40['incr_effectiveness'][i], group40['incr_cost'][i], 
                      label = legend[i],marker = marker[i],linewidths = linewidth)
for i in range(6):
    ax_local2.scatter(group45['incr_effectiveness'][i], group45['incr_cost'][i], 
                      label = legend[i],marker = marker[i],linewidths = linewidth)
for i in range(6):
    ax_local3.scatter(group50['incr_effectiveness'][i], group50['incr_cost'][i], 
                      label = legend[i],marker = marker[i],linewidths = linewidth)
ax_local1.spines['right'].set_color('none')
ax_local1.spines['top'].set_color('none')
ax_local1.set_xlim(-0.15,0.2)
ax_local1.set_ylim(-3000,2000)
#ax_local1.set_title("40岁组")
ax_local1.text(0,-3700,"(a)40岁组",fontsize = "large")
ax_local1.hlines(0,-0.15,0.2,linestyle = '-.',linewidth=hlinewidth)
ax_local1.vlines(0,-3000,2000,linestyle='-.',linewidth=hlinewidth)

ax_local2.spines['right'].set_color('none')
ax_local2.spines['top'].set_color('none')
ax_local2.set_xlim(-0.15,0.2)
ax_local2.set_ylim(-3000,2000)
ax_local2.text(0,-3700,"(b)45岁组",fontsize = 'large')
ax_local2.hlines(0,-0.15,0.2,linestyle = '-.',linewidth=hlinewidth)
ax_local2.vlines(0,-3000,2000,linestyle='-.',linewidth=hlinewidth)

ax_local3.spines['right'].set_color('none')
ax_local3.spines['top'].set_color('none')
ax_local3.set_xlim(-0.15,0.2)
ax_local3.set_ylim(-3000,2000)
ax_local3.text(0,-3700,"(c)50岁组",fontsize = 'large')
ax_local3.hlines(0,-0.15,0.2,linestyle = '-.',linewidth=hlinewidth)
ax_local3.vlines(0,-3000,2000,linestyle='-.',linewidth=hlinewidth)

ax_local3.legend(fontsize = 9)
plt.tight_layout()
#plt.show()
plt.savefig('ICER.png',format = 'png')


#敏感性分析
def sensitive_analsys(startAge, screen_interval):
    pNoToMild = 0.07
    pNoToMildRange = np.linspace(0.01, 0.1, 4)
    
    pMildToModerate = 0.19
    pMildToModerateRange = np.linspace(0.166, 0.214, 4)
    
    pModerateToVTDR = 0.17
    pModerateToVTDRRange = np.linspace(0.147, 0.193, 4)
    
    pVTDRToStable = 0.9
    pVTDRToStableRange = np.linspace(0.881, 0.919, 4)
    
    pStableToBlindness = 0.02
    pStableToBlindnessRange = np.linspace(0.002, 0.03, 4)
    
    pVTDRToBlindness = 0.09
    pVTDRToBlindnessRange = np.linspace(0.07, 0.11, 4)

    muti_diabetes = 1.9
    muti_diabetesRange = np.linspace(1.04, 2.7, 4)
    
    muti_blindness = 2.34
    muti_blindnessRange = np.linspace(2.22, 2.46, 4)
    
    c_doctor = 3.213
    c_doctorRange = np.linspace(1.606, 4.819, 4)
    
    c_examination = 1.63
    c_examinationRange = np.linspace(0.815, 2.445, 4)
    
    c_laser = 347.177
    c_laserRange = np.linspace(173.589, 520.766, 4)
 
    c_blindness_first = 8920
    c_blindness_firstRange = np.linspace(4460, 13380, 4)
    
    c_blindness_follow = 3600
    c_blindness_followRange = np.linspace(1800, 5400, 4)
    
    discountRate = 0.03
    discountRateRange = np.linspace(0, 0.06, 4)
    
    uNo = 0.94 
    uNoRange = np.linspace(0.83, 1.05, 4)
    
    uMild = 0.87
    uMildRange = np.linspace(0.73, 1.01, 4)
    
    uModerate =  0.87
    uModerateRange = np.linspace(0.73, 1.01)
    
    uVTDR = 0.83
    uVTDRRange = np.linspace(0.74, 0.92, 4)
    
    uStable = 0.85
    uStableRange = np.linspace(0.72, 0.78, 4)
    
    uBlindness = 0.81
    uBlindnessRange = np.linspace(0.73, 0.89, 4)
    
    #pNoToMild
    pNoToMildICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _pNoToMild = pNoToMildRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _pNoToMild = pNoToMildRange[i])
        pNoToMildICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)
	    
    #pMildToModerate
    pMildToModerateICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _pMildToModerate = pMildToModerateRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _pMildToModerate = pMildToModerateRange[i])
        pMildToModerateICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)
    
    #pModerateToVTDR
    pModerateToVTDRICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _pModerateToVTDR = pModerateToVTDRRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _pModerateToVTDR = pModerateToVTDRRange[i])
        pModerateToVTDRICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)
    
    #pVTDRToStable
    pVTDRToStableICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _pVTDRToStable = pVTDRToStableRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _pVTDRToStable = pVTDRToStableRange[i])
        pVTDRToStableICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)    
    
    #pStableToBlindness
    pStableToBlindnessICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _pStableToBlindness = pStableToBlindnessRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _pStableToBlindness = pStableToBlindnessRange[i])
        pStableToBlindnessICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)    
    
    #pVTDRToBlindness
    pVTDRToBlindnessICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _pVTDRToBlindness = pVTDRToBlindnessRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _pVTDRToBlindness = pVTDRToBlindnessRange[i])
        pVTDRToBlindnessICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)
    
    #muti_diabetes
    muti_diabetesICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _muti_diabetes = muti_diabetesRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _muti_diabetes = muti_diabetesRange[i])
        muti_diabetesICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)
    
    #muti_blindness
    muti_blindnessICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _muti_blindness = muti_blindnessRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _muti_blindness = muti_blindnessRange[i])
        muti_blindnessICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)
    
    #c_doctor
    c_doctorICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _c_doctor = c_doctorRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _c_doctor = c_doctorRange[i])
        c_doctorICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)
    
    #c_examination
    c_examinationICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _c_examination = c_examinationRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _c_examination = c_examinationRange[i])
        c_examinationICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)
    
    #c_laser
    c_laserICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _c_laser = c_laserRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _c_laser = c_laserRange[i])
        c_laserICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)

    #c_blindness_first
    c_blindness_firstICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _c_blindness_first = c_blindness_firstRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _c_blindness_first = c_blindness_firstRange[i])
        c_blindness_firstICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)
    
    #c_blindness_follow
    c_blindness_followICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _c_blindness_follow = c_blindness_followRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _c_blindness_follow = c_blindness_followRange[i])
        c_blindness_followICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)
    
    #discountRate
    discountRateICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _discountRate = discountRateRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _discountRate = discountRateRange[i])
        discountRateICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)
    
    #uNo
    uNoICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _uNo = uNoRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _uNo = uNoRange[i])
        uNoICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)
    
    #uMild
    uMildICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _uMild = uMildRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _uMild= uMildRange[i])
        uMildICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)
    
    #uModerate
    uModerateICER = np.zeros(4)
    for i in range(4):
        cost_screen_baseline ,cost_healthcare_baseline, effectiveness_baseline = markov_base(startAge, 30, screen_interval, init_pro, True, _uModerate = uModerateRange[i])
        cost_screen_eva ,cost_healthcare_eva, effectiveness_eva = markov_base(startAge, 30, screen_interval, init_pro, False, _uModerate= uModerateRange[i])
        uModerateICER[i] = ICER(cost_screen_baseline + cost_healthcare_baseline, effectiveness_baseline,
                             cost_screen_eva + cost_healthcare_eva, effectiveness_eva)
    
    return pd.DataFrame([pNoToMildICER, pMildToModerateICER,pModerateToVTDRICER,pVTDRToStableICER,
                     pStableToBlindnessICER,pVTDRToBlindnessICER,muti_diabetesICER,muti_blindnessICER,
                        c_doctorICER,c_examinationICER,c_laserICER,c_blindness_firstICER,c_blindness_followICER,
discountRateICER,uNoICER,uMildICER,uModerateICER],
index = ['pNoToMild', 'pMildToModerate','pModerateToVTDR','pVTDRToStable',
                                 'pStableToBlindness','pVTDRToBlindness','muti_diabetes','muti_blindness',
                                'c_doctor','c_examination','c_laser','c_blindness_first','c_blindness_follow','discountRate','uNo','uMild','uModerate'])


group40_sensitive_range = sensitive_analsys(40, 1)
group40_sensitive_range['min'] = group40_sensitive_range.min(axis = 1)
group40_sensitive_range['max'] = group40_sensitive_range.max(axis = 1) 
group40_sensitive_range['range'] = group40_sensitive_range['max'] - group40_sensitive_range['min']
group40_sensitive_range = group40_sensitive_range.sort_values('range',ascending = False, inplace = False)

group45_sensitive_range = sensitive_analsys(45, 1)
group45_sensitive_range['min'] = group45_sensitive_range.min(axis = 1)
group45_sensitive_range['max'] = group45_sensitive_range.max(axis = 1) 
group45_sensitive_range['range'] = group45_sensitive_range['max'] - group45_sensitive_range['min']
group45_sensitive_range = group45_sensitive_range.sort_values('range',ascending = False, inplace = False)

group50_sensitive_range = sensitive_analsys(50, 1)
group50_sensitive_range['min'] = group50_sensitive_range.min(axis = 1)
group50_sensitive_range['max'] = group50_sensitive_range.max(axis = 1) 
group50_sensitive_range['range'] = group50_sensitive_range['max'] - group50_sensitive_range['min']
group50_sensitive_range = group50_sensitive_range.sort_values('range',ascending = False, inplace = False)

group40_sensitive_range['right'] = group40_sensitive_range['max'] - EV_40
group40_sensitive_range['left'] = EV_40 - group40_sensitive_range['min']

group45_sensitive_range['right'] = group45_sensitive_range['max'] - EV_45
group45_sensitive_range['left'] = EV_45 - group45_sensitive_range['min']

group50_sensitive_range['right'] = group50_sensitive_range['max'] - EV_50
group50_sensitive_range['left'] = EV_50 - group50_sensitive_range['min']



dic = {
'pNoToMild':'无DR进展为轻度DR概率(0.01-0.10)',
'pMildToModerate':'轻度DR进展为中度DR概率(0.166-0.214)',
'pModerateToVTDR':'中度DR进展为视力威胁DR概率(0.147-0.193)',
'pVTDRToStable':'视力威胁DR到稳定DR概率(0.881-0.919)',
'pStableToBlindness':'稳定DR到眼盲概率(0.002-0.03)',
'pVTDRToBlindness':'视力威胁DR到眼盲概率(0.07-0.11)',
'uNo':'无DR的效果值(0.83-1.05)',
'uMild':'轻度DR的效果值(0.73-1.01)',
'uModerate':'中度DR的效果值(0.73-1.01)',
'uVTDR':'视力威胁DR的效果值(0.74-0.92)',
'uStable':'稳定DR的效果值(0.72-0.78)',
'uBlindness':'眼盲的效果值(0.73-0.89)',
'muti_blindness':'眼盲病人死亡倍数(2.22-2.46)',
'muti_diabetes':'糖尿病人死亡倍数(1.04-2.7)',
'discountRate':'贬值系数(0%-6%)',
'c_doctor':'眼科医生挂号花费(1.606-4.819)',
'c_examination':'眼底检查花费(0.815-2.445)',
'c_laser':'激光治疗花费(173.589-520.766)',
'c_blindness_first':'眼盲第一年的花费(4460-13380)',
'c_blindness_follow':'眼盲以后每年的花费(1800-5400)'
}

cm = 1/2.54
y_label_local = group50_sensitive_range.index[::-1]
y_label = [dic[label] for label in y_label_local]
num = len(y_label)
postive = group50_sensitive_range['right'][::-1]
negtive = group50_sensitive_range['left'][::-1] * (-1)
plt.subplots(figsize = (18*cm,16*cm),dpi = 300)
plt.barh(range(num), postive, color = 'blue', alpha = 0.5, label = '+')
plt.barh(range(num), negtive, color = 'blue', alpha = 0.5, label = '-')
ax = plt.gca()
ax.set_xlim(xmin = -30000, xmax = 30000)
#ax.spines['right'].set_color('none')
#ax.spines['top'].set_color('none')
ax.set_title('Tornado Diagram -ICER')
plt.yticks(range(num), y_label,fontsize = 9)
plt.xticks([-20000,0,19508.1160],['-40000','-19508.1160','0'])
plt.vlines(0,0,num,linestyle = '--',color = 'grey')
plt.vlines(19508.1160,0,num,linestyle = '--',color = 'red')
#plt.show()
plt.savefig('Tornado50.png',format = 'png', bbox_inches = 'tight')

y_label_local = group40_sensitive_range.index[::-1]
y_label = [dic[label] for label in y_label_local]
num = len(y_label)
postive = group40_sensitive_range['right'][::-1]
negtive = group40_sensitive_range['left'][::-1] * (-1)
plt.subplots(figsize = (18*cm,16*cm),dpi = 300)
plt.barh(range(num), postive, color = 'blue', alpha = 0.5, label = '+')
plt.barh(range(num), negtive, color = 'blue', alpha = 0.5, label = '-')
ax = plt.gca()
ax.set_xlim(xmin = -30000, xmax = 30000)
#ax.spines['right'].set_color('none')
#ax.spines['top'].set_color('none')
ax.set_title('Tornado Diagram -ICER')
plt.yticks(range(num), y_label,fontsize = 9)
plt.xticks([-(40000-25752.9080),0,25752.9080],['-40000','-25752.9080','0'])
plt.vlines(0,0,num,linestyle = '--',color = 'grey')
plt.vlines(25752.9080,0,num,linestyle = '--',color = 'red')
#plt.show()
plt.savefig('Tornado40.png',format = 'png', bbox_inches = 'tight')

y_label_local = group45_sensitive_range.index[::-1]
y_label = [dic[label] for label in y_label_local]
num = len(y_label)
postive = group45_sensitive_range['right'][::-1]
negtive = group45_sensitive_range['left'][::-1] * (-1)
plt.subplots(figsize = (18*cm,16*cm),dpi = 300)
plt.barh(range(num), postive, color = 'blue', alpha = 0.5, label = '+')
plt.barh(range(num), negtive, color = 'blue', alpha = 0.5, label = '-')
ax = plt.gca()
ax.set_xlim(xmin = -30000, xmax = 30000)
#ax.spines['right'].set_color('none')
#ax.spines['top'].set_color('none')
ax.set_title('Tornado Diagram -ICER')
plt.yticks(range(num), y_label,fontsize = 9)
plt.xticks([-(40000-22972.1069),0,22972.1069],['-40000','-22972.1069','0'])
plt.vlines(0,0,num,linestyle = '--',color = 'grey')
plt.vlines(22972.1069,0,num,linestyle = '--',color = 'red')
print(plt.axis())
#plt.show()
plt.savefig('Tornado45.png',format = 'png', bbox_inches = 'tight')


c_blindness_followRange_further = np.linspace(0, 3600, 5)
group40_CBR = pd.DataFrame([], index = ['S40_1','S40_2','S40_3','S40_4','S40_5'])
group45_CBR = pd.DataFrame([], index = ['S45_1','S45_2','S45_3','S45_4','S45_5'])
group50_CBR = pd.DataFrame([], index = ['S50_1','S50_2','S50_3','S50_4','S50_5'])
i = '0'
for i in range(len(c_blindness_followRange_further)):
    ### group 40
    Baseline40_further = markov_base(40, 30, 1, init_pro, True,_c_blindness_follow = c_blindness_followRange_further[i])
    S40_1_further = markov_base(40, 30, 1, init_pro, False, _c_blindness_follow = c_blindness_followRange_further[i])
    S40_2_further = markov_base(40, 30, 2, init_pro, False, _c_blindness_follow = c_blindness_followRange_further[i])
    S40_3_further = markov_base(40, 30, 3, init_pro, False, _c_blindness_follow = c_blindness_followRange_further[i])
    S40_4_further = markov_base(40, 30, 4, init_pro, False, _c_blindness_follow = c_blindness_followRange_further[i])
    S40_5_further = markov_base(40, 30, 5, init_pro, False, _c_blindness_follow = c_blindness_followRange_further[i])
#    print(Baseline40_further,S40_1_further,S40_2_further,S40_3_further,S40_4_further,S40_5_further)
    group40_further = pd.DataFrame([Baseline40_further,S40_1_further,S40_2_further,S40_3_further,S40_4_further,S40_5_further],index = ['Baseline40','S40_1','S40_2','S40_3','S40_4','S40_5'],columns = ['screen','healthcare','effectiveness'])
    group40_local = count_values(group40_further)
    group40_CBR[i] = group40_local['CBR'][1:]

    ### group 45
    Baseline45_further = markov_base(45, 30, 1, init_pro, True, _c_blindness_follow = c_blindness_followRange_further[i])
    S45_1_further = markov_base(45, 30, 1, init_pro, False, _c_blindness_follow = c_blindness_followRange_further[i])
    S45_2_further = markov_base(45, 30, 2, init_pro, False, _c_blindness_follow = c_blindness_followRange_further[i])
    S45_3_further = markov_base(45, 30, 3, init_pro, False, _c_blindness_follow = c_blindness_followRange_further[i])
    S45_4_further = markov_base(45, 30, 4, init_pro, False, _c_blindness_follow = c_blindness_followRange_further[i])
    S45_5_further = markov_base(45, 30, 5, init_pro, False, _c_blindness_follow = c_blindness_followRange_further[i])
    group45_further = pd.DataFrame([Baseline45_further,S45_1_further,S45_2_further,S45_3_further,S45_4_further,S45_5_further],index = ['Baseline45','S45_1','S45_2','S45_3','S45_4','S45_5'],columns = ['screen','healthcare','effectiveness'])
    group45_local = count_values(group45_further)
    group45_CBR[i] = group45_local['CBR'][1:]

    ### group 50
    Baseline50_further = markov_base(50, 30, 1, init_pro, True, _c_blindness_follow = c_blindness_followRange_further[i])
    S50_1_further = markov_base(50, 30, 1, init_pro, False, _c_blindness_follow = c_blindness_followRange_further[i])
    S50_2_further = markov_base(50, 30, 2, init_pro, False, _c_blindness_follow = c_blindness_followRange_further[i])
    S50_3_further = markov_base(50, 30, 3, init_pro, False, _c_blindness_follow = c_blindness_followRange_further[i])
    S50_4_further = markov_base(50, 30, 4, init_pro, False, _c_blindness_follow = c_blindness_followRange_further[i])
    S50_5_further = markov_base(50, 30, 5, init_pro, False, _c_blindness_follow = c_blindness_followRange_further[i])
#    print(Baseline50_further,S50_1_further,S50_2_further,S50_3_further,S50_4_further,S50_5_further)
    group50_further = pd.DataFrame([Baseline50_further,S50_1_further,S50_2_further,S50_3_further,S50_4_further,S50_5_further],index = ['Baseline50','S50_1','S50_2','S50_3','S50_4','S50_5'],columns = ['screen','healthcare','effectiveness'])
    group50_local = count_values(group50_further)
    group50_CBR[i] = group50_local['CBR'][1:]
    i = i + 1
 

legend = [ '每年一次', '每两年一次', '每三年一次', '每四年一次', '每五年一次']
marker = ['v','s','p','8','^']
colors = ['orange', 'green', 'red', 'purple', 'brown']
linewidth = 1
hlinewidth = 0.5


fig_local ,(ax_local1,ax_local2,ax_local3) = plt.subplots(1, 3, figsize = (15,5), sharey=True)
fig_local.suptitle("收益成本图",fontsize = 20)
fig_local.supxlabel('眼盲后每年的花费, $')
fig_local.supylabel('收益成本率')
#fig_local.text(0.5, 0, '效果（调整质量寿命年）', ha='center',fontsize = 13)
#fig_local.text(0, 0.5, '成本（元）', va='center', rotation='vertical',fontsize = 13)
for i in range(len(legend)):
    ax_local1.plot(c_blindness_followRange_further,group40_CBR.iloc[i], label = legend[i], color = colors[i], linestyle = '-')
    ax_local2.plot(c_blindness_followRange_further,group45_CBR.iloc[i], label = legend[i], color = colors[i], linestyle = '-')
    ax_local3.plot(c_blindness_followRange_further,group50_CBR.iloc[i], label = legend[i], color = colors[i], linestyle = '-')

ax_local1.spines['right'].set_color('none')
ax_local1.spines['top'].set_color('none')
ax_local1.set_xlim(0,3700)
ax_local1.set_ylim(-30, 80)
ax_local1.text(1500,-50,'(a)40岁组',fontsize = 'large')
ax_local1.hlines(0, 0, 3700,linestyle = '-.',linewidth=hlinewidth)

ax_local2.spines['right'].set_color('none')
ax_local2.spines['top'].set_color('none')
ax_local2.set_xlim(0,3700)
ax_local2.set_ylim(-30, 80)
ax_local2.text(1500,-50,'(b)45岁组',fontsize = 'large')
ax_local2.hlines(0,0, 3700 ,linestyle = '-.',linewidth=hlinewidth)

ax_local3.spines['right'].set_color('none')
ax_local3.spines['top'].set_color('none')
ax_local3.set_xlim(0,3700)
ax_local3.set_ylim(-30, 80)
ax_local3.text(1500,-50,'(c)50岁组',fontsize = 'large')
ax_local3.hlines(0, 0, 3700, linestyle = '-.',linewidth=hlinewidth)


ax_local3.legend(fontsize = 9, loc = 'upper right')
plt.tight_layout()
#plt.show()
plt.savefig('CBR.png',format = 'png')

