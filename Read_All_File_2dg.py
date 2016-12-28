# -*- coding:utf-8 -*-  
import io 
import os
import sys
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030') #这一句是为了能在windows命令行下以UTF-8格式输出字符串
#reload(sys)
#sys.setdefaultencoding("utf-8")

Data_Dir = "Data_In"   #这个目录下面存了已经转成txt的对外投资信息
Data_Er = 'Data_Er'    #这个目录下面存了已经抽取出来的投资信息，以及证券简称和证券代码

Data_Er_Prefix = "Data_Er_"    # 投资信息文本文件名前缀 

# Unicode 格式转换  python2版本使用
def ChangeUnicode(Contents):

	if type(Contents) != unicode:
		Contents = unicode(Contents, "UTF-8")
		pass
	#Contents = re.sub("\s","",Contents)
	return Contents
	pass    

def Read_Single_File(f_name):
	StringAndIndex_List = []
	eachline_List = []
	# Load and read file.
	try:
		File = open(f_name, 'r') #这一步是先把硬盘上的文本文件映射成为一个文件流
		eachline_List = File.readlines()  #读取文件流及文本文件里面的内容
	except UnicodeError:
		print('*********************转码异常********************')
		print('转码异常的文件名:',f_name)
	 
	Preprocess_List = Preprocess(eachline_List) # 预处理 清除空格以及页脚信息
	ParagraphIndex_List = Paragraph(Preprocess_List) # 抽取段落标记信息
	
	StringAndIndex_List.append(Preprocess_List)
	StringAndIndex_List.append(ParagraphIndex_List)
	return StringAndIndex_List
	
def Preprocess(eachline_List):
	eachline_List2 = [] #去除了空格的List
	#eachline_List3 = [] #去除了页眉页脚的List
	
	for index,eachline in enumerate(eachline_List):
		if eachline.strip() != '' and eachline.strip() != ' ' :  #清除空格 生成eachline_List2
			eachline_List2.append(eachline)
	#FileString = ChangeUnicode(FileString)  #先将字符转换为统一码 #pythont2版本使用
	'''
	for index,eachline in enumerate(eachline_List2):    #清除页眉页脚信息
		if not ( re.search('公司 2015年半年度报告全文 ', eachline) ):   #这里去除页码还有点问题
			eachline_List3.append(eachline)
	'''
	return eachline_List2
	
	pass

def Paragraph(Preprocess_List):
	'''
		函数功能:为了提取段落标记
	'''
	ParagraphIndex_List = [] #只存储段落标记索引，判断每行里面是否有。 为准
	for index,eachline in enumerate(Preprocess_List):
		if re.match(r'。$', eachline):
			ParagraphIndex_List.append(index)
	return ParagraphIndex_List

def LineBreaks(Preprocess_List):
	'''
		函数功能：为了提取分行标记
	'''
	pass

