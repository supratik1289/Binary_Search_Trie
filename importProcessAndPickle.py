import warnings
warnings.simplefilter(action='ignore', category=DeprecationWarning)
import pandas as p
import time
import pickle
from unidecode import unidecode

#opening and reading all the data from the corpus

a = time.time()
df = p.read_excel("wiki_movie_plots_deduped.xlsx") #using excel format for better reading without errors
df = df.drop(columns=["Release Year","Origin/Ethnicity","Director","Cast","Genre"]) #drops unimportant fields


#storing essential data
title = df["Title"]
plot = df["Plot"]
link = df["Wiki Page"]

l = time.time()
b = time.time()
print("Total reading to data frame time: ",b-a) #measuring time taken for performance judging purposes

#pickling the unedited data to get back original results during search
a = time.time()

with open("dataframe","wb") as f:
    pickle.dump((title,plot,link),f)

b = time.time()
print("Time required to pickle the dataframe: ",b-a)

#preprocessing the data (removing special characters and numbers)

NDOC = len(title)
print("Number of documents to be processed:",NDOC)

#preprocess function removes every special symbol from the list

symbols = ['`','~','!','@','#','$','%','^','&','*','(',')','_','-','+','=','{','[','}','}','|',':',';','"',"'",'<',',','>','.','?','/',']','\n','\0','1','2','3','4','5','6','7','8','9','0']

def preprocess(x):
    y = ''
    x_iter = iter(x) 
    for a in x_iter:
        if (a not in symbols): 
            y = y+unidecode(a.lower())
    return y

a = time.time()

#preprocessing title and plot for search engine building
for i in range(len(title)):
    title[i] = preprocess(str(title[i]))

for i in range(len(plot)):
    plot[i] = preprocess(str(plot[i]))

b = time.time()
print("Total Pre-processing time: ",b-a)

#trie structure part

#trie structure definition

class Node:
    def __init__(self, postings): #node initialization function 
        #each node has a postings list for a word ending this node and a children list with link to next 26 letters
        self.postings = []
        self.children = [None for a in range(27)]
    def insert(self,word,docid): #insert function inserts a word and the corresponding docid recursively
        a = list(word) #takes the word and split into letters
        if a!=[]: #if not empty then go to the node corresponding to the first letter in the array or create one if it doesn't exist
            if self.children[ord(a[0])-97] == None:
                self.children[ord(a[0])-97] = Node([])
                s = a.pop(0) #after going to the node remove the letter from list and call the function again with the smaller word
                self.children[ord(s)-97].insert("".join(a),docid) 
            else:
                #print(ord(a[0])-97)
                s = a.pop(0)
                self.children[ord(s)-97].insert("".join(a),docid)
        else: #if empty it means end of word is reached then simply append the postings list if the docid is not present previously
            if self.postings == []:
                self.postings.append(docid)
            elif docid != self.postings[len(self.postings)-1]:
                self.postings.append(docid)
    def search(self,word): #search function searches a word and retrieves the postings  
        """
        if self.children == ['' for a in range(27)]:
            return ['Result Not Found']
        else:
        """
        a = list(word) #breaks the word into letters and finds the postings recursively
        if a == []: #if a is empty it means we have reached the destination node and we return the postings
            return self.postings
        else:
            if self.children[ord(a[0])-97] != None: #otherwise we go to the next node if it exists and call the function on the next node
                s = a.pop(0)
                return self.children[ord(s)-97].search("".join(a))
            else:
                return ['Result Not Found'] #if the next node doesn't existm it means the word doesn't exist in the trie and we return

#trie initialization

head = Node([])
head1 = Node([])
head2 = Node([])
#forming the tries for different search engines

s = time.time()

for i in range(NDOC):
    x = title[i].split(" ")
    y = plot[i].split(" ")
    if i%500==0:
        print(i,"documents processed")
    for a in x:
        try:
            head.insert(a,i)
            head1.insert(a,i)
        except:
            continue
    for a in y:
        try:
            head.insert(a,i)
            head2.insert(a,i)
        except:
            continue
"""
for i in range(NDOC):
    x = plot[i].split(" ")
    if i%500==0:
        print(i,"documents processed")
    for a in x:
        try:
            head.insert(a,i)
            head2.insert(a,i)
        except:
            continue
"""
b = time.time()

print("Trie formation time:",b-s)

#converting the trie into a convenient structure to store it
def pickle_tree(node):
    if node is None:
        return None
    return (node, [pickle_tree(child) for child in node.children])

a = time.time()
#pickling the trees to a file
pickeled_tree = pickle_tree(head)
with open("moviedata", "wb") as f:
    pickle.dump(pickeled_tree, f)

pickeled_tree = pickle_tree(head1)
with open("moviedata_title", "wb") as f:
    pickle.dump(pickeled_tree, f)

pickeled_tree = pickle_tree(head2)
with open("moviedata_plot", "wb") as f:
    pickle.dump(pickeled_tree, f)

b = time.time()
print("Trie Pickling time:",b-a)

print("Total time taken:",time.time()-l)