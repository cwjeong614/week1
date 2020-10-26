from slacker import Slacker

class Slack():
    def __init__(self):

        f = open('E:/AutoTrading_5/security/pwd.csv')
        lines = f.readlines()

        pwd = lines[3].split(',')[-1].rstrip('\n')

        self.token = pwd

    def notification(self, pretext=None, title=None, fallback=None, text=None):
        attachments_dict = dict()
        attachments_dict['pretext'] = pretext       #test1
        attachments_dict['title'] = title           #test2
        attachments_dict['fallback'] = fallback     #test3
        attachments_dict['text'] = text             #test4

        attachments = [attachments_dict]

        slack = Slacker(self.token)
        slack.chat.post_message(channel='#autotrading', text=None, attachments=attachments, as_user=None)