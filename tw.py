from pymystem3 import Mystem
import codecs
from collections import Counter
import re
import xlwt



fileObj = codecs.open("text1.txt", "r", "utf_8_sig")
text = fileObj.read() # или читайте по строке
# print(text[0:150])
fileObj.close()
fileObj1 = codecs.open("text3.txt", "r", "utf_8_sig")
stop_words = fileObj1.read() # или читайте по строке
# print(text[0:150])
fileObj1.close()

# print(stop_words)
m = Mystem()
my_new_string = re.sub('([^\w\s])|(\d)|(\n)(\s){1,9}', ' ', text)
my_new_string = re.sub('([\t\r\n\v\f])', ' ', my_new_string)
my_new_string = re.sub('(\s){2,}', ' ', my_new_string)
# print(my_new_string)
lemmas = m.lemmatize(my_new_string)
# print(''.join(lemmas))

print(lemmas)

array =[]
for l in lemmas:
    if l.lower() not in stop_words:
        array.append(l)
        # print('___', l)
clear_array = []
for i in array:
    if i is not ' ':
        print(i)
        clear_array.append(i)
c = Counter(clear_array)

bigram_freq = {}
length = len(clear_array)
for i in range(length-1):
    bigram = (clear_array[i], clear_array[i+1])
    if bigram not in bigram_freq:
        bigram_freq[bigram] = 0
    bigram_freq[bigram] += 1
d = Counter(bigram_freq)
print(d)
for i in d:
    print(i , ' ', d[i])
for i in c:
    print(i , ' ', c[i])


