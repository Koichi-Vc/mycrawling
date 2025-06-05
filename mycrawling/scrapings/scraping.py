from collections import deque
import bs4
import logging
import pandas
from statistics import median
import time
import tracemalloc
from mycrawling.logs.debug_log import debug_logger

#Var37.06.14.15a(24/07/25/時点のバージョン)

class PageScraping():

    def __init__(self, df=None, text_parse_method=None):
        self.company_overview = None
        self.col_median_list = deque()
        self.df = df if df else list()
        self.text_parse_method = text_parse_method
        
    
    def column_count(self, company_overview):
        '''各項目の列数をカウントし、中央値を算出する。改行の基準を中央値にする。'''
        num_column = []
        #tag_name = None
        tag_elements = []
        for elem in company_overview:
            debug_logger.debug(f'elem: {elem} | elem length : {len(elem)} | elem.text: {elem.text}')

            if elem.name in ['table','tbody','th','tr']:
                #isinstance(i, bs4.element.Tag)を追加して事前にコメントアウトに対してattributeエラーが起きない様にした。
                tag_elements = (elm.find_all(['th', 'td']) for elm in elem.find_all('tr') if isinstance(elm, bs4.element.Tag))
                #tag_name = 'table'

            elif elem.name == 'dl' or elem.find_all('dl') or elem.find_all(['dt','dd']):
                #tag_name = 'dl'
                debug_logger.debug(f'dl要素あり')
                dt,dd = elem.find_all('dt'),elem.find_all('dd')
                
                for dt_i,dd_i in zip(dt, dd):
                    t, d = '',''
                    if isinstance(dt_i, bs4.element.Tag):
                        t = dt_i.text.strip().split('\n')
                    if isinstance(dd_i, bs4.element.Tag):
                        d = dd_i.text.strip().split('\n')
                    #t_d = []
                    t_d = [i for i in [t, d] if i != '']
                    debug_logger.debug(f't_d: {t_d}')
                    if t_d:
                        num_column.append(len(t_d))
                    else:
                        num_column.append(0)        
            else:
                tag_elements = (content for content in elem.contents if isinstance(content, bs4.element.Tag) or content.strip() != '')
            if not num_column:
                num_column = [len(i) for i in tag_elements][1:]
            
            if num_column:
                self.col_median_list.append(int(median(num_column)))
            else:
                self.col_median_list.append(1)
        #return num_column
     
    
    def table_element_scrape(self, element, col_median, company_list, index, text_line_blake):
        '''table要素の場合のスクレイピング関数'''

        tr_elements = []
        #elems_index = element
        if element.name == 'table' or element.find_all('tr'):
            tr_elements = (i for i in element.find_all('tr') if isinstance(i, bs4.element.Tag))
        elif element.name == 'tr':
            tr_elements = element
        debug_logger.debug(f'element: {element} | tr_elements: {tr_elements}')

        td_tag_gen = (i.find_all(['th','td']) for i in tr_elements if isinstance(i, bs4.element.Tag))
        td_list = []

        for td_item in td_tag_gen:
            li = []
            for td_elem in td_item:
                td_txt = td_elem.text.strip()
                if td_txt != '':
                    if '\n' not in td_txt:
                        li.append(td_txt)
                    else:
                        for i in td_txt.strip().split('\n'):
                            li.append(i)
                    td_a = td_elem.find_all('a')#aタグを検索
                    if td_a:
                        for a in td_a:#aタグが存在すれば、追加
                            li.append(a)
            if li:
                td_list.append(li)
                li = []
        debug_logger.debug(f'td_list: {td_list}')

        tr_txt = td_list.copy()
        for tr in tr_txt:
            if len(tr) <= col_median:
                index.append(tr[0])
                company_list.append(tr[1:])    
            else:
                tag_name = 'table'
                text_line_blake(tr, tag_name, index, row_head=tr[0])


    def dl_element_scrape(self, element, col_median, company_list, index, text_line_blake):
        '''element_scrape()関数が長すぎる為dl要素のelement_scrape()をこちらへ分ける'''
        elem_index = element
        
        element_dt = element.find_all('dt')
        element_dd = element.find_all('dd')
        for dt, dd in zip(element_dt, element_dd):
            dt_txt = dt.text.strip().replace('\n',' ')
            if dd.find_all(name=['ul','ol','dl']):
                uli = []
                index_item =[]
                ul = dd.find_all(['ul','ol','dl'])
                for ui in ul:#roop1
                    li = ui.text.strip().split('\n')
                    uli.append(li)
                    index_item.append(dt_txt)
                #roop1で収集したテキストリストを順番に代入

                for i, u in zip(index_item, uli):
                    index.append(i)
                    company_list.append(u)
            else:
                txt = dd.text.strip().split('\n')
                txt = [i.strip() for i in txt]
                if len(txt) <= col_median:
                    company_list.append(txt)
                    index.append(dt_txt)
                else:
                    tag_name = 'dl'
                    text_line_blake(txt, tag_name, index, row_head=dt_txt)

    def comment_scrape(self, element, col_median, company_list, index, text_line_blake):
        '''コメントアウトのスクレイピング '''
        comment = []
        head = 'コメントアウト'
        text = element.find_all(text= lambda text: isinstance(text, bs4.Comment))
        comment = [txt for item in text for txt in item.strip().split('\n') if txt.strip() != '']
        if comment.count('') != len(comment):
            if len(comment) <= col_median:
                company_list.append(comment)
                index.append(head)
            else:
                text_line_blake(comment,'', index, row_head='')

    def other_elements_scrape(self, element, col_median, company_list, index, reference_score_texts, transpose=False):
        ''' text_key_listが問題なく動作していたら、 reference_score_textsは撤去する。24/03/05/216am '''
        #text_key_list = element[1]
        debug_logger.debug(f'element: {element}')
        if not col_median or col_median <= 1:
            col_median += 1
        child_elements = [child for child in element.contents if isinstance(child, (bs4.element.Tag, bs4.element.NavigableString, bs4.Comment))]
        #print(f'child_elements: {child_elements}')
        child_count = len(child_elements)#子要素の数をカウント
        debug_logger.debug(f'child_elements: {child_elements} | child_count: {child_count}')
        
        tx = []
        line_count = 0
        elem_index = ''
        debug_logger.debug(f'reference_score_texts : {reference_score_texts}')
        for i in range(child_count):
            child_text = (child.strip() for child in child_elements[i].text.strip().split('\n') if child.strip() != '')
            #print(f'child_text: {child_text}')
            #tx = []
            #line_count = 0
            #elem_index = ''#child_text毎のインデックスを参照する為の一時的な変数
            for elem in child_text:
                debug_logger.debug(f'child_text[elem] : {elem}')
                if elem in reference_score_texts:#【24/06/13/】any(reference in elem for reference in reference_score_texts)の導入可否を検討。
                    
                    if tx:#既にアイテムが収集されていた場合、今検出された項目の前の項目テキストに対応するアイテムの為保存処理に移る
                        company_list.append(tx)
                        tx = []
                        line_count = 0
                        if not elem_index:
                            index.append('')
                    elif not tx and elem_index:#収集アイテムが無く且つインデックスだけが検出されていた場合は、
                        company_list.append([''])
                    text_index = reference_score_texts.index(elem)
                    elem_index = reference_score_texts[text_index]
                    index.append(elem_index)
                    continue
                elif line_count<=col_median:
                    tx.append(elem)
                    line_count += 1
                
                if line_count >= col_median:
                    company_list.append(tx)
                    tx = []
                    line_count = 0
                    if not elem_index:
                        index.append('')
                    elem_index = ''
            
            debug_logger.debug(f'forループ終了後 tx: {tx}')
        debug_logger.debug(f'ifの手前, company_list: {company_list} | ')
        debug_logger.debug(f'index: {index} | elem_index: {elem_index} | company_list length: {len(company_list)} | index length : {len(index)}')
        
        if tx:
            company_list.append(tx)
            if not elem_index:
                index.append('')      
        elif elem_index and not tx:
            debug_logger.debug(f'elif-True. elem_index: {elem_index} | tx: {tx}')
            tx.append('')
            company_list.append(tx)
        debug_logger.debug(f'ifの後, company_list: {company_list}')
        if transpose:
            debug_logger.debug('転置実行')
            company_list = list(zip(*company_list))

            
    def element_scrape(self, company_overview, reference_score_texts:list):
        """対象ページをスクレイピングする。"""
        debug_logger.debug(f'reference_score_texts: {reference_score_texts}')
        
        if isinstance(company_overview, str) or isinstance(company_overview, bs4.element.Tag):
            raise TypeError('オブジェクトをリスト、タプル、deque等に格納して渡してください')

        def text_line_blake(text, tag_name, index, row_head=''):
            ''' データが長い場合はcol_median値を基準に改行する。'''
            counta = 1
            tx = []
            for key, txt in enumerate(text):
                if (tag_name == 'table' and counta <= col_median and txt != '' and key != 0) or (tag_name != 'table' and counta <= col_median and txt != '' and txt != row_head):
                    tx.append(txt)
                    counta += 1
                elif (tag_name == 'table' and tx and counta >= col_median) or (tag_name != 'table' and tx and counta >= col_median):
                    index.append(row_head)
                    company_list.append(tx)
                    tx = []
                    counta =1
                    if txt != '' or (tag_name=='table' and key != 0 and txt != row_head):
                        tx.append(txt)
            if tx:
                index.append(row_head)
                company_list.append(tx)
                tx = []
        ''' text_line_blake ここまで '''

        self.column_count(company_overview)
        
        debug_logger.debug(f'col_median_list: {self.col_median_list}')
        col_median = 2
        st = time.time()
        for com_element in company_overview:
            company_list = []
            col_name = None
            index = []#pandas.DataFrameのRowネームリスト
            col_median = self.col_median_list.popleft()
            if not col_median:
                logging.warning(f'No Column. カラムが無い。elements : {com_element}')
                col_median = 2
            if com_element.name in ['table','tbody','th','tr'] or com_element.find_all(['table','tbody','tr','td','td']):
                debug_logger.debug(f'table_element_scrape実行')
                logging.info(f'table_element_scrape()実行')
                self.table_element_scrape(com_element, col_median, company_list, index, text_line_blake)
                #logging.info(f'table_element_scrape()実行完了; time: {time.time() - st}')

            #elif com_element.name == 'dl' or com_element.find_all('dl') or com_element.find_all(['dt','dd']):
            elif com_element.has_attr('class') and com_element.attrs['class'] == 'overview_dl_elements':
                #class属性が存在且つ、属性値がoverview_dl_elementsだった場合
                debug_logger.debug(f'dl_element_scrape()実行')
                logging.info(f'dl_element_scrape()実行')
                self.dl_element_scrape(com_element, col_median, company_list, index, text_line_blake)
                #logging.info(f'dl_element_scrape()実行完了; time: {time.time() - st}')
                
            elif com_element.name in ['ul','ol'] or len(com_element.find_all(['ul','ol'])) / len(com_element.contents) *100 >= 70:
                ''' ul, ol要素だった場合の処理 '''
                logging.info(f'other_elements_scrape()実行')
                #self.other_elements_scrape(com_element, col_median, company_list, index, text_line_blake)
                self.other_elements_scrape(com_element, col_median, company_list, index, reference_score_texts)
                #col_name = True
            else:
                logging.info(f'other_elements_scrape()実行')
                debug_logger.debug(f'other_elements_scrape()の実行')
                self.other_elements_scrape(com_element, col_median, company_list, index, reference_score_texts)

            if com_element.find_all(text= lambda text: isinstance(text, bs4.Comment)):
                #コメントアウトはここでスクレイピングする。
                debug_logger.debug(f'comment_scrape()実行')
                logging.info(f'comment_scrape()実行')
                self.comment_scrape(com_element, col_median, company_list, index, text_line_blake)
                #logging.info(f'comment_scrape()実行完了; time: {time.time() - st}')

            if not list(map(bool, company_list)):
                logging.warning(f'Scrapinged No Item. スクレイピングしたがアイテムを確認できない。')#ロガー
                return self.df
            
            if index:
                debug_logger.debug(f'len(index):{len(index)} | len(company_list) : {len(company_list)}')
                if col_name:
                    debug_logger.debug(f'col_name: True')
                    self.df.append(pandas.DataFrame(company_list))
                else:
                    self.df.append(pandas.DataFrame(company_list,index=index))
            else:
                self.df.append(pandas.DataFrame(company_list))

        logging.info(f'Scraping完了; time: {time.time() - st}')
        current, peak = tracemalloc.get_traced_memory()
        debug_logger.debug(f'element_scrape()のメモリリソース: current: {current/10**6}MB; peak: {peak/10**6}MB;\n詳細値: current: {current}; peak: {peak}')      
        return self.df


