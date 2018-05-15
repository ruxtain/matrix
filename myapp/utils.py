# for special functions
# 记得反转实义字符 以压缩字符数

import re
import numpy
import htmlmin 
from bs4 import BeautifulSoup
import collections

# test = '''<b href="watashi" style="font-size:12px;">Easy Setup</b><br>Simply connect the camera to'''

def codeGenerator(htmlCode):
    
    def _remove_attrs(soup):
        for tag in soup.findAll(True): 
            tag.attrs = None
        return soup

    replaceDict = collections.OrderedDict()
    replaceDict[r'<p><br></p>'] = '<br>'
    replaceDict[r'<p>'] = ''
    replaceDict[r'</p>'] = '<br>'
    #这个有点复杂，我详细说一说。括号让&nbsp;可以作为整体重复出现，视为一个字符来匹配
    # \s表示&nbsp;可以在和末尾的tag之间有空白字符。 (?=...) 表示后面必须是符合...的，
    # c才会匹配前面的内容。 </[\w\s]+> 的例子： </p> </a >    
    replaceDict[r'(&nbsp;)+\s*(?=</[\w\s]+>)'] = '' 
    replaceDict[r'<strong\s*?>'] = '<b>'
    replaceDict[r'</strong\s*?>'] = '</b>'
    replaceDict[r'<em\s*?>'] = '<i>'
    replaceDict[r'</em\s*?>'] = '</i>'
    replaceDict[r'&nbsp;'] = ' ' # 李丹之问题
    replaceDict[r'&amp;'] = '&'
    replaceDict[r'&lt;'] = '<'
    replaceDict[r'&gt;'] = '>'    
    replaceDict[r'<br[\s/]+?>'] = ''
    replaceDict[r'<span>'] = ''
    replaceDict[r'</span>'] = ''

    soup = BeautifulSoup(htmlCode, 'html.parser')
    htmlCode = str(_remove_attrs(soup))

    for regex in replaceDict:
        htmlCode = re.sub(regex, replaceDict[regex], htmlCode)

    htmlCode = re.sub(r'^(<br\s*?>\s*)+', '', htmlCode)
    htmlCode = re.sub(r'(<br\s*?>\s*)+$', '', htmlCode)

    return htmlmin.minify(htmlCode.strip())


# 以下三个函数专用于分行
# 前端已经去重和转小写了。
def get_length(words):
    return len(' '.join(words))

def incise(words, standard): # 根据一个标准长度来切割单词列表里的单词
    results = []
    line = []
    i = 0
    while True: # 一定要小心死循环
        try:
            word = words[i]
        except IndexError:
            return results
        line.append(word)
        i+=1
        if get_length(line) > standard: # 只有当添加单词到这一行的长度超过标准长度后，再来探究
            longer_line = line[:] # [:]切片以免会误改line
            shorter_line = line[:-1] # 去掉最后一个单词的版本，叫shorter
            if i >= len(words): # 最后一个单词，不区分是longer还是shorter，一律加入result
                results.append(line[:])
            else:
                if standard - get_length(shorter_line) > get_length(longer_line) - standard: # 短的误差更大，选择长的
                    # print('采用了长的', longer_line[:])
                    results.append(longer_line[:]) # 只采纳line的变切片，貌似不能随便创建新的实例
                else: 
                    # print('采用了短的', shorter_line[:])
                    results.append(shorter_line[:])
                    if shorter_line[:]: # 短的不为空才行，否则会死循环
                        i-=1 # 可以理解成指向单词的指针往回退了一格，因为现在采用是短的
            line.clear() # 一行放入results后，就要清空这个变量 line= [] 并不能清空列表，必须 clear
        else: # 当前行压根儿就没有超过标准长度，所以直接忽略。但是，如果恰好是最后一行文字，那永远也超不多，只需要判断i超出总单词数就行
            if i >= len(words): # 都循环完了，却没有超过standard，那么剩下的全部构成一行
                results.append(line[:])

def divide_into_5_parts(raw):
    ultimate = {}
    for standard in range(10, 2000):
        results = incise(raw.split(), standard)
        if len(results) == 5:
            line_lengths = []
            for line in results:
                print(line)
                real_line = ' '.join(line)
                line_lengths.append(len(real_line))
            variance = numpy.var(line_lengths)
            ultimate[variance] = results
    if len(ultimate) == 0:
        return "Tip: Please add a few keywords."
    try:
        the_one = ultimate[min(ultimate)]
    except ValueError: # 单词数量太少
        return 'Unknown Error. Please try again.'
    finale = ''
    for line in the_one:
        finale += ' '.join(line) + '\n'
    return finale

if __name__ == '__main__':
    print(codeGenerator(test))
    raw = 'as the largest ecommerce site and de facto this is awesome product search engine amazon an important place to optimize content however be most valuable drive traffic on your products in article ill list tools results price free you can monthly average searches us purchase kit their homes blended'
    raw = 'those mother fucker who tried to rip off my wifi should fucking die these disgusting wank all the freaking time they know nothing about morality this girl sometimes thinks she is good but in fact tremendous things can be done improve her do happy everytime world shenzhen better than hongkong china'
    raw = 'nginx plus offers even more features for tcp load balancing these advanced offered in can be found throughout part i of this book available such as connection limiting, later chap‐ ter. health checks all will covered chapter dynamic reconfiguration upstream pools a feature is good non done'
    print(divide_into_5_parts(raw))