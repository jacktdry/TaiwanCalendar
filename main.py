#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣行政機關辦公日曆爬蟲系統主程式
整合爬蟲和轉換模組，提供統一的執行入口
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from crawler import TaiwanCalendarCrawler
from converter import CalendarConverter

# 設定日誌格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TaiwanCalendarSystem:
    """台灣行政機關辦公日曆系統主類別"""
    
    def __init__(self, origin_dir='origin', docs_dir='docs'):
        """
        初始化系統
        
        Args:
            origin_dir (str): 原始CSV檔案目錄
            docs_dir (str): 輸出JSON檔案目錄
        """
        self.origin_dir = origin_dir
        self.docs_dir = docs_dir
        self.crawler = TaiwanCalendarCrawler(origin_dir=origin_dir)
        self.converter = CalendarConverter(origin_dir=origin_dir, docs_dir=docs_dir)
        
        # 執行統計
        self.stats = {
            'execution_start_time': None,
            'execution_end_time': None,
            'crawl_success_count': 0,
            'crawl_total_count': 0,
            'convert_success_count': 0,
            'convert_total_count': 0,
            'errors': []
        }
    
    def check_environment(self) -> bool:
        """
        檢查執行環境
        
        Returns:
            bool: 環境檢查通過返回True，否則返回False
        """
        try:
            logger.info("正在檢查執行環境...")
            
            # 檢查必要的套件
            required_packages = {
                'requests': 'requests',
                'beautifulsoup4': 'bs4',
                'pandas': 'pandas', 
                'lxml': 'lxml'
            }
            missing_packages = []
            
            for package_name, import_name in required_packages.items():
                try:
                    __import__(import_name)
                except ImportError:
                    missing_packages.append(package_name)
            
            if missing_packages:
                logger.error(f"缺少必要套件: {', '.join(missing_packages)}")
                logger.error("請執行: pip install -r requirements.txt")
                return False
            
            # 檢查目錄權限
            try:
                os.makedirs(self.origin_dir, exist_ok=True)
                os.makedirs(self.docs_dir, exist_ok=True)
            except PermissionError:
                logger.error("沒有足夠權限創建目錄")
                return False
            
            # 檢查網路連線
            try:
                import requests
                response = requests.get('https://www.google.com', timeout=10)
                if response.status_code != 200:
                    logger.warning("網路連線可能不穩定")
            except Exception as e:
                logger.warning(f"網路連線檢查失敗: {e}")
            
            logger.info("執行環境檢查通過")
            return True
            
        except Exception as e:
            logger.error(f"環境檢查時發生錯誤: {e}")
            self.stats['errors'].append(f"環境檢查錯誤: {e}")
            return False
    
    def execute_crawling(self) -> bool:
        """
        執行爬蟲階段
        
        Returns:
            bool: 爬蟲執行成功返回True，否則返回False
        """
        try:
            logger.info("=" * 60)
            logger.info("開始執行爬蟲階段")
            logger.info("=" * 60)
            
            # 執行爬蟲
            success_count, total_count = self.crawler.crawl()
            
            # 更新統計資訊
            self.stats['crawl_success_count'] = success_count
            self.stats['crawl_total_count'] = total_count
            
            if success_count > 0:
                logger.info(f"爬蟲階段完成: 成功下載 {success_count}/{total_count} 個檔案")
                return True
            else:
                logger.error("爬蟲階段失敗: 沒有成功下載任何檔案")
                self.stats['errors'].append("爬蟲階段：沒有成功下載任何檔案")
                return False
                
        except Exception as e:
            logger.error(f"爬蟲階段發生錯誤: {e}")
            logger.error(f"錯誤詳情: {traceback.format_exc()}")
            self.stats['errors'].append(f"爬蟲階段錯誤: {e}")
            return False
    
    def execute_conversion(self) -> bool:
        """
        執行轉換階段
        
        Returns:
            bool: 轉換執行成功返回True，否則返回False
        """
        try:
            logger.info("=" * 60)
            logger.info("開始執行轉換階段")
            logger.info("=" * 60)
            
            # 執行轉換
            success_count, total_count = self.converter.convert_all()
            
            # 更新統計資訊
            self.stats['convert_success_count'] = success_count
            self.stats['convert_total_count'] = total_count
            
            if success_count > 0:
                logger.info(f"轉換階段完成: 成功轉換 {success_count}/{total_count} 個檔案")
                return True
            else:
                logger.error("轉換階段失敗: 沒有成功轉換任何檔案")
                self.stats['errors'].append("轉換階段：沒有成功轉換任何檔案")
                return False
                
        except Exception as e:
            logger.error(f"轉換階段發生錯誤: {e}")
            logger.error(f"錯誤詳情: {traceback.format_exc()}")
            self.stats['errors'].append(f"轉換階段錯誤: {e}")
            return False
    
    def generate_summary(self) -> dict:
        """
        生成執行摘要
        
        Returns:
            dict: 包含執行結果統計的字典
        """
        execution_time = 0
        if self.stats['execution_start_time'] and self.stats['execution_end_time']:
            execution_time = (self.stats['execution_end_time'] - self.stats['execution_start_time']).total_seconds()
        
        # 獲取檔案統計
        csv_files = []
        json_files = []
        
        if os.path.exists(self.origin_dir):
            csv_files = [f for f in os.listdir(self.origin_dir) if f.lower().endswith('.csv')]
        
        if os.path.exists(self.docs_dir):
            json_files = [f for f in os.listdir(self.docs_dir) if f.lower().endswith('.json')]
        
        summary = {
            'execution_time': round(execution_time, 2),
            'crawl_results': {
                'success': self.stats['crawl_success_count'],
                'total': self.stats['crawl_total_count'],
                'success_rate': round(self.stats['crawl_success_count'] / max(self.stats['crawl_total_count'], 1) * 100, 2)
            },
            'conversion_results': {
                'success': self.stats['convert_success_count'],
                'total': self.stats['convert_total_count'],
                'success_rate': round(self.stats['convert_success_count'] / max(self.stats['convert_total_count'], 1) * 100, 2)
            },
            'file_statistics': {
                'csv_files': len(csv_files),
                'json_files': len(json_files),
                'csv_file_list': csv_files,
                'json_file_list': json_files
            },
            'errors': self.stats['errors'],
            'overall_success': len(self.stats['errors']) == 0 and self.stats['crawl_success_count'] > 0 and self.stats['convert_success_count'] > 0
        }
        
        return summary
    
    def print_summary(self, summary: dict):
        """
        印出執行摘要
        
        Args:
            summary (dict): 執行摘要字典
        """
        logger.info("=" * 60)
        logger.info("執行摘要報告")
        logger.info("=" * 60)
        
        # 執行時間
        logger.info(f"總執行時間: {summary['execution_time']} 秒")
        
        # 爬蟲結果
        crawl = summary['crawl_results']
        logger.info(f"爬蟲結果: {crawl['success']}/{crawl['total']} 個檔案 (成功率: {crawl['success_rate']}%)")
        
        # 轉換結果
        convert = summary['conversion_results']
        logger.info(f"轉換結果: {convert['success']}/{convert['total']} 個檔案 (成功率: {convert['success_rate']}%)")
        
        # 檔案統計
        files = summary['file_statistics']
        logger.info(f"檔案統計: {files['csv_files']} 個CSV檔案, {files['json_files']} 個JSON檔案")
        
        # 錯誤資訊
        if summary['errors']:
            logger.error(f"發生 {len(summary['errors'])} 個錯誤:")
            for i, error in enumerate(summary['errors'], 1):
                logger.error(f"  {i}. {error}")
        
        # 整體結果
        if summary['overall_success']:
            logger.info("整體執行狀態: 成功 ✓")
        else:
            logger.error("整體執行狀態: 失敗 ✗")
        
        logger.info("=" * 60)
    
    def run(self) -> bool:
        """
        執行完整的爬蟲和轉換流程
        
        Returns:
            bool: 整體執行成功返回True，否則返回False
        """
        try:
            self.stats['execution_start_time'] = datetime.now()
            
            logger.info("台灣行政機關辦公日曆爬蟲系統啟動")
            logger.info(f"執行時間: {self.stats['execution_start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 1. 環境檢查
            if not self.check_environment():
                return False
            
            # 2. 執行爬蟲
            crawl_success = self.execute_crawling()
            
            # 3. 執行轉換（即使爬蟲部分失敗，也嘗試轉換現有檔案）
            convert_success = self.execute_conversion()
            
            # 記錄執行結果到日誌
            logger.info(f"爬蟲執行狀態: {'成功' if crawl_success else '失敗'}")
            logger.info(f"轉換執行狀態: {'成功' if convert_success else '失敗'}")
            
            # 4. 記錄結束時間
            self.stats['execution_end_time'] = datetime.now()
            
            # 5. 生成並顯示摘要
            summary = self.generate_summary()
            self.print_summary(summary)
            
            # 返回整體執行結果
            return summary['overall_success']
            
        except Exception as e:
            logger.error(f"系統執行時發生未預期的錯誤: {e}")
            logger.error(f"錯誤詳情: {traceback.format_exc()}")
            
            self.stats['execution_end_time'] = datetime.now()
            self.stats['errors'].append(f"系統錯誤: {e}")
            
            summary = self.generate_summary()
            self.print_summary(summary)
            
            return False


def main():
    """主函數"""
    try:
        # 創建系統實例並執行
        system = TaiwanCalendarSystem()
        success = system.run()
        
        # 設定退出碼
        exit_code = 0 if success else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("用戶中斷執行")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程式執行時發生致命錯誤: {e}")
        logger.error(f"錯誤詳情: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()