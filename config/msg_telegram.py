import telegram
import os

class Telegram_Bot():
    def __init__(self):

        self.tele_token = ''
        self.chat_id = ''

        test = 0        # 0: 실투 텔레그램 봇
        base_dir = 'D:/AutoTrading_real/security'

        f = open('D:/AutoTrading_real/security/pwd.csv')
        lines = f.readlines()

        if test == 0:       # 실투
            self.tele_token = lines[2].split(',')[-1].rstrip('\n')
            # print(self.tele_token)
        else:
            self.tele_token = lines[4].split(',')[-1].rstrip('\n')
            # print(self.tele_token)
        self.bot = telegram.Bot(token=self.tele_token)
        # updates = self.bot.getUpdates()
        # # print(updates)
        # self.chat_id = updates[-1].message.chat_id

        # chat_id 오류 때문에 수정 _ 200901
        if self.chat_id == '':
            if os.path.exists(base_dir + '/chat_id.txt'):
                with open(base_dir + '/chat_id.txt', mode='r') as chatfile:
                    try:
                        self.chat_id = int(chatfile.readline().strip())
                    except Exception as e:
                        pass

        if self.chat_id == '':
            updates = self.bot.getUpdates()
            last_message = None
            for u in updates:
                if u is not None:
                    last_message = u

            if last_message is not None:
                self.chat_id = last_message.message.chat_id
                with open(base_dir + '/chat_id.txt', mode='w') as chatfile:
                    chatfile.write('%s' % self.chat_id)

    def send_tele_msg(self, text):
        chat_id = self.chat_id
        self.bot.sendMessage(chat_id=chat_id, text=text)

if __name__ == '__main__':
    Telegram_Bot().__init__()
    Telegram_Bot().send_tele_msg('테스트')