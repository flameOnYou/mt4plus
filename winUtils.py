# -*- coding: UTF-8 -*-
import win32gui
import win32api


def get_child_windows(parent):        
    if not parent:
        return []

    hwndChildList = []     
    chirldhwn = win32gui.EnumChildWindows(parent, lambda hwnd, param: param.append(hwnd),  hwndChildList)      
    clsname = win32gui.GetClassName(chirldhwn) 
    # print "clsname",clsname
    return hwndChildList 


def demo_child_windows(parent):  
    ''''' 
    演示如何列出所有的子窗口 
    :return: 
    '''  
    if not parent:  
        return  
   
    hWndChildList = []  
    win32gui.EnumChildWindows(parent, lambda hWnd, param: param.append(hWnd),  hWndChildList)  
    show_windows(hWndChildList)  
    return hWndChildList  


def show_window_attr(hWnd):  
    ''''' 
    显示窗口的属性 
    :return: 
    '''  
    if not hWnd:  
        return  
   
    #中文系统默认title是gb2312的编码  
    title = win32gui.GetWindowText(hWnd)  
    title = gbk2utf8(title)  
    clsname = win32gui.GetClassName(hWnd)  
    
    print '窗口句柄:%s ' % (hWnd)  
    print '窗口标题:%s' % (title)  
    print '窗口类名:%s' % (clsname)  
    print ''  
   
def show_windows(hWndList):  
    for h in hWndList:  
        show_window_attr(h)  


def gbk2utf8(s):  
    return s.decode('gbk').encode('utf-8') 


"""

"""

def updateCharts():
    print "update dll ================"
    classname = "MetaQuotes::MetaTrader::4.00"
    titlename = ""
    #获取句柄
    # 自顶层窗口（也就是桌面）开始搜索条件匹配的窗体，并返回这个窗体的句柄。不搜索子窗口、不区分大小写。找不到就返回0
    mt4 = win32gui.FindWindow(classname, None)
    print "%x" % mt4

    # 获取MT4的所有子窗口
    MT4hWndChildList = []  
    win32gui.EnumChildWindows(mt4, lambda hWnd, param: param.append(hWnd),  MT4hWndChildList)

    MDIClient = None
    for GuiCharts in MT4hWndChildList:
        if not GuiCharts:  
            continue  
       
        #中文系统默认title是gb2312的编码  
        title = win32gui.GetWindowText(GuiCharts)  
        title = gbk2utf8(title)  
        clsname = win32gui.GetClassName(GuiCharts)  
        if clsname == "MDIClient":
            MDIClient = GuiCharts
            print '窗口句柄:%s ' % (GuiCharts)  
            print '窗口标题:%s' % (GuiCharts)  
            print '窗口类名:%s' % (GuiCharts)  
            print ''

    # 查找图表所有子窗口
    charts_list = []
    win32gui.EnumChildWindows(MDIClient, lambda hWnd, param: param.append(hWnd),  charts_list)
    for charts_hwnd in charts_list:
        if not charts_hwnd:  
            continue  
       
        #中文系统默认title是gb2312的编码  
        title = gbk2utf8(win32gui.GetWindowText(charts_hwnd))
        clsname = win32gui.GetClassName(charts_hwnd)
        WM_COMMAND = 0x0111
        win32api.PostMessage(charts_hwnd,WM_COMMAND,33324,0)
        if "Afx:" in clsname:
            print '窗口标题:%s' % (title)
if __name__ == '__main__':
    updateCharts()
