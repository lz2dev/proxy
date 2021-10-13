import tkinter as tk
import subprocess

def changeSwitch(value):
    # 打开代理
    if value==1:
        print('Globe Mode')
        p1 = subprocess.Popen('networksetup -setproxybypassdomains "'+ns+'" Empty',shell=True)
        p2 = subprocess.Popen('networksetup -setautoproxystate "'+ns+'" off',shell=True)
        turn_on(httpAddress.get(),httpPort.get(),sockAddress.get(),sockPort.get())
    
    # 黑名单模式
    elif value==2:
        print('Blacklist Mode')
        p1 = subprocess.Popen('networksetup -setautoproxystate "'+ns+'" off',shell=True)
        p2 = subprocess.Popen('networksetup -setproxybypassdomains "'+ns+'" '+blacklist.get(),shell=True)
        turn_on(httpAddress.get(),httpPort.get(),sockAddress.get(),sockPort.get())
    
    # 白名单模式
    elif value==3:
        print('Whitelist Mode(PAC)')
        p1 = subprocess.Popen('networksetup -setproxybypassdomains "'+ns+'" Empty',shell=True)
        p2 = subprocess.Popen('networksetup -setautoproxyurl "'+ns+'" '+whitelistURL.get(),shell=True)
        turn_on(httpAddress.get(),httpPort.get(),sockAddress.get(),sockPort.get())
    
    # 关闭代理
    else:
        p1 = subprocess.Popen('networksetup -setproxybypassdomains "'+ns+'" Empty',shell=True)
        p2 = subprocess.Popen('networksetup -setautoproxystate "'+ns+'" off',shell=True)
        turn_off()
        print('Proxy off')

def saveInfo():
    datas = [
        httpAddress.get()+'\n',
        httpPort.get()+'\n',
        sockAddress.get()+'\n',
        sockPort.get()+'\n',
        blacklist.get()+'\n',
        whitelistURL.get()+'\n']

    with open("data.txt","w") as f:
        f.writelines(datas)
    print('Saved')

def turn_on(httpIP,httpPort,sockIP,sockPort):
    # 配置代理端口
    p1 = subprocess.Popen('networksetup -setwebproxy "'+ns+'" '+httpIP+' '+httpPort,shell=True)
    p2 = subprocess.Popen('networksetup -setsecurewebproxy "'+ns+'" '+httpIP+' '+httpPort,shell=True)
    p3 = subprocess.Popen('networksetup -setsocksfirewallproxy "'+ns+'" '+sockIP+' '+sockPort,shell=True)

def turn_off():
    p1 = subprocess.Popen('networksetup -setwebproxystate "'+ns+'" off',shell=True)
    p2 = subprocess.Popen('networksetup -setsecurewebproxystate "'+ns+'" off',shell=True)
    p3 = subprocess.Popen('networksetup -setsocksfirewallproxystate "'+ns+'" off',shell=True)

# 读取数据
data = []
for line in open("data.txt","r"):
    data.append(line[0:-1])
# print(data)

# 初始化窗口
window = tk.Tk()
window.title('ProxySeverClient')
window.geometry('300x400')

#设置开关代理的按钮
tk.Label(window, text='代理模式选择', font=('Arial', 10)).place(x=10, y=10)
var = tk.IntVar()
toggle1 = tk.Radiobutton(window,text='全局模式', font=('Arial', 10),variable=var, value=1, command=lambda: changeSwitch(1))
toggle1.place(x=10,y=30)
toggle2 = tk.Radiobutton(window,text='黑名单模式', font=('Arial', 10),variable=var, value=2, command=lambda: changeSwitch(2))
toggle2.place(x=150,y=30)
toggle3 = tk.Radiobutton(window,text='白名单模式(PAC)', font=('Arial', 10),variable=var, value=3, command=lambda: changeSwitch(3))
toggle3.place(x=10,y=60)
toggle4 = tk.Radiobutton(window,text='关闭', font=('Arial', 10),variable=var, value=4, command=lambda: changeSwitch(0))
toggle4.place(x=150,y=60)

# 设置代理服务器地址以及端口
tk.Label(window, text='代理端口选择', font=('Arial', 10)).place(x=10, y=100)
tk.Label(window, text='Http主机', font=('Arial', 10)).place(x=10, y=120)
tk.Label(window, text='Http端口', font=('Arial', 10)).place(x=200, y=120)
addr = tk.StringVar(value=data[0])
httpAddress = tk.Entry(window, textvariable=addr, show='', font=('Arial', 10),width=24)
httpAddress.place(x=10,y=140)
port = tk.StringVar(value=data[1])
httpPort = tk.Entry(window, textvariable=port, show='', font=('Arial', 10), width=8)
httpPort.place(x=200,y=140)

tk.Label(window, text='Sock主机', font=('Arial', 10)).place(x=10, y=170)
tk.Label(window, text='Sock端口', font=('Arial', 10)).place(x=200, y=170)
addr = tk.StringVar(value=data[2])
sockAddress = tk.Entry(window, textvariable=addr, show='', font=('Arial', 10),width=24)
sockAddress.place(x=10,y=190)
port = tk.StringVar(value=data[3])
sockPort = tk.Entry(window, textvariable=port, show='', font=('Arial', 10), width=8)
sockPort.place(x=200,y=190)

tk.Label(window, text='避开代理(黑名单)', font=('Arial', 10)).place(x=10, y=230)
bl = tk.StringVar(value=data[4])
blacklist = tk.Entry(window, textvariable=bl, show='', font=('Arial', 10), width=40)
blacklist.place(x=10,y=250)

tk.Label(window, text='PAC文件位置', font=('Arial', 10)).place(x=10, y=290)
wl = tk.StringVar(value=data[5])
whitelistURL = tk.Entry(window, textvariable=wl, show='', font=('Arial', 10), width=40)
whitelistURL.place(x=10,y=310)

save = tk.Button(window, text=' 保存配置 ', font=('Arial', 10), command=lambda: saveInfo())
save.place(x=10,y=350)

# 获取networkservice
p = subprocess.Popen('networksetup -listnetworkserviceorder', stdout=subprocess.PIPE, shell=True)
out, err = p.communicate()
status = p.wait()
# print(out.decode())
x1 = str(out).find('(1)')
x2 = str(out).find('(Hardware Port')
ns = str(out)[x1+4:x2-2]

# 运行主窗口
if __name__=='__main__':
    window.mainloop()
