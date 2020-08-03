from indexing import indexing
from nltk import tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from autocorrect import spell
from textblob import TextBlob
from nltk import pos_tag
from wiki import url
import pysolr
import collections
import pandas as pd
import json
import os

class queryProcessing:

    def __init__(self):
        self.datafile=None

    """Function to tokenize the search input"""
    def tokenize(self,query):
        token_list=list(set(word_tokenize(query)))
        return token_list

    """function that separates stopwords from
    the search query"""
    def removing_stopwords(self,query):
        nonStopWords=[]
        stopWordsList=[]
        stopWord=stopwords.words("english")
        for word in query:
            if word not in stopWord:
                nonStopWords.append(word)
            elif word=='won':
                nonStopWords.append(word)
            else:
                stopWordsList.append(word)
        return nonStopWords,stopWordsList


    def stemming(self,query):
        temp=[]
        stemmed=PorterStemmer()
        for i in query:
            temp.append(stemmed.stem(i))
        return query+temp

    def lemmatizing(self,query):
        temp=[]
        lem=WordNetLemmatizer()
        for word in query:
            temp.append(lem.lemmatize(word))
        return query+temp

    """function that finds synonyms
    to the search query"""
    def synonyms(self,query):
        temp=[]
        for word in query:
            for mean in wordnet.synsets(word):
                for l in mean.lemmas():
                    syn=l.name()
                    lst=syn.split('_')
                    temp.extend(lst)
        return temp


    """performing autocorrection to search query"""
    def autocorrection(self,query):
        temp=[]
        for word in query:
            temp.append(spell(word))
        return temp

    def partsOfSpeech(self,query):
        temp=[]
        return pos_tag(query)

    def searchInSolr(self,query):

        solr = pysolr.Solr('http://localhost:8983/solr/semantic')
        query = "words:" + " || words:".join(query)
        print("Search Query: ", query)
        results = solr.search(query)

        return results

    def test(self):
        return "working"

    def finding_matches(self,querylist,data):
        for sent in range(len(data)):
            for query in querylist:
                if query.lower() in data[sent].lower():
                    return sent

    def file_return(self,filename):
        f=open("/Users/dinesh dk/Documents/mindtree/Data Set/"+filename,'r')
        return f.read().split('\n')

    def file_return1(self,filename):
        f=open("/Users/dinesh dk/Documents/mindtree/Data Set/"+filename,'r')
        return f.read()


    """Suggestions finding"""
    def related_words(self,words):
        suggestion = []
        for word in words:
            syns = wordnet.synsets(word)
            if len(syns) > 0:
                for sug in syns[0].hypernyms():
                    res=sug.name()[:-5].capitalize()
                    ress=res.replace('_',' ')
                    suggestion.append(ress)
                for sug in syns[0].hyponyms():
                    res=sug.name()[:-5].capitalize()
                    ress=res.replace('_',' ')
                    suggestion.append(ress)
        return suggestion

    def suggestions_finding(self,tagged):
        related=[]
        for pos in tagged:
            if pos[1] == 'NN':
                related.append(pos[0])
        if len(related)>0:
            suggestion=self.related_words(related)
            wikipedia=url(related[0])
            return suggestion,wikipedia,related[0]
        else:
            return [],"",""

    """starting of the search"""
    def starting_search(self,query):
        matchingfiles = []
        resultlist = []
        final = collections.OrderedDict()
        tokenized_list = self.tokenize(query)
        stopwordsRemovedList, stopwordsList = self.removing_stopwords(tokenized_list)
        pos = self.partsOfSpeech(stopwordsRemovedList)

        try:
            suggestion,wikipedia,wiki_word=self.suggestions_finding(pos)
        except:
            suggestion,wikipedia,wiki_word=[],"",""

        final['wikipedia']=[wiki_word,wikipedia]
        final['suggestion']=[len(suggestion),suggestion]

        tokenized_list.insert(0, query)
        result1 = self.searchInSolr(set(tokenized_list))
        resultlist.append(result1)

        stemmedList = self.stemming(tokenized_list)
        lemmmatizedList = self.lemmatizing(stemmedList)
        thesaurusAddedList = self.synonyms(lemmmatizedList)

        if len(thesaurusAddedList) > 0:
            processedFinalSearchList = lemmmatizedList + thesaurusAddedList
        else:
            processedFinalSearchList = lemmmatizedList + self.autocorrection(stopwordsRemovedList)


        result2 = self.searchInSolr(set(processedFinalSearchList + stopwordsList))
        resultlist.append(result2)

        for results in resultlist:
            for result in results:
                d = result['id']
                if d not in matchingfiles:
                    file=self.file_return1(d)
                    indexing_obj = indexing()
                    data = indexing_obj.tokenizing([file])
                    sent = self.finding_matches(processedFinalSearchList, data[0])
                    index1="".join(data[0][sent])
                    index2="".join(data[0][sent:])
                    final[d] = [index1,index2]


        return final






# if __name__ == '__main__':
#
#     matchingfiles=[]
#     resultlist=[]
#     final={}
#
#     indexing_obj=indexing()
#     path=indexing_obj.returnpath()
#     data,file_list=indexing_obj.readfiles(path)
#     data=indexing_obj.tokenizing(data)
#     qp=queryProcessing()
#
#     query=input("Enter the query:")
#     query_list=qp.tokenize(query)
#     query_list1,stopwordsList=qp.removing_stopwords(query_list)
#
#     pos=qp.partsOfSpeech(query_list1)
#
#     query_list.insert(0,query)
#     result1 = qp.searchInSolr(set(query_list))
#     resultlist.append(result1)
#
#     query_list=qp.stemming(query_list1)
#     query_list=qp.lemmatizing(query_list)
#     query_list2=qp.synonyms(query_list1)
#
#     if len(query_list2) > 0:
#         query_list=query_list+query_list2
#     else:
#         query_list=query_list+qp.autocorrection(query_list1)
#
#     qp.hypernyms(query_list1)
#     qp.hyponyms(query_list1)
#
#     result2=qp.searchInSolr(set(query_list+stopwordsList))
#
#
#     resultlist.append(result2)
#     for results in resultlist:
#         for result in results:
#             d=result['id']
#             if d not in matchingfiles:
#                 ind = file_list.index(d)
#                 final[d]="".join(data[ind])
#                 sent=qp.finding_matches(query_list,data[ind])
#                 print(d, "".join(data[ind][sent]), sep="\n")
#                 print("\n\n")
#                 matchingfiles.append(d)

# qp=queryProcessing()
# print(qp.starting("bubblers"))
