# encoding=utf-8

"""
    @author: anzz
    @date: 2019/6/3
"""
import email
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app import celery
from communicate.withdrawal_content import WITHDRAWAL_VALIDATION_TITLE, \
    WITHDRAWAL_VALIDATION_CONTENT
from conf import USERNAME, PASSWORD
from logs import celery_logger


@celery.task()
def email_sender_task(to_mail, pass_code, frozen):
    """
    提现验证
    :param email:
    :param pass_code:
    :param frozen:
    :param lan:
    :return:
    """
    celery_logger.info("email_sender_task to_mail:%s, " % to_mail)

    mail_task(to_mail, WITHDRAWAL_VALIDATION_TITLE,
              WITHDRAWAL_VALIDATION_CONTENT.format(
                  code=pass_code, email=to_mail
              ))


def mail_task(to_email, title, content):
    rcptto = to_email

    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header(title).encode()
    msg['From'] = '%s <%s>' % (Header('F1pool').encode(), USERNAME)
    msg['To'] = rcptto
    msg['Message-id'] = email.utils.make_msgid()
    msg['Date'] = email.utils.formatdate()
    texthtml = MIMEText(content, _subtype='html', _charset='UTF-8')
    msg.attach(texthtml)
    client = smtplib.SMTP()
    client.connect('smtpdm.aliyun.com', 80)
    client.set_debuglevel(0)
    client.login(USERNAME, PASSWORD)
    client.sendmail(USERNAME, rcptto, msg.as_string())
    client.quit()
    return True


if __name__ == '__main__':
    mail_task("anzhaozhong@163.com", "hello", "qwer")
