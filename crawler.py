#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣行政機關辦公日曆爬蟲模組
從政府開放資料平台爬取CSV格式的日曆資料
"""

import os
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import logging
import urllib3

# 設定日誌格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TaiwanCalendarCrawler:
    """台灣行政機關辦公日曆爬蟲類別"""
    
    def __init__(self, target_url='https://data.gov.tw/dataset/14718', origin_dir='origin'):
        """
        初始化爬蟲
        
        Args:
            target_url (str): 目標網站URL
            origin_dir (str): 原始檔案存放目錄
        """
        self.target_url = target_url
        self.origin_dir = origin_dir
        self.session = requests.Session()
        
        # 設定請求標頭，模擬瀏覽器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 處理SSL憑證問題
        self.session.verify = False
        
        # 確保目錄存在
        os.makedirs(self.origin_dir, exist_ok=True)
    
    def fetch_page_content(self, url, max_retries=3):
        """
        獲取網頁內容
        
        Args:
            url (str): 目標URL
            max_retries (int): 最大重試次數
            
        Returns:
            str: 網頁HTML內容，失敗時返回None
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"正在獲取網頁內容: {url} (嘗試 {attempt + 1}/{max_retries})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                response.encoding = 'utf-8'
                logger.info("網頁內容獲取成功")
                return response.text
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"網頁請求失敗 (嘗試 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # 等待2秒後重試
                else:
                    logger.error(f"網頁請求最終失敗: {e}")
                    return None
    
    def parse_resource_items(self, html_content):
        """
        解析網頁中的資源項目
        
        Args:
            html_content (str): 網頁HTML內容
            
        Returns:
            list: 包含(連結, 檔名)元組的列表
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            resource_items = []
            
            # 尋找class="resource-item"的li元素
            li_elements = soup.find_all('li', class_='resource-item')
            logger.info(f"找到 {len(li_elements)} 個resource-item")
            
            for li in li_elements:
                try:
                    # 提取<a>連結
                    a_tag = li.find('a')
                    
                    if a_tag and a_tag.get('href'):
                        link = a_tag.get('href')
                        
                        # 尋找不在button中的span元素來獲取檔案名稱
                        filename = None
                        
                        # 找到所有span元素，排除在button中的span
                        all_spans = li.find_all('span')
                        for span in all_spans:
                            # 檢查這個span是否在button中
                            parent_button = span.find_parent('button')
                            if not parent_button:
                                span_text = span.get_text(strip=True)
                                if span_text and span_text != 'CSV':  # 避免取到通用的"CSV"文字
                                    filename = span_text
                                    break
                        
                        # 如果還是沒找到合適的檔名，嘗試從URL參數中提取
                        if not filename:
                            from urllib.parse import urlparse, parse_qs
                            parsed_url = urlparse(link)
                            query_params = parse_qs(parsed_url.query)
                            if 'name' in query_params:
                                filename = query_params['name'][0]
                            else:
                                filename = f"calendar_{len(resource_items)+1}"
                        
                        # 過濾條件：排除包含"Google"的項目
                        if 'Google' not in filename:
                            # 確保連結是完整的URL
                            if not link.startswith('http'):
                                link = urljoin(self.target_url, link)
                            
                            resource_items.append((link, filename))
                            logger.info(f"找到有效資源: {filename}")
                        else:
                            logger.info(f"已過濾Google相關資源: {filename}")
                            
                except Exception as e:
                    logger.warning(f"解析資源項目時發生錯誤: {e}")
                    continue
            
            logger.info(f"總共找到 {len(resource_items)} 個有效資源")
            return resource_items
            
        except Exception as e:
            logger.error(f"解析HTML內容時發生錯誤: {e}")
            return []
    
    def download_file(self, url, filename, max_retries=3):
        """
        下載檔案
        
        Args:
            url (str): 檔案URL
            filename (str): 檔案名稱
            max_retries (int): 最大重試次數
            
        Returns:
            bool: 下載成功返回True，失敗返回False
        """
        # 清理檔名，移除不合法字元
        safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        if not safe_filename.endswith('.csv'):
            safe_filename += '.csv'
        
        file_path = os.path.join(self.origin_dir, safe_filename)
        
        # 如果檔案已存在，先檢查是否需要重新下載
        if os.path.exists(file_path):
            logger.info(f"檔案已存在: {safe_filename}")
            return True
        
        for attempt in range(max_retries):
            try:
                logger.info(f"正在下載檔案: {safe_filename} (嘗試 {attempt + 1}/{max_retries})")
                response = self.session.get(url, timeout=60, stream=True)
                response.raise_for_status()
                
                # 檢查內容類型
                content_type = response.headers.get('content-type', '').lower()
                if 'text/csv' not in content_type and 'application/csv' not in content_type:
                    logger.warning(f"檔案內容類型可能不是CSV: {content_type}")
                
                # 寫入檔案
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # 檢查檔案大小
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    os.remove(file_path)
                    raise Exception("下載的檔案為空")
                
                logger.info(f"檔案下載成功: {safe_filename} ({file_size} bytes)")
                return True
                
            except Exception as e:
                logger.warning(f"檔案下載失敗 (嘗試 {attempt + 1}/{max_retries}): {e}")
                if os.path.exists(file_path):
                    os.remove(file_path)  # 清理不完整的檔案
                
                if attempt < max_retries - 1:
                    time.sleep(3)  # 等待3秒後重試
                else:
                    logger.error(f"檔案下載最終失敗: {safe_filename}")
                    return False
    
    def crawl(self):
        """
        執行爬蟲主流程
        
        Returns:
            tuple: (成功下載檔案數, 總檔案數)
        """
        logger.info("開始執行台灣行政機關辦公日曆爬蟲")
        
        # 1. 獲取網頁內容
        html_content = self.fetch_page_content(self.target_url)
        if not html_content:
            logger.error("無法獲取網頁內容，爬蟲終止")
            return 0, 0
        
        # 2. 解析資源項目
        resource_items = self.parse_resource_items(html_content)
        if not resource_items:
            logger.error("未找到任何有效資源，爬蟲終止")
            return 0, 0
        
        # 3. 下載檔案
        success_count = 0
        total_count = len(resource_items)
        
        for i, (link, filename) in enumerate(resource_items, 1):
            logger.info(f"處理檔案 {i}/{total_count}: {filename}")
            if self.download_file(link, filename):
                success_count += 1
            
            # 避免請求過於頻繁
            if i < total_count:
                time.sleep(1)
        
        logger.info(f"爬蟲執行完成: 成功下載 {success_count}/{total_count} 個檔案")
        return success_count, total_count


def main():
    """主函數，用於測試爬蟲功能"""
    crawler = TaiwanCalendarCrawler()
    success_count, total_count = crawler.crawl()
    
    if success_count > 0:
        print(f"爬蟲執行成功: {success_count}/{total_count} 個檔案下載完成")
    else:
        print("爬蟲執行失敗，沒有成功下載任何檔案")


if __name__ == "__main__":
    main()