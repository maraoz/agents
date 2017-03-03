from __future__ import print_function
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

if (sys.stdout.encoding is None):
    print >> sys.stderr, "please set python env PYTHONIOENCODING=UTF-8, example: export PYTHONIOENCODING=UTF-8, when write to stdout."
    exit(1)


from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import numpy as np
import random
import time
import codecs
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler






fout = codecs.open('base.txt', 'a')
base_text = open('base.txt').read().lower()
maxlen = 14
step = 3
chars = sorted(list(set(base_text)))
print('total chars:', len(chars))
c2i = dict((c, i) for i, c in enumerate(chars))
i2c = dict((i, c) for i, c in enumerate(chars))


class MyHandler(FileSystemEventHandler):

    model = None

    def sample(self, preds, temperature=1.0):
        # helper function to sample an index from a probability array
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return np.argmax(probas)

    def learn(self, file_name):
        print('New data source! %s' % file_name)
        text = open(file_name).read().lower()
        nonascii = ''.join([c for c in text if ord(c) >= 128])
        if len(nonascii) > 0:
            fout.write(nonascii)
            fout.flush()

        # build the model: a single LSTM
        if not self.model:
            print('Build model...')
            self.model = Sequential()
            self.model.add(LSTM(128, input_shape=(maxlen, len(chars))))
            self.model.add(Dense(len(chars)))
            self.model.add(Activation('softmax'))

            optimizer = RMSprop(lr=0.01)
            self.model.compile(loss='categorical_crossentropy', optimizer=optimizer)


        sentences = []
        next_chars = []
        for i in range(0, len(text) - maxlen, step):
            sentence = text[i: i + maxlen]
            sentences.append(sentence)
            next_chars.append(text[i + maxlen])

        print('Vectorization...')
        X = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
        y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
        for i, sentence in enumerate(sentences):
            for t, char in enumerate(sentence):
                ind = c2i.get(char)
                if ind is None:
                    continue
                X[i, t, ind] = 1
            next_ind = c2i.get(next_chars[i])
            if next_ind is None:
                continue
            y[i, next_ind] = 1
        self.model.fit(X, y, batch_size=128, nb_epoch=1)
        print('Model fitted')

        start_index = random.randint(0, len(text) - maxlen - 1)

        for diversity in [0.2, 0.5, 1.0, 1.2]:
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

                preds = self.model.predict(x, verbose=0)[0]
                next_index = self.sample(preds, diversity)
                next_char = i2c[next_index]

                generated += next_char
                sentence = sentence[1:] + next_char

                sys.stdout.write(next_char)
                sys.stdout.flush()
            print()
        print('Done with file %s' % file_name)
        print('Waiting for new data feeds...')

    def on_created(self, event):
        if 'part' in event.src_path:
            return
        self.learn(event.src_path)

    def on_moved(self, event):
        if 'part' in event.dest_path:
            return
        self.learn(event.dest_path)


print('Waiting for new data feeds...')

event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path='data/', recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
