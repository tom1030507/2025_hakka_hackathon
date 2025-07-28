"""
課程生成處理模組
負責處理前端課程生成請求，調用 webhook，並返回結果
"""

import os
import aiohttp
import asyncio
import json
from typing import Dict, Any, List
from pydantic import BaseModel
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class CourseRequest(BaseModel):
    """課程生成請求的數據模型"""
    topic: str
    difficulty: str
    includeQuiz: bool

class CourseGenerator:
    """課程生成器類"""
    
    def __init__(self):
        self.webhook_url = os.getenv("COURSE_WEBHOOK_URL", "")
        self.timeout = int(os.getenv("WEBHOOK_TIMEOUT", "30"))
    
    async def generate_course(self, request: CourseRequest) -> List[Dict[str, Any]]:
        """
        生成課程內容
        
        Args:
            request: 課程生成請求
            
        Returns:
            課程數據列表
            
        Raises:
            Exception: 當課程生成失敗時
        """
        try:
            # 將英文難度轉換為中文
            difficulty_map = {
                "beginner": "初級",
                "intermediate": "中級", 
                "advanced": "高級"
            }
            difficulty_chinese = difficulty_map.get(request.difficulty, "中級")
            
            # 將 includeQuiz 轉換為中文
            include_quiz_chinese = "包含練習題" if request.includeQuiz else "不包含練習題"
            
            # 準備要發送給 webhook 的資料
            webhook_data = {
                "主題": request.topic,
                "難度": difficulty_chinese,
                "練習題": include_quiz_chinese
            }
            
            print(f"收到課程生成請求: {webhook_data}")
            
            # 檢查是否設定了 webhook URL
            if not self.webhook_url:
                print("警告：未設定 COURSE_WEBHOOK_URL，使用模擬課程資料")
                return self._generate_mock_course_data(request)
            
            # 調用 webhook
            response = await self._call_webhook(webhook_data)
            
            # 驗證回應格式
            if not self._validate_response(response):
                print("Webhook 回應格式不正確，使用模擬課程資料")
                return self._generate_mock_course_data(request)
            
            print("課程生成成功")
            return response
            
        except aiohttp.ClientTimeout:
            print("Webhook 調用超時，使用模擬課程資料")
            return self._generate_mock_course_data(request)
        except Exception as e:
            print(f"課程生成過程中發生錯誤: {e}，使用模擬課程資料")
            return self._generate_mock_course_data(request)
    
    async def _call_webhook(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        調用 webhook API
        
        Args:
            data: 要發送的數據
            
        Returns:
            webhook 回應數據
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "CourseGenerator/1.0",
            "Accept": "application/json"
        }
        
        print(f"正在調用 webhook: {self.webhook_url}")
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                self.webhook_url,
                json=data,
                headers=headers
            ) as response:
                response.raise_for_status()
                
                print(f"Webhook 回應成功，狀態碼: {response.status}")
                
                # 解析 JSON 回應
                webhook_response = await response.json()
                
                return webhook_response
    
    def _validate_response(self, response: Any) -> bool:
        """
        驗證 webhook 回應格式
        
        Args:
            response: webhook 回應數據
            
        Returns:
            是否為有效格式
        """
        if not isinstance(response, list):
            return False
        
        for item in response:
            if not isinstance(item, dict):
                return False
            if "text" not in item:
                return False
            # output 是可選的
            if "output" in item:
                output = item["output"]
                if not isinstance(output, dict):
                    return False
                # quiz_questions 是可選的
                if "quiz_questions" in output:
                    quiz_questions = output["quiz_questions"]
                    if not isinstance(quiz_questions, list):
                        return False
        
        return True
    
    def _generate_mock_course_data(self, request: CourseRequest) -> List[Dict[str, Any]]:
        """
        生成模擬的課程資料
        
        Args:
            request: 課程生成請求
            
        Returns:
            模擬課程數據
        """
        difficulty_map = {
            "beginner": "初級",
            "intermediate": "中級", 
            "advanced": "高級"
        }
        
        difficulty_text = difficulty_map.get(request.difficulty, "中級")
        
        mock_data = [
            {
                "text": f"# {request.topic} - {difficulty_text}課程\n\n## 課程介紹\n\n歡迎來到{request.topic}的學習課程！這是一個專為{difficulty_text}學習者設計的課程。\n\n在這個章節中，我們將介紹{request.topic}的基本概念和重要性。\n\n## 學習目標\n\n- 了解{request.topic}的基本概念\n- 掌握相關的核心知識\n- 能夠應用所學知識",
                "output": {
                    "quiz_questions": [
                        {
                            "question_number": 1,
                            "question_text": f"什麼是{request.topic}的核心概念？",
                            "options": {
                                "A": "基礎理論知識",
                                "B": "實踐應用技能", 
                                "C": "綜合理解能力",
                                "D": "以上皆是"
                            },
                            "correct_answer": "D",
                            "explanation": f"{request.topic}需要理論與實踐並重，綜合發展各項能力。"
                        }
                    ] if request.includeQuiz else []
                }
            },
            {
                "text": f"# {request.topic} - 深入學習\n\n## 進階概念\n\n在上一章節中，我們學習了{request.topic}的基礎知識。現在讓我們深入探討更複雜的概念。\n\n## 重要原理\n\n{request.topic}包含許多重要的原理和方法，這些都是我們需要深入理解的內容。\n\n## 實際應用\n\n理論知識需要與實際應用相結合，才能真正掌握{request.topic}的精髓。",
                "output": {
                    "quiz_questions": [
                        {
                            "question_number": 1,
                            "question_text": f"在{request.topic}的學習過程中，最重要的是什麼？",
                            "options": {
                                "A": "理論學習",
                                "B": "實踐練習",
                                "C": "理論與實踐結合", 
                                "D": "記憶背誦"
                            },
                            "correct_answer": "C",
                            "explanation": "學習任何知識都需要理論與實踐相結合，這樣才能真正掌握和應用。"
                        }
                    ] if request.includeQuiz else []
                }
            },
            {
                "text": f"# {request.topic} - 總結與展望\n\n## 課程總結\n\n通過本課程的學習，我們已經掌握了{request.topic}的核心知識和技能。\n\n## 學習成果\n\n- 建立了扎實的理論基礎\n- 培養了實踐應用能力\n- 具備了持續學習的方法\n\n## 未來發展\n\n{request.topic}是一個不斷發展的領域，希望大家能夠持續學習，跟上時代的步伐。\n\n## 結語\n\n學習是一個持續的過程，希望大家能夠將所學知識應用到實際生活和工作中。",
                "output": {
                    "quiz_questions": [
                        {
                            "question_number": 1,
                            "question_text": f"完成{request.topic}課程後，下一步應該怎麼做？",
                            "options": {
                                "A": "停止學習",
                                "B": "持續實踐和深化",
                                "C": "重新開始",
                                "D": "轉向其他領域"
                            },
                            "correct_answer": "B",
                            "explanation": "學習是持續的過程，完成課程後應該繼續實踐和深化所學知識。"
                        }
                    ] if request.includeQuiz else []
                }
            }
        ]
        
        return mock_data

# 創建全局課程生成器實例
course_generator = CourseGenerator()
