import email, email.header, sys
import imaplib, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class imapClient:
    imap = None

    # using outlook IMAP 
    def __init__(self, recipient, password, server='imap-mail.outlook.com', use_ssl=True, move_to_archive=True):
        if not recipient:
            raise ValueError('You must provide a recipient email address')

        self.recipient = recipient
        self.password = password
        self.use_ssl = use_ssl
        self.recipient_folder = 'INBOX'
        self.move_to_archive = move_to_archive

        if self.use_ssl:
            self.imap = imaplib.IMAP4_SSL(server)
        else:
            self.imap = imaplib.IMAP4(server)

    def login(self):
        try:
            rv, data = self.imap.login(self.recipient, self.password)
        except (imaplib.IMAP4_SSL.error, imaplib.IMAP4.error) as error:
            print("during IMAP login:", error)
            sys.exit(1)

    def logout(self):
        self.imap.close()
        self.imap.logout()

    def get_messages(self, subject):
        resp, _ = self.imap.select(self.recipient_folder)

        if resp != 'OK':
            print(f"ERROR: Unable to open the {self.recipient_folder} folder")
            sys.exit(1)

        messages = []
        mbox_response, msgnums = self.imap.uid('SEARCH', None, 'ALL')

        if mbox_response == 'OK':
            for num in msgnums[0].split():
                retval, rawmsg = self.imap.uid('FETCH', num, '(RFC822)')

                if retval != 'OK':
                    print('ERROR getting message', num)
                    continue
                
                msg = email.message_from_bytes(rawmsg[0][1])
                msg_subject = msg["Subject"]

                if subject in msg_subject:
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            type = part.get_content_type()
                            disp = str(part.get('Content-Disposition'))
                            # look for plain text parts, but skip attachments
                            
                            if type == 'text/plain' and 'attachment' not in disp:
                                charset = part.get_content_charset()
                                body = part.get_payload(decode=True).decode(encoding=charset, errors="ignore")
                                break
                    else:
                        # not multipart - i.e. plain text, no attachments
                        charset = msg.get_content_charset()
                        body = msg.get_payload(decode=True).decode(encoding=charset, errors="ignore")

                    messages.append({'num': num, 'subject': msg_subject, 'body': body})
        return messages

    def move_message(self, msg_uid):
        if not msg_uid:
            return

        # Copy msg to archive folder
        self.imap.uid('COPY',msg_uid, 'Archive')

        # Flag original msg for deletion
        self.imap.uid('STORE', msg_uid, '+FLAGS', '\\Deleted')
        
        # Delete original msg
        self.imap.expunge()

class smtpClient:
    smtp = None

    # using outlook SMTP
    def __init__(self, sender, password, server="smtp-mail.outlook.com", port=587, use_ssl=True):
        if not sender:
            raise ValueError('You must provide a sender email address')

        self.sender = sender
        self.password = password
        self.use_ssl = use_ssl

        ssl_context = ssl.create_default_context()
        self.smtp = smtplib.SMTP(server, port)
        self.smtp.starttls(context=ssl_context)

    def login(self):
        try:
            self.smtp.login(self.sender, self.password)

        except (smtplib.SMTPException) as error:
            print("during SMTP login:", error)
            sys.exit(1)
    
    def logout(self):
        self.smtp.quit()

    def send_message(self, receiver, msg_subject, msg_body):
        try: 
            msg = MIMEMultipart()
            msg['Subject'] = "%s" % (msg_subject)
            text = msg_body
            msg.attach(MIMEText(text, 'plain'))
            self.smtp.sendmail(self.sender, receiver, msg.as_string())
            
        except (smtplib.SMTPException) as error:
            msg = MIMEMultipart()
            msg['Subject'] = "Error when sending mail, check error and fix script ASAP!"
            msg.attach(MIMEText(error, 'plain'))
            self.smtp.sendmail(self.sender, receiver, msg.as_string())
            sys.exit(1)
