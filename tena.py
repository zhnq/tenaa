#coding:utf-8
import os
import time
import urllib.request
import ssl
from urllib.request import urlretrieve
from lxml import etree

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pandas import DataFrame
import pandas

def download(url, savepath='./'):
    """
    download file from internet
    :param url: path to download from
    :param savepath: path to save files
    :return: None
    """
    def reporthook(a, b, c):
        """
        显示下载进度
        :param a: 已经下载的数据块
        :param b: 数据块的大小
        :param c: 远程文件大小
        :return: None
        """
        print("\rdownloading: %5.1f%%" % (a * b * 100.0 / c), end="")
    filename = os.path.basename(url)
    # 判断文件夹是否存在
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    # 判断文件是否存在，如果不存在则下载
    if not os.path.isfile(os.path.join(savepath, filename)):
        print('Downloading data from %s' % url)
        urlretrieve(url, os.path.join(savepath, filename), reporthook=reporthook)
        print('\nDownload finished!')
    else:
        print('File already exsits!')
    # 获取文件大小
    filesize = os.path.getsize(os.path.join(savepath, filename))
    # 文件大小默认以Bytes计， 转换为Mb
    print('File size = %.2f Mb' % (filesize/1024/1024))

if __name__ =='__main__':    
    base_url = 'http://shouji.tenaa.com.cn/mobile/mobileindex.aspx'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver=webdriver.Chrome(options=chrome_options)

    driver.get(base_url)
    # 在 选机中心 位置单击
    driver.find_element_by_id("chkSSNF_2").click()
    driver.find_element_by_xpath('//*[@id="Table3"]/tbody/tr[5]/td[2]/img').click()
    time.sleep(1)
    root_src = driver.page_source
    root_response = BeautifulSoup(root_src,'lxml')
    # 获取页数
    Now_page = int(root_response.find("span",id = "nowPage").string[2])
    All_page = int(root_response.find("span",id = "allPage").string[2:4])
    print('共有'+str(All_page)+'页...')
    data = pandas.DataFrame()
    # 跳转到页
    inputElement = driver.find_element_by_id('getPage') #获取输入框
    searchButton = driver.find_element_by_xpath('//*[@id="Table15"]/tbody/tr/td[3]/table/tbody/tr[2]/td/img') #获取搜索按钮
    inputElement.send_keys("33") #输入框输入"Python"
    searchButton.click() #搜索
    time.sleep(1)
    for page in range(All_page):
        # 获取所有手机详情页链接：20个
        elms=driver.find_elements_by_xpath('//div[@id="showMobile"]//td[@width="152"]//td[@align="center"]//a')
        print('正在进入第'+str(page)+'页...')
        for elm in elms:
            value = elm.get_attribute("href")
            inner_driver=webdriver.Chrome(options=chrome_options)
            inner_driver.get(value)
            html = inner_driver.page_source
            response = BeautifulSoup(html,'lxml')

            # 参数标签      
            
            brands = response.find(id='lblPP').string
            model = response.find(id='lblXH').string
            number = response.find(id='txtSLBH')['value']
            phone_size = response.find(text="机身尺寸").next_element.string
            phone_color = response.find(text="可选颜色").next_element.string
            weight = response.find(text="重量").next_element.string
            sc_params = response.find(text = "外屏参数").next_element.string
            network = response.find(text = "手机制式").next_element.string
            batt = response.find(text = "电池额定容量").next_element.string
            cpuhz = response.find(text="CPU主频").next_element.string
            ram = response.find(text="RAM内存容量").next_element.string
            rom = response.find(text="手机内存").next_element.string
            cpu_cnt = response.find(text="CPU内核数").next_element.string
            print('正在爬取：'+brands + model)
            # 写入dataframe 
            a = ({"brands":brands,"model":model,'number':number,'phone_size':phone_size,'phone_color':phone_color,
                  'weight':weight,'sc_params':sc_params,'network':network,'batt':batt,'cpuhz':cpuhz,'ram':ram,'ram':ram,'rom':rom,'cpu_cnt':cpu_cnt})
            data = data.append(a,ignore_index=True)
            data.to_csv("phone_dataset_2017",encoding = "utf_8_sig")
            print(brands+model+'写入csv成功！')
            # 获取图片链接
            pic_url = response.find(id="tblPic").find_all('img')
            savepath = 'E:\\phone_data\\2017\\'+ brands +'\\'+ model +'\\'
            for i in pic_url:
                # time.sleep(2)
                idl = i.get('src')
                url="http://shouji.tenaa.com.cn"+idl.lstrip('..')
                download(url,savepath)
            inner_driver.close()
            time.sleep(1)
        driver.find_element_by_xpath('//*[@id="Table15"]/tbody/tr/td[5]/table/tbody/tr[2]/td/img').click()
        time.sleep(1)
        df2 = pandas.read_csv("phone_dataset_2017" , encoding = "utf_8_sig")    
        print (df2)
    

