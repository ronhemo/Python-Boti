import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import tflearn
import tensorflow
import random
import json
import pickle

with open("chatbot/intents.json") as file:
    data = json.load(file)

try:
    with open("chatbot/data.pickle", "rb") as file:
        words, tags, training, output = pickle.load(file)
except:
    words =[]
    tags = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in tags:
            tags.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w not in "?"]
    words = sorted(list(set(words)))

    tags = sorted(tags)

    training = []
    output = []

    out_empty = [0 for _ in range(len(tags))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)
        
        output_row = out_empty[:]
        output_row[tags.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = numpy.array(training)
    output = numpy.array(output)

    with open("chatbot/data.pickle", "wb") as file:
        pickle.dump((words,tags, training, output), file)


tensorflow.compat.v1.reset_default_graph()
net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

try:
    model.load("chatbot/model.tflearn")
except:
    tensorflow.compat.v1.reset_default_graph()
    net = tflearn.input_data(shape=[None, len(training[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
    net = tflearn.regression(net)

    model = tflearn.DNN(net)
    model.fit(training, output, n_epoch=2000, batch_size=8, show_metric=True)
    model.save("chatbot/model.tflearn")

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]
    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i,w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)

def chat(message):
    results = model.predict([bag_of_words(message, words)])
    result_index = numpy.argmax(results)
    tag = tags[result_index]
    for tg in data["intents"]:
        if(tg["tag"] == tag):
            responses = tg["responses"]
            say = random.choice(responses)
            res = {}
            res["tag"] = tag
            res["response"] = say
            if(tag == "help"):
                res["response"] = "i can help you with: "
                for t in tags:
                    res["response"] += t + ", "
            return(res)