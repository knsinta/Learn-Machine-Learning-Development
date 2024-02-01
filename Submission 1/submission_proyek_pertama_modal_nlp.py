# -*- coding: utf-8 -*-
"""Submission Proyek Pertama: Modal NLP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xcqr9pom1-L6Q03W-jYKtBhPtDrLWzC6
"""

import pandas as pd

missing_values = ["n/a", "na", "--"]
df = pd.read_csv('McD_Reviews.csv', encoding="ISO-8859-1")

df = df.drop(['reviewer_id', 'store_name', 'category', 'store_address',
         'longitude', 'rating_count', 'review_time', 'latitude '], axis = 1)

df.info()

df.isna().sum()

df.head(1000)

import regex as re

def tokenize(text):
    split=re.split("\W+",text)
    return split
df['review_split']=df['review'].apply(lambda x: tokenize(x.lower()))
df.head(100)

import nltk as nltk
from nltk import corpus
from nltk.stem import PorterStemmer

nltk.download('stopwords')
stopword = nltk.corpus.stopwords.words('english')
print(stopword[:20])

def remove_stopwords(text):
    text=[word for word in text if word not in stopword]
    return text
df['review_text_stopwords'] = df['review_split'].apply(lambda x: remove_stopwords(x))
df.head(1000)

stemmer = nltk.stem.SnowballStemmer(language='english')
def stem_list(row):
    my_list = row['review_text_stopwords']
    stemmed_list = [stemmer.stem(word) for word in my_list]
    return (stemmed_list)

df['stemmed_review'] = df.apply(stem_list, axis=1)

df.head()

def rating_group(rate):
    group = rate['rating']
    global grouped_rate
    if rate['rating'] > '3 stars':
        grouped_rate = 'Good'
    elif rate['rating'] == '3 stars':
        grouped_rate = 'Neutral'
    elif rate['rating'] < '3 stars':
        grouped_rate = 'Bad'
    return grouped_rate

df['new_rating'] = df.apply(rating_group, axis=1)

df.head(1000)

df.tail(1000)

rating_category = pd.get_dummies(df.new_rating)
df_new = pd.concat([df, rating_category], axis=1)
df_new = df_new.drop(columns='rating')
df_new

review = df_new['stemmed_review'].values
label = df_new[['Good', 'Neutral', 'Bad']].values
label

from sklearn.model_selection import train_test_split

review_train, review_test,label_train, label_test = train_test_split(review, label, test_size=0.2, shuffle=False)

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

tokenizer = Tokenizer(num_words=10000, oov_token='x')
tokenizer.fit_on_texts(review_train)
tokenizer.fit_on_texts(review_test)

sequence_train = tokenizer.texts_to_sequences(review_train)
sequence_test = tokenizer.texts_to_sequences(review_test)

padded_train = pad_sequences(sequence_train, padding='post', maxlen=20, truncating='post')
padded_test = pad_sequences(sequence_test, padding='post', maxlen=20, truncating='post')

import tensorflow as tf

model = tf.keras.Sequential([
     tf.keras.layers.Embedding(input_dim=50000, output_dim=16),
     tf.keras.layers.BatchNormalization(),
     tf.keras.layers.Dropout(0.2),
     tf.keras.layers.LSTM(128),
     tf.keras.layers.Dense(128, activation='relu'),
     tf.keras.layers.Dropout(0.5),
     tf.keras.layers.Dense(128, activation='relu'),
     tf.keras.layers.Dropout(0.5),
     tf.keras.layers.Dense(3, activation='softmax')
     ])

model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy' and 'val_accuracy')>0.9):
      print("\nAkurasi telah mencapai >90%!")
      self.model.stop_training = True
callbacks = myCallback()

num_epochs = 100
history = model.fit(padded_train, label_train,
                    batch_size=128, epochs=num_epochs, callbacks=[callbacks],
                    validation_data=(padded_test, label_test), verbose=2)

import matplotlib.pyplot as plt

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper right')
plt.show()

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='lower right')
plt.show()