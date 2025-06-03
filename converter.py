#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台灣行政機關辦公日曆資料轉換模組
將CSV格式的日曆資料轉換為JSON格式
"""

import os
import json
import pandas as pd
import logging
import re
from datetime import datetime
from typing import List, Dict, Any

# 設定日誌格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CalendarConverter:
    """日曆資料轉換器類別"""
    
    def __init__(self, origin_dir='origin', docs_dir='docs'):
        """
        初始化轉換器
        
        Args:
            origin_dir (str): 原始CSV檔案目錄
            docs_dir (str): 輸出JSON檔案目錄
        """
        self.origin_dir = origin_dir
        self.docs_dir = docs_dir
        
        # 確保目錄存在
        os.makedirs(self.docs_dir, exist_ok=True)
    
    def get_csv_files(self) -> List[str]:
        """
        獲取origin目錄中的所有CSV檔案
        
        Returns:
            List[str]: CSV檔案路徑列表
        """
        csv_files = []
        
        if not os.path.exists(self.origin_dir):
            logger.warning(f"原始檔案目錄不存在: {self.origin_dir}")
            return csv_files
        
        for filename in os.listdir(self.origin_dir):
            if filename.lower().endswith('.csv'):
                file_path = os.path.join(self.origin_dir, filename)
                csv_files.append(file_path)
        
        logger.info(f"找到 {len(csv_files)} 個CSV檔案")
        return csv_files
    
    def read_csv_file(self, file_path: str) -> pd.DataFrame:
        """
        讀取CSV檔案
        
        Args:
            file_path (str): CSV檔案路徑
            
        Returns:
            pd.DataFrame: 讀取的資料，失敗時返回空DataFrame
        """
        try:
            logger.info(f"正在讀取CSV檔案: {os.path.basename(file_path)}")
            
            # 嘗試不同的編碼方式讀取檔案
            encodings = ['utf-8', 'big5', 'cp950', 'gb2312']
            
            for encoding in encodings:
                try:
                    # 讀取CSV檔案
                    df = pd.read_csv(file_path, encoding=encoding)
                    logger.info(f"成功讀取CSV檔案 (編碼: {encoding}): {len(df)} 筆資料")
                    return df
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    logger.warning(f"使用編碼 {encoding} 讀取失敗: {e}")
                    continue
            
            # 如果所有編碼都失敗，嘗試自動偵測
            logger.warning("嘗試自動偵測編碼")
            df = pd.read_csv(file_path, encoding='utf-8', errors='ignore')
            logger.info(f"使用容錯模式讀取CSV檔案: {len(df)} 筆資料")
            return df
            
        except Exception as e:
            logger.error(f"讀取CSV檔案失敗: {e}")
            return pd.DataFrame()
    
    def validate_csv_structure(self, df: pd.DataFrame) -> bool:
        """
        驗證CSV檔案結構
        
        Args:
            df (pd.DataFrame): 待驗證的DataFrame
            
        Returns:
            bool: 結構正確返回True，否則返回False
        """
        if df.empty:
            logger.error("CSV檔案為空")
            return False
        
        # 檢查欄位數量（應該至少有4欄：日期、星期、是否放假、備註）
        if len(df.columns) < 4:
            logger.error(f"CSV檔案欄位數量不足: {len(df.columns)} < 4")
            return False
        
        logger.info(f"CSV檔案結構驗證通過: {len(df.columns)} 欄位, {len(df)} 筆資料")
        return True
    
    def convert_date_format(self, date_str: str) -> str:
        """
        轉換日期格式為ISO 8601格式 (YYYY-MM-DD)
        
        Args:
            date_str (str): 原始日期字串
            
        Returns:
            str: ISO格式日期字串
        """
        try:
            # 嘗試解析不同的日期格式
            date_formats = [
                '%Y/%m/%d',    # 2024/1/1
                '%Y-%m-%d',    # 2024-01-01
                '%Y年%m月%d日', # 2024年1月1日
                '%m/%d/%Y',    # 1/1/2024
                '%d/%m/%Y',    # 1/1/2024
            ]
            
            for fmt in date_formats:
                try:
                    date_obj = datetime.strptime(str(date_str).strip(), fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # 如果以上格式都不匹配，嘗試pandas的自動解析
            date_obj = pd.to_datetime(str(date_str).strip())
            return date_obj.strftime('%Y-%m-%d')
            
        except Exception as e:
            logger.warning(f"日期格式轉換失敗: {date_str} -> {e}")
            return str(date_str).strip()
    
    def convert_holiday_flag(self, flag_value: Any) -> bool:
        """
        轉換放假標誌
        
        Args:
            flag_value: 原始放假標誌值
            
        Returns:
            bool: 放假為True，上班為False
        """
        try:
            # 轉換為字串後處理
            flag_str = str(flag_value).strip()
            
            # 根據需求文件：2表示放假，0表示上班
            if flag_str == '2':
                return True
            elif flag_str == '0':
                return False
            else:
                # 嘗試其他可能的表示方式
                if flag_str.lower() in ['true', '是', '放假', 'holiday']:
                    return True
                elif flag_str.lower() in ['false', '否', '上班', 'work']:
                    return False
                else:
                    logger.warning(f"未知的放假標誌值: {flag_value}")
                    return False
                    
        except Exception as e:
            logger.warning(f"放假標誌轉換失敗: {flag_value} -> {e}")
            return False
    
    def extract_roc_year_from_filename(self, filename: str) -> int:
        """
        從檔案名稱中提取民國年份
        
        Args:
            filename (str): 檔案名稱
            
        Returns:
            int: 民國年份，提取失敗時返回0
        """
        try:
            # 使用正規表達式提取民國年份，例如：114年中華民國政府行政機關辦公日曆表.csv
            pattern = r'(\d{3})年'
            match = re.search(pattern, filename)
            
            if match:
                roc_year = int(match.group(1))
                logger.info(f"從檔案名稱 '{filename}' 提取民國年份: {roc_year}")
                return roc_year
            else:
                logger.warning(f"無法從檔案名稱提取民國年份: {filename}")
                return 0
                
        except Exception as e:
            logger.error(f"提取民國年份時發生錯誤: {e}")
            return 0
    
    def convert_roc_to_western_year(self, roc_year: int) -> int:
        """
        將民國年份轉換為西元年份
        
        Args:
            roc_year (int): 民國年份
            
        Returns:
            int: 西元年份（民國年+1911）
        """
        if roc_year <= 0:
            return 0
        
        western_year = roc_year + 1911
        logger.info(f"民國年份轉換: {roc_year} -> 西元 {western_year}")
        return western_year
    
    def generate_json_filename(self, csv_file_path: str) -> str:
        """
        根據CSV檔案路徑生成對應的JSON檔案名稱（使用西元年）
        
        Args:
            csv_file_path (str): CSV檔案路徑
            
        Returns:
            str: JSON檔案名稱
        """
        filename = os.path.basename(csv_file_path)
        
        # 提取民國年份
        roc_year = self.extract_roc_year_from_filename(filename)
        
        if roc_year > 0:
            # 轉換為西元年份
            western_year = self.convert_roc_to_western_year(roc_year)
            json_filename = f"{western_year}.json"
            logger.info(f"生成JSON檔案名稱: {filename} -> {json_filename}")
            return json_filename
        else:
            # 如果無法提取年份，使用原始檔名
            base_filename = os.path.splitext(filename)[0]
            json_filename = f"{base_filename}.json"
            logger.warning(f"無法提取年份，使用原始檔名: {json_filename}")
            return json_filename
    
    def convert_csv_to_json(self, file_path: str) -> bool:
        """
        將單個CSV檔案轉換為JSON格式
        
        Args:
            file_path (str): CSV檔案路徑
            
        Returns:
            bool: 轉換成功返回True，失敗返回False
        """
        try:
            # 讀取CSV檔案
            df = self.read_csv_file(file_path)
            if not self.validate_csv_structure(df):
                return False
            
            # 準備JSON資料
            json_data = []
            
            for index, row in df.iterrows():
                try:
                    # 提取欄位資料（假設前4欄分別是：日期、星期、是否放假、備註）
                    date_value = row.iloc[0] if len(row) > 0 else ''
                    week_value = row.iloc[1] if len(row) > 1 else ''
                    holiday_flag = row.iloc[2] if len(row) > 2 else 0
                    description = row.iloc[3] if len(row) > 3 else ''
                    
                    # 轉換資料格式
                    record = {
                        'date': self.convert_date_format(date_value),
                        'week': str(week_value).strip() if pd.notna(week_value) else '',
                        'isHoliday': self.convert_holiday_flag(holiday_flag),
                        'description': str(description).strip() if pd.notna(description) else ''
                    }
                    
                    json_data.append(record)
                    
                except Exception as e:
                    logger.warning(f"轉換第 {index + 1} 筆資料時發生錯誤: {e}")
                    continue
            
            if not json_data:
                logger.error("沒有成功轉換任何資料")
                return False
            
            # 生成輸出檔案名稱（使用西元年命名）
            json_filename = self.generate_json_filename(file_path)
            json_path = os.path.join(self.docs_dir, json_filename)
            
            # 寫入JSON檔案
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON檔案轉換成功: {json_filename} ({len(json_data)} 筆資料)")
            return True
            
        except Exception as e:
            logger.error(f"CSV轉JSON轉換失敗: {e}")
            return False
    
    def convert_all(self) -> tuple:
        """
        轉換所有CSV檔案為JSON格式
        
        Returns:
            tuple: (成功轉換檔案數, 總檔案數)
        """
        logger.info("開始執行CSV到JSON的批量轉換")
        
        # 獲取所有CSV檔案
        csv_files = self.get_csv_files()
        if not csv_files:
            logger.warning("沒有找到任何CSV檔案")
            return 0, 0
        
        # 轉換所有檔案
        success_count = 0
        total_count = len(csv_files)
        
        for i, csv_file in enumerate(csv_files, 1):
            logger.info(f"轉換檔案 {i}/{total_count}: {os.path.basename(csv_file)}")
            if self.convert_csv_to_json(csv_file):
                success_count += 1
        
        logger.info(f"批量轉換完成: 成功轉換 {success_count}/{total_count} 個檔案")
        return success_count, total_count
    
    def get_conversion_summary(self) -> Dict[str, Any]:
        """
        獲取轉換摘要資訊
        
        Returns:
            Dict[str, Any]: 包含轉換統計資訊的字典
        """
        csv_files = self.get_csv_files()
        json_files = []
        
        if os.path.exists(self.docs_dir):
            json_files = [f for f in os.listdir(self.docs_dir) if f.lower().endswith('.json')]
        
        return {
            'csv_files_count': len(csv_files),
            'json_files_count': len(json_files),
            'csv_files': [os.path.basename(f) for f in csv_files],
            'json_files': json_files
        }


def main():
    """主函數，用於測試轉換功能"""
    converter = CalendarConverter()
    
    # 顯示轉換前的狀態
    summary_before = converter.get_conversion_summary()
    print(f"轉換前: {summary_before['csv_files_count']} 個CSV檔案")
    
    # 執行轉換
    success_count, total_count = converter.convert_all()
    
    # 顯示轉換結果
    summary_after = converter.get_conversion_summary()
    print(f"轉換後: {summary_after['json_files_count']} 個JSON檔案")
    
    if success_count > 0:
        print(f"轉換執行成功: {success_count}/{total_count} 個檔案轉換完成")
    else:
        print("轉換執行失敗，沒有成功轉換任何檔案")


if __name__ == "__main__":
    main()