def Information_extraction(File_Dict):

	'''
		函数:先把公司信息、盈利能力的表格信息和经营情况这三部分抽取出来
	'''
	for filename, StringAndIndex_List in File_Dict.items():
		try:
			print('**********************文件名**********************')
			print(filename)
			eachline_List = StringAndIndex_List[0]
			ParagraphIndex_List = StringAndIndex_List[1] 
			
			#规则定义
			
			#抽取标题信息
			Title_I = []
			Title_behavior_tag = ['增持', '减持', '转让']
			#义务人名称列表
			title_ywr = '信息披露义务人  指 |信息披露义务人 指 |信息披露义务人：'
			title_qy = '本次权益变动 指 |本次权益变动  指 '
			namelist = []
			#抽取公告日期
			AnnDate = []
			#公司信息
			infor_T = []
			#权益变动基本情况, 这部分抽取一、本次权益变动基本情况到二、所涉及事后事项之间的内容
			infor_J = []
			#所涉及事后事项 这部分内容抽取二、所涉及事后事项后面的一行
			#infor_Y = []
			
			#公司信息索引
			First_Index_T = 0
			Second_Index_T = 0
			
			#协议转让目的
			First_Index_Y = 0
			Second_Index_Y = 0
			
			#权益变动方式
			First_Index_qy = 0
			Second_Index_qy = 0
			
			#证券简称和证券代码
			abbreviation = ' '
			code = ' '
			
			#检测所需信息的索引位置
			for index,eachline in enumerate(eachline_List):
				#print('#################Print每行读取的内容#################')
				#print(eachline) 
				'''
				#抽取标题模板 主要是抽取出减持股东的详情
				if re.search('的公告',eachline.strip()) or re.search('的提示性公告',eachline.strip()):
				'''	
				
				#抽取公司信息部分规则
				if re.search('证券代码',eachline.strip()) or re.search('证券简称',eachline.strip()):
					First_Index_T = index
				m_start = re.compile(r'第三节.*?目的')
				#抽取权益变动情况 
				if re.search(m_start, eachline.strip()):
					First_Index_Y = index
				m_end= re.compile(r'第四节.*?权益变动方式')
				if re.search(m_end, eachline.strip()):
					Second_Index_Y = index
				#简化版
				qy_reg = '第四节.*?权益变动方式.*?一、|第四节.*?权益变动方式$'
				qy_m1 = re.search(qy_reg, eachline.strip())
				qy_end= re.compile(r'三、')
				if qy_m1:
					First_Index_qy = index
				if First_Index_qy > 0:
					if re.search(qy_end, eachline.strip()):
							Second_Index_qy = index
				'''
				qy_start = re.compile(r'第四节.*?权益变动方式.*?一、')
				qy_start2 = re.compile(r'第四节.*?权益变动方式$')
				qy_end= re.compile(r'三、')
				#抽取权益变动情况 
				if re.search(qy_start, eachline.strip()):
					First_Index_qy = index
				if First_Index_qy > 0:
					if re.search(qy_end, eachline.strip()):
							Second_Index_qy = index
				if re.search(qy_start2, eachline.strip()):
					First_Index_qy = index
					if re.search(qy_end, eachline.strip()):
							Second_Index_qy = index
				#print("******")
				'''
				#Title 抽取 可优化
				if len(namelist) == 0:
					reg1 = re.compile('('+ title_ywr +')([^ ]+)',re.S)
					s_name = reg1.search(eachline.strip())
					if s_name:
						namestring = s_name.group(2)
						if '自然人' in namestring:
							namestring = namestring.replace('自然人', '')
						#print(namestring)
						if '、' in namestring:
							namelist = namestring.split('、')
						else:
							namelist.append(namestring)
						#print(namelist)
					elif re.search(r'信息披露义务人', eachline.strip()):
						if eachline_List[index+1].strip() == "指":	#还差一种情况
							namestring = eachline_List[index+2].strip()
							if '自然人' in namestring:
								namestring = namestring.replace('自然人', '')
							if '、' in namestring:
								namelist = namestring.split('、')
							else:
								namelist.append(namestring)
							#print("!!!!!!!!!!!!!!!!!!!!!!!!!")
							#print(namelist)
						elif re.search(r'指.*', eachline_List[index+1].strip()):
							namestring = eachline_List[index+1].strip()
							if '自然人' in namestring:
								namestring.replace('自然人', '')
							if '、' in namestring:
								namelist = namestring.split('、')
							else:
								namelist.append(namestring)
				if re.search(r'('+ title_qy +')[^ ]+', eachline.strip()):
					name = set([n for n in namelist if n in eachline.strip()])
					if not len(name) and "信息披露义务人" in eachline.strip():
						name = namelist[0]
					Title_I.append(''.join(name))
					for behavior in Title_behavior_tag:
						if behavior in eachline.strip():
							Title_I.append(behavior)
							break
				elif re.search(r'本次权益变动', eachline.strip()):
					if eachline_List[index+1].strip() == "指":
						contentstring = eachline_List[index+2].strip()
						name = [n for n in namelist if n in contentstring]
						Title_I.append(''.join(name))
						for behavior in Title_behavior_tag:
							if behavior in contentstring:
								Title_I.append(behavior)
								break
					elif re.search(r'指.*', eachline_List[index+1].strip()):
						name = set([n for n in namelist if n in eachline_List[index+1].strip()])
						if not len(name) and "信息披露义务人" in eachline_List[index+1].strip():
							name = namelist[0]
						Title_I.append(''.join(name))
						for behavior in Title_behavior_tag:
							if behavior in eachline_List[index+1].strip():
								Title_I.append(behavior)
								break
			#Title_I = ''.join(Title_I)
			#时间抽取
			time_m = re.compile(r'(.*?)(\d{2}月.*?\d{2}日)(.*?)')
			for eachline in eachline_List[-5:]:
				#print(eachline)
				if re.search(time_m, eachline):
					AnnDate = re.search(time_m, eachline).group(2)
			
			
			infor_T = eachline_List[First_Index_T]
			infor_qy = eachline_List[First_Index_qy + 1 : Second_Index_qy+1]	#包含三那行 第二段内容
			infor_Y = eachline_List[First_Index_Y + 1 : Second_Index_Y]	#概括的第一段内容
			
			#概括内容只取前两句
			infor_Y = ''.join(infor_Y)
			if len(infor_Y.split('。')) > 1:
				infor_Y = infor_Y.split('。')[:2]
			else:
				infor_Y = infor_Y.split('。')[0]
			
			#infor_Y去掉“本次权益变动是|本次权益变动|本次权益变动是由|本次权益变动为.*(,)$”
			infor_reg = '本次权益变动为.*?，|本次权益变动是由|本次权益变动是|本次权益变动'
			infor_Y = re.match(r'(' +infor_reg+ ')(.*)', ''.join(infor_Y)).group(2)
			
			#获取股份数量
			Title_shares_m = re.search(r'(.*?)(\d+[,.\d]+股)(.*?)$', infor_Y)
			if Title_shares_m:
				Title_shares = Title_shares_m.group(2)
			##股量转中文万单位
			Title_shares_chinese = float(re.sub(r',|股', '', Title_shares))
			if Title_shares_chinese > 10000:
				Title_shares_chinese = int(Title_shares_chinese / 10000)
				Title_shares_chinese = str(Title_shares_chinese) + '万'
			else:
				Title_shares_chinese = str(int(Title_shares_chinese))
			Title_I.append(str(Title_shares_chinese))
			
			#第二次抽取，获取权益转让所需内容
			qy_change_m1 = re.compile(r'(^本次权益变动.*?后.*?)')
			qy_change_m2 = re.compile(r'(^本次权益变动.*?)')
			qy_change_m3 = re.compile(r'(^本次.*?)')
			#以。来分句
			infor_qy = ''.join([i_qy.replace('\n', '') for i_qy in infor_qy]).split('。')
			#print(infor_qy)
			#匹配qy_change_m1直接break，其他两个必须不断匹配
			for index, eachline in enumerate(infor_qy):
				if re.search(qy_change_m1, eachline.strip()):
					qy_start_info_index = index
					break
				elif re.match(qy_change_m2, eachline.strip()):
					qy_start_info_index = index
				elif re.match(qy_change_m3, eachline.strip()):
					qy_start_info_index = index
				else:
					#昶昱黄金匹配问题
					print("")

			infor_qy = infor_qy[qy_start_info_index]
			
			#第二次抽取，将公司信息中的证券代码和证券简称抽取出来
			daima = '股份代码:|股份代码：|证券代码:|证券代码：'
			jiancheng = '股份简称:|股份简称：|证券简称:|证券简称：'
			m1 = re.search(r'^(' +daima+ ')(.*?)(' +jiancheng+ ')(.*?)主办券商', ''.join(eachline_List[0]).strip())

			#去除空格
			abbreviation = m1.group(4).strip()
			code = m1.group(2).strip()

			#list 转 str
			Title_I = ''.join(Title_I)
			'''
			print('*****************标题*****************')
			
			print(Title_I)
			
			print('*****************抽取权益变动*********************')
			print(infor_Y)

			print('*****************抽取权益变动方式*********************')
			print(infor_qy)

			print('*****************公司信息:证券信息*********************')

			print(abbreviation)
			print(code)
			
			print('*****************公告日期*********************')
			print(AnnDate)
			#规则定义
			
			print('*****************公司信息:证券信息*********************')

			print(abbreviation)
			print(code)
			'''
			#拟添加抽取失败文件抛出文件名代码
			pass

		except IndexError:
			print('*********************出现异常********************')
			print('出现异常的文件名:',filename)
		
		#将抽取出来的信息写入文本文件
		Write_To_File(filename, abbreviation, code, Title_I, infor_Y, infor_qy, AnnDate.strip())
		
