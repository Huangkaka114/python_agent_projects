import smtplib
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# from AgentFlow.utils import logger
from AgentFlow.utils import permission
from langchain.tools import tool
import subprocess
import os
from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, "../config/.env")
load_dotenv(dotenv_path=ENV_PATH)

@tool
@permission("admin")
def screenshot():
    """系统截图"""
    print("正在执行...")
    subprocess.Popen("snippingtool")
    return "✅ 截图已打开"

@tool
@permission("guest")
def play_music():
    """播放音乐"""
    # os.startfile("calc.exe")
    return "✅ 开始播放音乐"

@tool
@permission("admin")
def send_email(to_email: str, subject: str, content: str, attachment_path: str):
    """
         发送邮件（支持附件）
        使用163邮箱 SMTP 服务

    参数:
        to_email: 收件人邮箱
        subject: 邮件标题
        content: 邮件正文
        attachment_path: 附件路径（可选，不传则不带附件）
    """
    smtp_server = os.getenv("EMAIL_HOST")
    prot = int(os.getenv("EMAIL_PORT", 465))
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(content, "plain", "utf-8"))

    if attachment_path and os.path.exists(attachment_path):
        filename = os.path.basename(attachment_path)

        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())

            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename={filename}")
            msg.attach(part)
    try:
        # 163 邮箱 SSL 发送
        with smtplib.SMTP_SSL(smtp_server, prot, timeout=10) as server:
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())

        return f"✅ 邮件发送成功 → {to_email}，标题：{subject}"
    except Exception as e:

        return f"❌ 邮件发送失败：{str(e)}"