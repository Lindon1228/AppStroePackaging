#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2018/12/1 21:14
# @Author  : haven
# @Site    :
# @File    : auto_archive_ios.py
# @Software: PyCharm


import os
import requests
import webbrowser
import subprocess
import time
import smtplib
from email.mime.text import MIMEText
from email import encoders
from email.header import Header
from email.utils import parseaddr, formataddr

project_name = 'xxx'    # 项目名称
archive_workspace_path = 'xxxxxxxxxx'    # 项目路径 如果是pods则是.xcworkspace文件的路径
export_ipa_path = 'xxxxxxx'    # 输出的文件夹
exportOptions_plist_path = 'xxxxxxxxxx/ExportOptions.plist'    # ExportOptions.plist文件路径 exportOptionsPlist 文件需要在之前通过xcode打包导出ipa时的文件夹中去找




ipa_download_url = 'https://www.pgyer.com/xxx' #蒲公英的APP地址


# 蒲公英账号USER_KEY、API_KEY
USER_KEY = 'xxxxxx'
API_KEY = 'xxxxxxx'

from_address = 'xxx@qq.com'    # 发送人的地址
password = 'xxx'  # 邮箱密码换成他提供的16位授权码
to_address = 'xxx@qq.com'    # 收件人地址,可以是多个的
smtp_server = 'smtp.qq.com'    # 因为我是使用QQ邮箱..

altool_path = "/Applications/Xcode.app/Contents/Developer/usr/bin/altool"#altool的路径
user_id = "xxxxxx"#AppleID
pass_word = "xxxxxx"#AppleID的密码 注意这个密码也可能是专用密码
noError = 0

class AutoArchive(object):
    """自动打包并上传到蒲公英,发邮件通知"""

    def __init__(self):
        pass

    def clean(self):
        print("\n\n===========开始clean操作===========")
        start = time.time()
        clean_command = 'xcodebuild clean -workspace %s/%s.xcworkspace -scheme %s -configuration Release' % (
            archive_workspace_path, project_name, project_name)
        clean_command_run = subprocess.Popen(clean_command, shell=True)
        clean_command_run.wait()
        end = time.time()
        # Code码
        clean_result_code = clean_command_run.returncode
        if clean_result_code != 0:
            print("=======clean失败,用时:%.2f秒=======" % (end - start))
        else:
            print("=======clean成功,用时:%.2f秒=======" % (end - start))
#            self.archive()
        self.upload_appstore()
#           self.upload('%s/%s.ipa' % (export_ipa_path, project_name))


    def archive(self):
        print("\n\n===========开始archive操作===========")

        # 删除之前的文件
        subprocess.call(['rm', '-rf', '%s' % export_ipa_path])
        time.sleep(1)
        
#        # 创建文件夹存放打包文件
#        subprocess.call(['mkdir', '-p', '%s/%s' % (archive_workspace_path, export_directory)])
#        time.sleep(1)
        # 创建文件夹存放打包文件
        subprocess.call(['mkdir', '-p', '%s' % export_ipa_path])
        time.sleep(1)

        start = time.time()
        archive_command = 'xcodebuild archive -workspace %s/%s.xcworkspace -scheme %s -configuration Release -archivePath %s' % (
            archive_workspace_path, project_name, project_name, export_ipa_path)
        archive_command_run = subprocess.Popen(archive_command, shell=True)
        archive_command_run.wait()
        end = time.time()
        # Code码
        archive_result_code = archive_command_run.returncode
        if archive_result_code != 0:
            print("=======archive失败,用时:%.2f秒=======" % (end - start))
        else:
            print("=======archive成功,用时:%.2f秒=======" % (end - start))
            # 导出IPA
            self.export()

    def export(self):
        print("\n\n===========开始export操作===========")
        print("\n\n==========请你耐心等待一会~===========")
        start = time.time()
