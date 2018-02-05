
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import datetime


class EmailSender(object):
    """
    监控爬虫相应动态并将动态发送邮件到指定位置
    发送内容须含有msg字段和spidername字段
    """

    def __init__(self):
        pass

    @staticmethod
    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def sendmsg(self, spidermsg):
        """
        发送邮件
        :param spidermsg: 爬虫信息，必须为dict
        :return:
        """

        if isinstance(spidermsg, dict):
            spidermsg['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # 发件人地址，需开启smtp服务
            from_addr = 'myirelias@163.com'
            # smtp授权码(目前暂时限于163邮箱)
            password = '0107unkown'
            # 目标邮件地址
            to_addr = 'myirelia@aliyun.com'
            # smtp地址
            smtp_server = 'smtp.163.com'
            # 邮件主体
            msg = MIMEText('[%s]爸爸这里是你要的数据统计:\n\n%s' %
                           (spidermsg.get('time', ''), spidermsg.get('msg', '')), 'plain', 'utf-8')
            # 邮件发送人
            msg['From'] = self._format_addr('daqSoft Server<%s>' % from_addr)
            # 收件人信息
            msg['To'] = self._format_addr('spider owner<%s>' % to_addr)
            # 主题信息
            msg['Subject'] = Header('[%s]爸爸!你的数据反馈来啦' % spidermsg.get('spidername', ''), 'utf-8').encode()
            # 创建smtp服务，25为timeout
            server = smtplib.SMTP(smtp_server, 25)
            # 登录服务
            server.login(from_addr, password)
            # 发送邮件
            server.sendmail(from_addr, [to_addr], msg.as_string())
            # 退出服务
            server.quit()
        else:
            print('msg must be dict not %s' % type(spidermsg))
            return


