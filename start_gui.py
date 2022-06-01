import tkinter as tk
import tkinter.messagebox
from PIL import Image, ImageTk
import pickle

from crawler import run_run

# 第1步，实例化object，建立窗口window
window = tk.Tk()

# 第2步，给窗口的可视化起名字
window.title('Instagram Crawler')

# 第3步，设定窗口的大小(长 * 宽)
window.geometry('350x450')  # 这里的乘是小x

# 第4步，加载 welcome image
canvas = tk.Canvas(window, width=879, height=135, bg='green')
img = Image.open(r'Instagram-Cover-Photo-copy-1.jpg')
i_w, i_h = img.size
img = img.resize((int(i_w*0.4), int(i_h*0.4)), Image.ANTIALIAS)
image_file = ImageTk.PhotoImage(img)
image = canvas.create_image(175, 0, anchor='n', image=image_file)
canvas.pack(side='top', ) # side='top'
tk.Label(window, text='',font=('Arial', 2)).pack()
tk.Label(window, text='Input hashtags to be crawled',font=('Arial', 16)).pack()

# Step 4.1 Hashtag input box
hashtags_text = tk.Text(window, height=10, width=56)
hashtags_text.place(x=2, y=170)

# 第5步，用户信息
tk.Label(window, text='Ins  name:', font=('Arial', 14)).place(x=10, y=290)
tk.Label(window, text='Password:',  font=('Arial', 14)).place(x=10, y=330)

# 第6步，用户登录输入框entry
# 用户名
var_usr_name = tk.StringVar()
# var_usr_name.set('example@python.com')
entry_usr_name = tk.Entry(window, textvariable=var_usr_name, font=('Arial', 14))
entry_usr_name.place(x=120, y=290)
# 用户密码
var_usr_pwd = tk.StringVar()
entry_usr_pwd = tk.Entry(window, textvariable=var_usr_pwd, font=('Arial', 14), show='*')
entry_usr_pwd.place(x=120, y=330)

# 第8步，定义用户登录功能
def crawling():
    # 这两行代码就是获取用户输入的usr_name和usr_pwd
    usr_name = var_usr_name.get()
    usr_pwd = var_usr_pwd.get()
    hashtags =  hashtags_text.get(0.0, tk.END)
    print(hashtags)
    tag_list = []
    for tag in hashtags.strip().rstrip("\n").split("\n"):
        if len(tag) > 0:
            tag_list.append(tag)
    # print('===')
    # print(tag_list)
    run_run(usr_name, usr_pwd, tag_list)



# 第9步，定义用户注册功能
def usr_sign_up():
    def sign_to_Hongwei_Website():
        # 以下三行就是获取我们注册时所输入的信息
        np = new_pwd.get()
        npf = new_pwd_confirm.get()
        nn = new_name.get()

        # 这里是打开我们记录数据的文件，将注册信息读出
        with open('usrs_info.pickle', 'rb') as usr_file:
            exist_usr_info = pickle.load(usr_file)
        # 这里就是判断，如果两次密码输入不一致，则提示Error, Password and confirm password must be the same!
        if np != npf:
            tkinter.messagebox.showerror('Error', 'Password and confirm password must be the same!')
 
        # 如果用户名已经在我们的数据文件中，则提示Error, The user has already signed up!
        elif nn in exist_usr_info:
            tkinter.messagebox.showerror('Error', 'The user has already signed up!')
 
        # 最后如果输入无以上错误，则将注册输入的信息记录到文件当中，并提示注册成功Welcome！,You have successfully signed up!，然后销毁窗口。
        else:
            exist_usr_info[nn] = np
            with open('usrs_info.pickle', 'wb') as usr_file:
                pickle.dump(exist_usr_info, usr_file)
            tkinter.messagebox.showinfo('Welcome', 'You have successfully signed up!')
            # 然后销毁窗口。
            window_sign_up.destroy()
 
    # 定义长在窗口上的窗口
    window_sign_up = tk.Toplevel(window)
    window_sign_up.geometry('300x200')
    window_sign_up.title('Sign up window')
 
    new_name = tk.StringVar()  # 将输入的注册名赋值给变量
    new_name.set('example@python.com')  # 将最初显示定为'example@python.com'
    tk.Label(window_sign_up, text='User name: ').place(x=10, y=10)  # 将`User name:`放置在坐标（10,10）。
    entry_new_name = tk.Entry(window_sign_up, textvariable=new_name)  # 创建一个注册名的`entry`，变量为`new_name`
    entry_new_name.place(x=130, y=10)  # `entry`放置在坐标（150,10）.
 
    new_pwd = tk.StringVar()
    tk.Label(window_sign_up, text='Password: ').place(x=10, y=50)
    entry_usr_pwd = tk.Entry(window_sign_up, textvariable=new_pwd, show='*')
    entry_usr_pwd.place(x=130, y=50)
 
    new_pwd_confirm = tk.StringVar()
    tk.Label(window_sign_up, text='Confirm password: ').place(x=10, y=90)
    entry_usr_pwd_confirm = tk.Entry(window_sign_up, textvariable=new_pwd_confirm, show='*')
    entry_usr_pwd_confirm.place(x=130, y=90)
 
    # 下面的 sign_to_Hongwei_Website
    btn_comfirm_sign_up = tk.Button(window_sign_up, text='Sign up', command=sign_to_Hongwei_Website)
    btn_comfirm_sign_up.place(x=180, y=120)

# 第7步，login and sign up 按钮
btn_login = tk.Button(window, text='Crawl', font=('Arial', 16), command=crawling)
btn_login.place(x=140, y=390)

# btn_sign_up = tk.Button(window, text='Sign up', command=usr_sign_up)
# btn_sign_up.place(x=200, y=360)

# 第10步，主窗口循环显示
window.mainloop()
