"""
AI助手工具，集成DeepSeek大模型
"""
import json
import requests
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class DeepSeekAI:
    """
    DeepSeek AI 助手类
    """
    def __init__(self, api_key=None):
        """
        初始化DeepSeekAI
        
        @param {string} api_key - API密钥
        """
        self.api_key = api_key or current_app.config.get('DEEPSEEK_API_KEY')
        self.api_base = current_app.config.get('DEEPSEEK_API_BASE', 'https://api.deepseek.com')
        
    def analyze_sentiment(self, text):
        """
        分析文本情感
        
        @param {string} text - 待分析文本
        @return {float} - 情感分数 (-1.0 到 1.0)
        """
        try:
            # 此处为模拟实现，实际需要调用DeepSeek API
            # 正式开发时需替换为实际API调用
            # 简单分析算法，仅用于演示
            positive_words = ['好', '满意', '感谢', '喜欢', '很棒', '优秀']
            negative_words = ['差', '不满', '投诉', '退款', '失望', '问题']
            
            score = 0.0
            for word in positive_words:
                if word in text:
                    score += 0.2
            
            for word in negative_words:
                if word in text:
                    score -= 0.2
            
            # 限制范围在 -1.0 到 1.0
            return max(-1.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"情感分析失败: {str(e)}")
            return 0.0  # 默认中性
    
    def generate_response(self, question, context=None, knowledge_base=None):
        """
        生成问题的回复
        
        @param {string} question - 用户提问
        @param {list} context - 对话上下文
        @param {list} knowledge_base - 知识库数据
        @return {string} - 生成的回复
        """
        try:
            # 此处为模拟实现，实际需要调用DeepSeek API
            # 正式开发时需替换为实际API调用
            if '价格' in question or '费用' in question:
                return "我们的收费标准根据具体治疗项目而定，一般种植牙单颗价格在5000-15000元不等，具体可以到店咨询或预约医生进行专业评估。"
            elif '疼痛' in question or '痛不痛' in question:
                return "我们采用先进的麻醉技术，治疗过程中一般不会有明显疼痛，术后可能有轻微不适，可按医嘱服用止痛药物缓解。"
            elif '时间' in question or '多久' in question:
                return "一般种植牙手术时间约1-2小时，但整个疗程包括愈合期可能需要3-6个月。正畸治疗时间则因个人情况不同，通常在1-2年左右。"
            else:
                return "感谢您的咨询，这是一个很好的问题。我们的医生团队非常专业，建议您可以到店面详细咨询，或者预约我们的专家进行一对一沟通，为您提供最适合的个性化治疗方案。"
            
        except Exception as e:
            logger.error(f"回复生成失败: {str(e)}")
            return "非常抱歉，系统临时出现故障，请稍后再试或联系在线客服。"
    
    def summarize_conversation(self, conversation):
        """
        总结对话内容
        
        @param {list} conversation - 对话记录
        @return {dict} - 对话摘要信息
        """
        try:
            # 此处为模拟实现，实际需要调用DeepSeek API
            # 正式开发时需替换为实际API调用
            
            # 模拟提取关键信息
            summary = {
                'key_points': [],
                'customer_needs': [],
                'follow_up_items': []
            }
            
            for msg in conversation:
                text = msg.get('content', '')
                is_customer = msg.get('role') == 'customer'
                
                if is_customer:
                    if '价格' in text or '费用' in text:
                        summary['customer_needs'].append('关心价格因素')
                    if '疼痛' in text or '痛' in text:
                        summary['customer_needs'].append('关心治疗疼痛程度')
                    if '时间' in text or '多久' in text:
                        summary['customer_needs'].append('关心治疗时间')
                    if '预约' in text:
                        summary['follow_up_items'].append('客户想预约咨询')
            
            # 去重
            summary['customer_needs'] = list(set(summary['customer_needs']))
            summary['follow_up_items'] = list(set(summary['follow_up_items']))
            
            return summary
            
        except Exception as e:
            logger.error(f"对话总结失败: {str(e)}")
            return {
                'key_points': [],
                'customer_needs': [],
                'follow_up_items': ['系统处理失败，请手动跟进']
            }
    
    def generate_marketing_content(self, client_info, template_type='promotion'):
        """
        生成营销内容
        
        @param {dict} client_info - 客户信息
        @param {string} template_type - 模板类型
        @return {string} - 生成的营销内容
        """
        try:
            # 此处为模拟实现，实际需要调用DeepSeek API
            # 正式开发时需替换为实际API调用
            
            templates = {
                'promotion': f"尊敬的{client_info.get('name', '顾客')}，感谢您对我们的信任！我们近期推出了{client_info.get('interest', '牙齿美白')}优惠活动，前20名预约可享受8折优惠，期待您的光临！",
                'follow_up': f"尊敬的{client_info.get('name', '顾客')}，距离您上次的{client_info.get('last_treatment', '口腔检查')}已经过去了{client_info.get('days_since_visit', 90)}天，建议进行复查，可以随时预约！",
                'birthday': f"亲爱的{client_info.get('name', '顾客')}，祝您生日快乐！作为我们尊贵的客户，我们为您准备了生日专属礼遇，本月内到店可享受指定项目7折优惠，期待您的到来！"
            }
            
            return templates.get(template_type, templates['promotion'])
            
        except Exception as e:
            logger.error(f"营销内容生成失败: {str(e)}")
            return f"尊敬的顾客，感谢您对我们的信任与支持！" 