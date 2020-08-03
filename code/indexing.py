import os
import io
import csv
import json
import pysolr
from nltk import tokenize
from nltk.corpus import stopwords
import collections
import pandas as pd


"""Indexing all the files to Apache-solr server"""

class indexing:

    """
    Reading files from the data set(local disk) and storing it with
    corresponding filename.
    """
    def readfiles(self,path):
        data=[] #to store data in the file
        file_list=[]  #to store the name of the files
        for file in sorted(os.listdir(path),key=lambda x: int(x.split('.')[0])):
            with io.open(path + file, 'r', encoding='utf-8', errors='ignore') as f:
                data.append(f.read())
            file_list.append(file)
        return data,file_list

    """
    Tokenizing each files and storing it in the data list
    """
    def tokenizing(self,data):

        for i in range(len(data)):
            sentences = tokenize.sent_tokenize(data.pop(i).strip())
            temp = sentences.pop(0).split('\n\n')
            if len(temp) == 2:
                sentences.insert(0, temp[1])
            data.insert(i, sentences)
        return data

    """
    Performing word tokenizing for each files and 
    removing the stopwords like 'the','that'...etc 
    """
    def indexing_words(self,data,file_list):
        indexedWord=collections.OrderedDict()
        indexedSentence = collections.OrderedDict()
        for i in range(len(data)):
            index=file_list[i]
            indexedWord[index]=[]
            for sentence in data[i]:
                indexedWord[index].extend(list(set(tokenize.word_tokenize(sentence))))
            indexedWord[index]=self.removing_stopwords(indexedWord[index])
        return indexedWord

    """
    Removing stopwords
    """
    def removing_stopwords(self,indexedwords):
        stop_words=stopwords.words("english")
        temp=[]
        for word in indexedwords:
            if word.lower() not in stop_words:
                temp.append(word)
        return temp


    """
    Starting of preprocessing
    """
    def preprocess(self,path):
        print("Preprocessing...")
        data,file_list=self.readfiles(path)
        data=self.tokenizing(data)
        indexWord=self.indexing_words(data,file_list)

        wordsDFrame = pd.DataFrame(list(indexWord.items()), columns=['id', 'words'])
        jsonFileName = 'words.json'
        wordsDFrame.to_json(jsonFileName, orient='records')
        return jsonFileName,indexWord,data,file_list

    """
    Adding the json file to Apache-solr
    """
    def add_to_solr(self,jsonFileName):
        solr=pysolr.Solr('http://localhost:8983/solr/semantic')
        solr.delete(q='*:*')
        with open("/Users/dinesh dk/Documents/mindtree/code/" + jsonFileName,'rb') as jsonFile:
            entry = json.load(jsonFile)
        solr.add(entry)
        #print("added")

    """performing searching in Apache-solr"""
    def searchInSolr(self,query, indexSentenceMap,data,file_list):
        solr = pysolr.Solr('http://localhost:8983/solr/semantic')
        query = "words:" + " || words:".join(query)
        print("Search Query: ", query)
        results = solr.search(query)
        for result in results:
            d=result['id']
            ind=file_list.index(d)
            print(d,"".join(data[ind]),sep="\n")
            print("\n\n")


    def returnpath(self):
        return "/Users/dinesh dk/Documents/mindtree/Data Set/"



if __name__ == '__main__':
    indexing_obj=indexing()
    path="/Users/dinesh dk/Documents/mindtree/Data Set/"
    jsonfilename,indexwords,data,file_list=indexing_obj.preprocess(path)
    indexing_obj.add_to_solr(jsonfilename)
    # query=input("Enter the query:")
    # indexing_obj.searchInSolr(list(set(tokenize.word_tokenize(query))),indexwords,data,file_list)