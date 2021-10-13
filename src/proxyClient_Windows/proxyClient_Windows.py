import tkinter as tk
import subprocess
import sys
import ctypes
import winreg as wg

#windows方法
#是否管理员
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def changeSwitch(value):
    # 打开代理
    if(value==1):
        try:
            subprocess.run("reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\" /v ProxyEnable /t REG_DWORD /d 1 /f", shell=True),
            #print("代理已开启")
            proxyServer = address.get() + ":" + port.get()
            subprocess.run("reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\" /v ProxyServer /d \""+ proxyServer +"\" /f", shell=True)
            proxyOverride = override.get("1.0","end")[0:-1]
            subprocess.run("reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\" /v ProxyOverride /d \""+ proxyOverride +"\" /f", shell=True)
        except:
            print("代理未成功开启")
        
    # 关闭代理
    else:
        try:
            subprocess.run("reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\" /v ProxyEnable /t REG_DWORD /d 0 /f", shell=True)
            #print("代理已关闭")
        except:
            print("代理未成功关闭")

def saveInfo():
    proxyAddress = address.get()
    proxyPort = port.get()
    proxyOverride = override.get("1.0","end")[0:-1]
    proxyServer = proxyAddress + ":" + proxyPort

    #保存在reg.reg文件
    fo = open("reg.reg","w")
    fo.write("REGEDIT4\n")
    fo.write("[HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings]\n")
    fo.write("\"ProxyServer\"=\"" + proxyServer + "\"\n")
    fo.write("\"ProxyOverride\"=\""+ proxyOverride + "\"")
    fo.close()

    bl = blacklist.get("1.0","end")[:-1]
    fo = open("blacklist.txt","w")
    fo.write(bl)
    fo.close()

    #修改注册表
    subprocess.run("reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\" /v ProxyServer /d \""+ proxyServer +"\" /f", shell=True)
    subprocess.run("reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\" /v ProxyOverride /d \""+ proxyOverride +"\" /f", shell=True)
    
    #新建防火墙规则，屏蔽出入站ip地址
    try:
        subprocess.run("netsh advfirewall firewall delete rule name=blacklist ",shell=True)
        subprocess.run("netsh advfirewall firewall add rule name=blacklist dir=out action=block remoteip=\""+bl+"\"",shell=True)
        subprocess.run("netsh advfirewall firewall add rule name=blacklist dir=in action=block remoteip=\""+bl+"\"",shell=True)
    except:
        print("黑名单应用失败")
    
#获取注册表信息，保存备份
def regInfo():
    #打开注册表键
    key = wg.OpenKey(wg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
    #获取代理服务器地址和端口
    proxyEnable,_ = wg.QueryValueEx(key,'ProxyEnable')
    proxyServer,_ = wg.QueryValueEx(key,'ProxyServer')
    proxyOverride,_ = wg.QueryValueEx(key,'ProxyOverride')
    wg.CloseKey(key)
    
    fo = open("backup.reg","w")
    fo.write("REGEDIT4\n")
    fo.write("[HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings]\n")
    if proxyEnable:
        fo.write("\"ProxyEnable\"=dword:00000001\n")
    else:
        fo.write("\"ProxyEnable\"=dword:00000000\n")
    fo.write("\"ProxyServer\"=\"" + proxyServer + "\"\n")
    fo.write("\"ProxyOverride\"=\""+ proxyOverride +";")
    fo.close()

    #初始窗口数据设置
    address.insert(0,proxyServer[:-5])
    port.insert(0,proxyServer[-4:].split(':',1)[-1])
    override.insert('1.0',proxyOverride)
    try:
            fo = open("blacklist.txt","r")
            bl = fo.read()
            blacklist.insert('1.0',bl)
            subprocess.run("netsh advfirewall firewall add rule name=blacklist dir=out action=block remoteip=\""+bl+"\"",shell=True)
            subprocess.run("netsh advfirewall firewall add rule name=blacklist dir=in action=block remoteip=\""+bl+"\"",shell=True)
    except:
            blacklist.insert('1.0',"")
            
# 运行主窗口
def open_window():
    if is_admin():
        window.mainloop()
    else:
        if sys.version_info[0] ==3:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    
# 初始化窗口
window = tk.Tk()
window.title('ProxySeverClient')
window.geometry('290x400')

#设置开关代理的按钮
tk.Label(window, text='使用代理服务器', font=('Arial', 10)).place(x=5, y=10)
on = tk.Radiobutton(window,text='开', font=('Arial', 10),variable=1, value=1, command=lambda: changeSwitch(1))
on.place(x=5,y=30)
off = tk.Radiobutton(window,text='关', font=('Arial', 10),variable=1, value=2, command=lambda: changeSwitch(0))
off.place(x=45,y=30)

# 设置代理服务器地址以及端口
tk.Label(window, text='地址', font=('Arial', 10)).place(x=10, y=60)
tk.Label(window, text='端口', font=('Arial', 10)).place(x=200, y=60)
address = tk.Entry(window, show='', font=('Arial', 10),width=24)
address.place(x=10,y=80)
port = tk.Entry(window, show='', font=('Arial', 10), width=8)
port.place(x=200,y=80)

#
tk.Label(window, text='请勿对下列条目开头的地址使用代理服务器。', font=('Arial', 10)).place(x=10, y=120)
override = tk.Text(window, font=('Arial', 10), width=35,height=4)
override.place(x=10,y=150)

#黑白名单设置
tk.Label(window, text='阻止以下IP地址的访问，各ip以/分隔。', font=('Arial', 10)).place(x=10, y=240)
blacklist = tk.Text(window,  font=('Arial', 10),width=35,height=4)
blacklist.place(x=10,y=270)
save = tk.Button(window, text='保存', font=('Arial', 10), command=lambda: saveInfo())
save.place(x=120,y=350)


if __name__=='__main__':
    regInfo()
    #window.mainloop()
    open_window()