#        export_command = 'xcodebuild -exportArchive -archivePath /Users/haven/Documents/xxx/archive.xcarchive -exportPath /Users/haven/Documents/xxx/archive -exportOptionsPlist /Users/haven/Documents/xxx/ExportOptions.plist'
#        export_command = 'xcodebuild -exportArchive -archivePath %s/%s.xcarchive -exportPath %s/%s -exportOptionsPlist %s' % (
#             archive_workspace_path, export_directory, archive_workspace_path, export_directory, exportOptions_plist_path)

        export_command = 'xcodebuild -exportArchive -archivePath %s.xcarchive -exportPath %s -exportOptionsPlist %s' % (
                  export_ipa_path, export_ipa_path, exportOptions_plist_path)
        export_command_run = subprocess.Popen(export_command, shell=True)
        export_command_run.wait()
        end = time.time()
        # Code码
        export_result_code = export_command_run.returncode
        if export_result_code != 0:
            print("=======导出IPA失败,用时:%.2f秒=======" % (end - start))
        else:
            print("=======导出IPA成功,用时:%.2f秒=======" % (end - start))
            # 删除archive.xcarchive文件
            subprocess.call(['rm', '-rf', '%s.xcarchive' % export_ipa_path])
            self.upload_appstore()


    #上传到App Store
    def upload_appstore(self):
        dirName = export_ipa_path
        ipa_path = dirName + '/' + project_name + '.ipa'
        print(ipa_path)

        if os.path.exists(ipa_path):
            print('正在验证ipa文件,请稍后...')
            r1 = os.system('%s -v -f %s -u %s -p %s -t ios [--output-format xml]' % (
            altool_path, ipa_path, user_id, pass_word))
            print("验证的结果是:")
            print(r1)
            if r1 == noError:
                print('正在上传ipa文件,请稍后...')
                r2 = os.system('%s --upload-app -f %s -t ios -u %s -p %s [--output-format xml]' % (
                altool_path, ipa_path, user_id, pass_word))
                print(r2)
                self.send_email()
            else:
                return
        else:
            print('没有找到.ipa文件')
            return

    def upload(self, ipa_path):
        print("\n\n===========开始上传蒲公英操作===========")
        if ipa_path:
            # https://www.pgyer.com/doc/api 具体参数大家可以进去里面查看,
            url = 'http://www.pgyer.com/apiv1/app/upload'
            data = {
                'uKey': USER_KEY,
                '_api_key': API_KEY,
                'installType': '1',
                'updateDescription': description
            }
            files = {'file': open(ipa_path, 'rb')}
            r = requests.post(url, data=data, files=files)
            if r.status_code == 200:
                # 是否需要打开浏览器
                 self.open_browser(self)
#                self.send_email()
        else:
            print("\n\n===========没有找到对应的ipa===========")
            return

    @staticmethod
    def open_browser(self):
        webbrowser.open(ipa_download_url, new=1, autoraise=True)

    @staticmethod
    def _format_address(self, s):
        name, address = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), address))

    def send_email(self):
        # https://www.pgyer.com/XXX app地址
        # 只是单纯的发了一个文本邮箱,具体的发附件和图片大家可以自己去补充
        msg = MIMEText('Hello' + '╮(╯_╰)╭应用已更新,请下载测试╮(╯_╰)╭' +
                       '蒲公英的更新会有延迟,具体版本时间以邮件时间为准' + '', 'html', 'utf-8')
        msg['From'] = self._format_address(self, 'iOS开发团队 <%s>' % from_address)
        msg['Subject'] = Header('来自iOS开发团队的问候……', 'utf-8').encode()
        server = smtplib.SMTP(smtp_server, 25)  # SMTP协议默认端口是25
        server.set_debuglevel(1)
        server.login(from_address, password)
        server.sendmail(from_address, [to_address], msg.as_string())
        server.quit()
        print("===========邮件发送成功===========")


if __name__ == '__main__':
    description = input("请输入内容:")
    archive = AutoArchive()
    archive.clean()