def Write_To_File(name, abbreviation, code, Title_I, infor_Y, infor_qy, AnnDate):
	'''
		函数功能：将抽取出来的信息写入文本文件
		参数说明：infor_J 涉及事后事项
				  infor_Y 权益变动情况
	'''
	#StrOfInfor_J = ('').join(infor_J)
	#StrOfInfor_Y = ('').join(infor_Y)
	
	#将信息写入文本文件
	Data_Er_file = open(os.path.join(Data_Er, Data_Er_Prefix + str(name)) , 'w')
		
	#将标题信息写入文本文件
	Data_Er_file.write(abbreviation+'股东'+Title_I)
	
	#写入换成符，将两段内容分割开
	Data_Er_file.write('\n')
	Data_Er_file.write('\n')
	
	#将证券代码及证券简称写入文件开头
	abbr = abbreviation+'（'+code+'） '+AnnDate+'公告，'
	Data_Er_file.write(abbr)
	print(abbreviation+'('+code+') '+AnnDate+'公告，')
	#将权益变动情况写入文本文件
	StrOfInfor_Y = infor_Y.strip()    #开头处添加两个空格
	StrOfInfor_Y = StrOfInfor_Y.replace('\n','')
	Data_Er_file.write(StrOfInfor_Y)
	
	#写入换成符，将两段内容分割开
	Data_Er_file.write('\n')
	Data_Er_file.write('\n')
	
	#将涉及事后事项写入文本文件
	StrOfInfor_J = infor_qy.strip()    #开头处添加两个空格
	Data_Er_file.write(StrOfInfor_J)
	
	Data_Er_file.close

def Read_All_File(Data_Dir):
	'''
		函数：读取Data_Dir目录下的所有文件，并返回File_Dict
		Input:
		Data_Dir 存放半年报的目录
		Output: 
		File_Dict 该字典key为文件名，value为文件包含的字符串信息
	'''
	File_Dict = {}
	File_Path_Prefix = os.path.join(os.getcwd(), Data_Dir) #os.getcwd() 获取当前工作目录
	for f_name in os.listdir(Data_Dir): #os.listdir获得指定目录中的内容
		if f_name.endswith(".txt"):  
			f_full_name = os.path.join(File_Path_Prefix, f_name)
			#print(f_full_name)
			File_Dict[f_name] = Read_Single_File(f_full_name)
	return File_Dict
	
def main():
	File_Dict = Read_All_File(Data_Dir)
	#print(Read_All_File(Data_Dir))
	Information_extraction(File_Dict)
	
	pass

if __name__ == '__main__':
	main()