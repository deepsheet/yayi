# LY牙助手

LY牙助手是一个基于Python Flask框架开发的牙科门店营销管理SaaS系统，旨在为牙科诊所门店提供线上新客户拓展，增加门店引流到店，实现客户管理、营销自动化与跨端协作。

## 项目特点

- **多角色支持**：支持管理员、全职咨询师、兼职咨询师和普通用户等多种角色
- **客户管理**：查看客户基础信息、历史沟通记录、诊疗记录，支持集成财务系统
- **咨询师绑定规则**：客户默认绑定唯一咨询师，支持"孤儿客户"机制
- **知识库管理**：结构化存储牙科问答知识，支持动态学习机制
- **AI智能助手**：集成DeepSeek大模型，提供智能会话、情感分析、营销自动化等功能
- **多端适配**：同时兼容PC端和移动端，提供良好的用户体验

## 技术架构

- **后端**：Python Flask框架
- **前端**：HTML5, CSS3, JavaScript, Bootstrap 5
- **数据库**：MySQL
- **AI技术**：DeepSeek大模型
- **部署**：支持Docker容器化部署

## 安装指南

### 前置条件

- Python 3.8+
- MySQL 5.7+
- 可选：Redis (用于缓存)

### 安装步骤

1. 克隆仓库

```bash
git clone https://github.com/yourusername/ly-dental-assistant.git
cd ly-dental-assistant
```

2. 创建并激活虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用 venv\Scripts\activate
```

3. 安装依赖包

```bash
pip install -r requirements.txt
```

4. 配置环境变量（创建.env文件）

```
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://username:password@localhost/ly_dental_dev
```

5. 初始化数据库

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. 启动开发服务器

```bash
flask run
```

访问 http://localhost:5000 即可打开应用。

## 项目结构

```
ly-dental-assistant/
├── app/                    # 应用主目录
│   ├── api/                # API接口
│   ├── models/             # 数据模型
│   ├── static/             # 静态资源
│   ├── templates/          # 模板文件
│   ├── utils/              # 工具类
│   ├── views/              # 视图函数
│   └── __init__.py         # 应用初始化
├── migrations/             # 数据库迁移文件
├── config.py               # 配置文件
├── requirements.txt        # 依赖列表
├── run.py                  # 应用入口
└── README.md               # 项目说明
```

## 主要功能模块

### 店铺端（B端）

- 客户管理：查看客户信息、历史沟通记录、诊疗记录
- 咨询师绑定规则：支持默认绑定、孤儿客户处理、线下流量管理等
- 知识库管理：结构化存储牙科问答知识，动态学习机制

### 咨询师端（C端）

- 普通用户功能：查看附近门店、到店扫码登入、预约系统
- 兼职咨询师功能：客户管理、在线沟通、智能营销
- 全职咨询师功能：更强大的客户管理和营销功能
- AI辅助工作台：会话摘要生成、智能跟单提醒
- 跨平台客户画像：企微聊天记录+小程序行为数据分析

### 智能化中枢

- DeepSeek大模型集成：智能会话系统
- 营销自动化引擎：个性化促销方案、朋友圈互动文案
- 企微深度集成：自动化运营、朋友圈管理
- 自动化消息中枢：定时/事件触发消息推送
- 权限体系：根据角色智能分配功能权限

## 开发团队

- 产品经理：XXX
- 前端开发：XXX
- 后端开发：XXX
- UI设计：XXX
- 测试：XXX

## 许可证

本项目采用MIT许可证，详情见LICENSE文件。 