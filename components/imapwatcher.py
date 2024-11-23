import imaplib

class IMAPWatcher:
    def __init__(self, email, password, imap_server, imap_port, email_sender):
        self.email = email
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.email_sender = email_sender

        self.imap = None

    def connect(self):
        self.imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        try:
            self.imap.login(self.email, self.password)
        except Exception as e:
            print(e)
        self.imap.select('inbox') # select inbox

    def disconnect(self):
        self.imap.close()
        self.imap.logout()

        self.imap = None

    # Get latest email from defined sender
    def get_latest_email(self):
        status, messages = self.imap.search(None, 'FROM', self.email_sender)
        latest_email_id = messages[-1]

        status, email_data = self.imap.fetch(latest_email_id, '(RFC822)')
        email_body = email_data[0][1]

        return email_body