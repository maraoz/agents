'''Example script to generate text from Nietzsche's writings.

At least 20 epochs are required before the generated text
starts sounding coherent.

It is recommended to run this script on GPU, as recurrent
networks are quite computationally intensive.

If you try this script on new data, make sure your corpus
has at least ~100k characters. ~1M is better.
'''

from __future__ import print_function
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import numpy as np
import random
import sys

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

#Variables that contains the user credentials to access Twitter API 
access_token = "14427338-qTKP9eaTUtVhctkw9VzKlyEaunQyLwzL5nRhoOdcH"
access_token_secret = "VNwfXQYrOrpfEtuWDUDD7lTWddhSrUBYVb09RvNIyKG0P"
consumer_key = "u4wa6Q14ivCu1M6sE4o1Q"
consumer_secret = "7URlnEg8mQaIp009v1N0nCujNNlAutKRPTnB8A5USYU"


path = get_file('nietzsche.txt', origin="https://s3.amazonaws.com/text-datasets/nietzsche.txt")
text = open(path).read().lower()
print('corpus length:', len(text))

chars = sorted(list(set(text)))
print('total chars:', len(chars))
c2i = dict((c, i) for i, c in enumerate(chars))
i2c = dict((i, c) for i, c in enumerate(chars))

text = None

# cut the text in semi-redundant sequences of maxlen characters
maxlen = 14
step = 3



# build the model: a single LSTM
print('Build model...')
model = Sequential()
model.add(LSTM(128, input_shape=(maxlen, len(chars))))
model.add(Dense(len(chars)))
model.add(Activation('softmax'))

optimizer = RMSprop(lr=0.01)
model.compile(loss='categorical_crossentropy', optimizer=optimizer)


def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

iteration = 0

class StdOutListener(StreamListener):

    def on_error(self, status):
        print(status)

    def on_status(self, status):
        author = status.author
        print('*'*50)
        print(author.screen_name, author.followers_count, status.text)
        print('*'*50)
        text = status.text.lower()
        nonascii = ''.join([c for c in text if ord(c) >= 128])
        if len(nonascii) > 0:
            print('tweet skipped.')
            fout.write(nonascii)
            fout.flush()
            return
        global iteration
        iteration += 1
        print('Iteration', iteration)

        sentences = []
        next_chars = []
        for i in range(0, len(text) - maxlen, step):
            sentence = text[i: i + maxlen]
            sentences.append(sentence)
            next_chars.append(text[i + maxlen])

    def learn(self):
        print('Vectorization...')
        X = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
        y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
        for i, sentence in enumerate(sentences):
            for t, char in enumerate(sentence):
                X[i, t, c2i[char]] = 1
            y[i, c2i[next_chars[i]]] = 1
        model.fit(X, y, batch_size=128, nb_epoch=1)
        print('Model fitted')

        start_index = random.randint(0, len(text) - maxlen - 1)

        if iteration % 50 is not 0:
            return
        for diversity in [0.2, 0.5]:
            print()
            print('----- diversity:', diversity)

            generated = ''
            sentence = text[start_index: start_index + maxlen]
            generated += sentence
            print('----- Generating with seed: "' + sentence + '"')
            sys.stdout.write(generated)

            for i in range(140 - len(sentence)):
                x = np.zeros((1, maxlen, len(chars)))
                for t, char in enumerate(sentence):
                    ind = c2i[char]
                    x[0, t, ind] = 1.

                preds = model.predict(x, verbose=0)[0]
                next_index = sample(preds, diversity)
                next_char = i2c[next_index]

                generated += next_char
                sentence = sentence[1:] + next_char

                sys.stdout.write(next_char)
                sys.stdout.flush()
            print()



if (sys.stdout.encoding is None):
    print >> sys.stderr, "please set python env PYTHONIOENCODING=UTF-8, example: export PYTHONIOENCODING=UTF-8, when write to stdout."
    exit(1)



l = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, l)

#This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
stream.filter(track=['i'], async=False)
