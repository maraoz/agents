#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

#Variables that contains the user credentials to access Twitter API 
access_token = "14427338-qTKP9eaTUtVhctkw9VzKlyEaunQyLwzL5nRhoOdcH"
access_token_secret = "VNwfXQYrOrpfEtuWDUDD7lTWddhSrUBYVb09RvNIyKG0P"
consumer_key = "u4wa6Q14ivCu1M6sE4o1Q"
consumer_secret = "7URlnEg8mQaIp009v1N0nCujNNlAutKRPTnB8A5USYU"


#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_error(self, status):
        print status

    def on_status(self, status):
        author = status.author
        print('*'*80)
        print(author.screen_name, author.followers_count, status.text)


if __name__ == '__main__':

    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    stream.filter(track=['bitcoin'], async=False)
