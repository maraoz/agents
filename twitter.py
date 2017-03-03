#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

#Variables that contains the user credentials to access Twitter API 
access_token = "14427338-qTKP9eaTUtVhctkw9VzKlyEaunQyLwzL5nRhoOdcH"
access_token_secret = "VNwfXQYrOrpfEtuWDUDD7lTWddhSrUBYVb09RvNIyKG0P"
consumer_key = "u4wa6Q14ivCu1M6sE4o1Q"
consumer_secret = "7URlnEg8mQaIp009v1N0nCujNNlAutKRPTnB8A5USYU"

import codecs
import os
import sys

batch = 0
currentFile = lambda isComplete=False: 'data/tweets.%d.txt%s' % \
        (batch, '' if isComplete else '.part')
fout = codecs.open(currentFile(), 'a', encoding="utf-8")

amount = -1
class StdOutListener(StreamListener):

    def on_error(self, status):
        print status

    def on_status(self, status):
        global amount, fout, batch
        amount += 1
        if amount % 10 == 0:
            size = os.fstat(fout.fileno()).st_size
            print('Parsed', amount, 'tweets')
            print('size', size)
            if size > 1e5:
                fout.close()
                os.rename(currentFile(), currentFile(True))
                batch += 1
                fout = codecs.open(currentFile(), \
                        'a', encoding="utf-8")
        
        author = status.author
        fout.write(status.text+'\n')
        fout.flush()


if __name__ == '__main__':

    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    stream.filter(track=['I'], async=False)
