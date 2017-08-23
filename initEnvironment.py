# -*- coding: UTF-8 -*-
import json
import struct
from itertools import islice  
import os        

symbols_raw_path = "../history/default/symbols.raw"
symgroups_raw_path="../history/default/symgroups.raw"
marketInfo_json_path ="marketInfo.json"
symbols_sel_path = "../history/default/symbols.sel"
"""
补0		
str : 字符串
num : 总的字符串个数
"""
def supplementZero(str,num):
    for i in range(1,num):
        str += "\x00"
    return str

"""
写入symbols文件
"""

def CreateSymbols(sym_name,sym_group,sym_Color):
    symLstCnt = len(sym_name)+1
    
#     with open("MarketWatch.csv") as csvFile:
#         for content  in islice(csvFile, 1, None):
#             if "," not in content:
#                 continue
#             name = content.split(",")[0]
#             groups = content.split(",")[1]
#             color = content.split(",")[2]+content.split(",")[3]+content.split(",")[4]
#             sym_name.append(name)
#             sym_group.append(groups)
#             sym_Color.append(color)
#             symLstCnt += 1
    
    with open(symbols_raw_path,"w") as rawFile:
        for i in range(1,symLstCnt):
#             为了防止过长
            snu = sym_name[i-1].strip()
            if len(snu) > 11:
                snu = snu[0:11]
            rawFile.write(struct.pack("100s", snu))
            
            sgu = sym_group[i-1].strip()
            sgu_content = "\x00"
            if sgu == "0":
                sgu_content = "\x00"
            if sgu == "1":
                sgu_content = "\x01"
            if sgu == "2":
                sgu_content = "\x02"
            if sgu == "3":
                sgu_content = "\x03"
            if sgu == "4":
                sgu_content = "\x04"
            if sgu == "5":
                sgu_content = "\x05"
            rawFile.write(supplementZero(sgu_content,4))
            
            color = sym_Color[i-1]
            red = int(color[0:3])
            green = int(color[3:6])
            blue = int(color[6:9])
            rawFile.write(supplementZero("\x02",4))
            rawFile.write(supplementZero("\x02",4))
#             rawFile.write(struct.pack("3c",chr(red),chr(green),chr(blue)))
            rawFile.write(struct.pack("3B",red,green,blue))
            rawFile.write("\x00")
            rawFile.write("\x01")
            rawFile.write("\x00"*3)
            rawFile.write(supplementZero("\x51",1816))
        rawFile.close()
        
"""
写入group
"""

def create_groups(grp_name,grp_Desc):
#     grp_name = []
#     grp_Desc = []

#     with open("groups.csv") as csvFile:
#         for content  in csvFile:
#             if "," not in content:
#                 continue
#             row1 = content.split(",")[0]
#             row2 = content.split(",")[1]
#             
#             grp_name.append(row1)
#             grp_Desc.append(row2)
            
    with open(symgroups_raw_path,"w") as  groupFile:
        symgroups = 2560
        for i in range(1,len(grp_name)+1):
            coreid = grp_name[i-1].strip()
            if isinstance(coreid ,unicode):
                coreid = coreid.encode("utf-8")
            groupFile.write(struct.pack("16s",coreid))
            
            remark = grp_Desc[i-1].strip()
            if isinstance(remark ,unicode):
                remark = remark.encode("utf-8")
            groupFile.write(struct.pack("64s",remark ))
            
            symgroups = symgroups - 80
#             补0
        groupFile.write('\x00'*symgroups)
        
    
def initFunc():
    # 删除symbols.sel文件
    if os.path.exists(symbols_sel_path):

       os.remove(symbols_sel_path)
    with open(marketInfo_json_path) as json_file:
        
        grp_name = []
        grp_Desc = []
        
        sym_name = []
        sym_group = []
        sym_Color = []
        
        json_data = json.load(json_file)
        for i,data in enumerate(json_data):
             grp_name.append(data["market"])
             grp_Desc.append(data["remarks"])
             symboljson = data["symbols"]
             for symbol in symboljson:
                 coreId = str(symbol["coreId"])
                 groupId = str(i)
                 color = str(symbol["red"])+str(symbol["green"])+str(symbol["blue"])
                
                 sym_name.append(coreId)
                 sym_group.append(groupId)
                 sym_Color.append(color)
                 
        
        create_groups(grp_name,grp_Desc)
        CreateSymbols(sym_name,sym_group,sym_Color)
if __name__ == '__main__':
    initFunc()