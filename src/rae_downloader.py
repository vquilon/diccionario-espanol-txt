#!/usr/bin/env python3

# Desarrollado por Jorge Dueñas Lerín
import sys
from urllib.parse import quote
from urllib.request import Request, urlopen
from lxml import etree
import time


UA="Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
url_list="https://dle.rae.es/{}?m=31"
url_detail="https://dle.rae.es/{}"

to_remove_from_title='Ir a la entrada '
"""
Usamos title por que el contenido en determinadas situaciones cambia:
<a data-cat="FETCH" data-acc="LISTA EMPIEZA POR" data-eti="abollado" title="Ir a la entrada abollado, abollada" href="/abollado">abollado<sup>1</sup>, da</a>
"""
skip = len(to_remove_from_title)

letras = ['a', 'á', 'b', 'c', 'd', 'e', 'é', 'f', 'g', 'h', 'i', 'í', 'j', 'k', 'l', 'm',
             'n', 'ñ', 'o', 'ó', 'p', 'q', 'r', 's', 't', 'u', 'ú', 'ü', 'v', 'w', 'x', 'y', 'z']

#Para comprobar la necesidad de title
#letras = ['abonado']

def main():
    start_withs = letras.copy()

    def get_xtree(url, param):
        tree = None
        attemps = 5
        while attemps > 0 and tree == None:
            try:
                req = Request(url.format(quote(param)), headers={'User-Agent': UA})
                print(req.full_url)
                print(start_withs)
                webpage = urlopen(req)
                htmlparser = etree.HTMLParser()
                tree = etree.parse(webpage, htmlparser)
            except Exception as e:
                attemps -= 1
                print(str(e), file=sys.stderr)
                time.sleep(0.5)

        return tree

    with open("palabras_todas.txt", "w") as ftodas:
        while len(start_withs) != 0:
            palabra_start_with = start_withs.pop(0)

            if(palabra_start_with in ['app', 'docs', 'js']):
                continue

            print(palabra_start_with)
            tree = get_xtree(url_list, palabra_start_with)
            res = tree.xpath('//*[@id="resultados"]/*/div[@class="n1"]/a/@title')

            conj_raw_list = []
            # Se repiten palabras. Cuando por ejemplo aba tiene más de 30 y se exapande
            # abaa, abab, etc... las primeras palabras no aparecen: aba
            for pal in res:
                pal_clean = pal[skip:]
                pal_clean = pal_clean.split(", ")
                for p in pal_clean:
                    # print(p)
                    ftodas.write(p+'\n')
                    # Try conjugación
                    tree = get_xtree(url_detail, p)

                    contains_conjug = tree.xpath('//*[@id="resultados"]/*/a[@class="e2"]/@title')
                    if len(contains_conjug) > 0:
                        # print("^" * 80)
                        # print(contains_conjug)
                        # get all contant in tds
                        # conj_raw_list.append()
                        conjug = tree.xpath('//div[@id="conjugacion"]//td//text()')
                        conjug_clean = ' '.join(conjug).replace(', ', ' ').replace(' / ', ' ').split(' ')
                        for conj in conjug_clean:
                            if(conj!=''):
                                # print(conj)
                                ftodas.write(conj+'\n')

            if(len(res)>30):
                print("!" * 80)
                print("EXAPEND: " + palabra_start_with)
                expand = [palabra_start_with + l for l in letras]
                start_withs = expand + start_withs


if __name__ == '__main__':
    main()
