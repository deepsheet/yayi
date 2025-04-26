-- 创建数据库
CREATE DATABASE IF NOT EXISTS yayi DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE yayi;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(20) DEFAULT 'client' COMMENT 'client, consultant, fulltime_consultant, admin',
    avatar VARCHAR(200),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 客户表
CREATE TABLE IF NOT EXISTS clients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(64) NOT NULL,
    gender VARCHAR(10),
    birth_date DATE,
    address VARCHAR(256),
    contact_info VARCHAR(128),
    tags VARCHAR(256) COMMENT '客户标签，逗号分隔',
    is_orphan BOOLEAN DEFAULT FALSE COMMENT '是否为孤儿客户',
    last_contact DATETIME,
    assigned_consultant_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 咨询师表
CREATE TABLE IF NOT EXISTS consultants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    type VARCHAR(20) COMMENT 'fulltime 或 parttime',
    verified BOOLEAN DEFAULT FALSE,
    store_id INT,
    certification TEXT COMMENT 'JSON存储认证信息',
    bio TEXT COMMENT '个人简介',
    specialties VARCHAR(256) COMMENT '专业领域，逗号分隔',
    rating FLOAT DEFAULT 5.0,
    contact_info VARCHAR(128) COMMENT '联系电话',
    wechat VARCHAR(64) COMMENT '微信号',
    working_hours VARCHAR(256) COMMENT '工作时间',
    education TEXT COMMENT '教育背景',
    certifications TEXT COMMENT '专业证书',
    experience TEXT COMMENT '工作经验',
    supervisor_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 门店表
CREATE TABLE IF NOT EXISTS stores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(128) NOT NULL,
    address VARCHAR(256) NOT NULL,
    contact VARCHAR(64),
    description TEXT,
    latitude FLOAT,
    longitude FLOAT,
    business_hours TEXT COMMENT 'JSON格式存储营业时间',
    photos TEXT COMMENT 'JSON数组存储门店照片',
    specialties VARCHAR(256) COMMENT '专长领域，逗号分隔',
    status VARCHAR(20) DEFAULT 'active' COMMENT 'active, inactive',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 医生表
CREATE TABLE IF NOT EXISTS doctors (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(64) NOT NULL,
    title VARCHAR(64) COMMENT '如主任医师、副主任医师等',
    specialty VARCHAR(128) COMMENT '专业领域，如种植、正畸等',
    bio TEXT COMMENT '个人简介',
    avatar VARCHAR(200),
    store_id INT,
    status VARCHAR(20) DEFAULT 'available' COMMENT 'available, busy, off_duty',
    rating FLOAT DEFAULT 5.0,
    rating_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 治疗记录表
CREATE TABLE IF NOT EXISTS treatments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT NOT NULL,
    store_id INT NOT NULL,
    doctor_id INT NOT NULL,
    consultant_id INT,
    type VARCHAR(64) COMMENT '如种植、正畸、美白等',
    description TEXT,
    fee FLOAT,
    payment_status VARCHAR(20) DEFAULT 'unpaid' COMMENT 'unpaid, partial, paid',
    paid_amount FLOAT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'scheduled' COMMENT 'scheduled, in_progress, completed, cancelled',
    appointment_date DATETIME,
    rating FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 消息表
CREATE TABLE IF NOT EXISTS messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    content TEXT NOT NULL,
    msg_type VARCHAR(20) DEFAULT 'text' COMMENT 'text, image, file, system',
    is_read BOOLEAN DEFAULT FALSE,
    attachment_url VARCHAR(256),
    sentiment_score FLOAT COMMENT '消息情感值（AI分析）-1.0到1.0',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 群发消息表
CREATE TABLE IF NOT EXISTS group_messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sender_id INT NOT NULL,
    content TEXT NOT NULL,
    msg_type VARCHAR(20) DEFAULT 'text',
    target_type VARCHAR(20) COMMENT 'all_clients, tagged_clients',
    target_tags VARCHAR(256) COMMENT '如果是tagged_clients，存储目标标签',
    attachment_url VARCHAR(256),
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending, sending, sent, failed',
    sent_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 知识库文章表
CREATE TABLE IF NOT EXISTS knowledge_articles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(256) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(64) COMMENT '如种植、正畸、美白等',
    tags VARCHAR(256) COMMENT '标签，逗号分隔',
    author_id INT NOT NULL,
    rating FLOAT DEFAULT 5.0,
    use_count INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending, approved, rejected',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 知识问答表
CREATE TABLE IF NOT EXISTS knowledge_qa (
    id INT PRIMARY KEY AUTO_INCREMENT,
    question VARCHAR(512) NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(64),
    tags VARCHAR(256),
    source VARCHAR(20) DEFAULT 'preset' COMMENT 'preset, conversation',
    source_id INT COMMENT '如果来自对话，存储对话ID',
    use_count INT DEFAULT 0,
    rating FLOAT DEFAULT 5.0,
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending, approved, rejected',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 删除所有表的数据
DELETE FROM knowledge_qa;
DELETE FROM knowledge_articles;
DELETE FROM group_messages;
DELETE FROM messages;
DELETE FROM treatments;
DELETE FROM clients;
DELETE FROM consultants;
DELETE FROM doctors;
DELETE FROM stores;
DELETE FROM users;

-- 插入示例数据

-- 1. 创建管理员账号
INSERT INTO users (username, email, phone, password_hash, role, is_active, is_verified)
VALUES ('admin', 'admin@lydental.com', '13800138000', 'pbkdf2:sha256:1000000$NcSA0T1UhVGz3JQK$80b24f626125302bedf05929ae8e35f995d62a364313df4365c8d950f86f8595', 'admin', TRUE, TRUE);

-- 2. 创建demo账号
INSERT INTO users (username, email, phone, password_hash, role, is_active, is_verified)
VALUES ('demo', 'demo@lydental.com', '13800138001', 'pbkdf2:sha256:1000000$NcSA0T1UhVGz3JQK$80b24f626125302bedf05929ae8e35f995d62a364313df4365c8d950f86f8595', 'client', TRUE, TRUE);

-- 3. 创建示例门店
INSERT INTO stores (name, address, contact, description, latitude, longitude, business_hours, specialties)
VALUES 
('LY牙科总店', '上海市浦东新区张杨路500号', '021-12345678', 'LY牙科旗舰店，提供全方位的牙科服务', 31.2304, 121.4737, 
'{"monday": "9:00-18:00", "tuesday": "9:00-18:00", "wednesday": "9:00-18:00", "thursday": "9:00-18:00", "friday": "9:00-18:00", "saturday": "9:00-17:00", "sunday": "休息"}',
'种植牙,正畸,美白,修复'),
('LY牙科分店', '上海市静安区南京西路1000号', '021-87654321', 'LY牙科分店，提供专业的牙科服务', 31.2304, 121.4737,
'{"monday": "9:00-18:00", "tuesday": "9:00-18:00", "wednesday": "9:00-18:00", "thursday": "9:00-18:00", "friday": "9:00-18:00", "saturday": "9:00-17:00", "sunday": "休息"}',
'种植牙,正畸,美白,修复');

-- 4. 创建示例医生
INSERT INTO doctors (name, title, specialty, bio, store_id, status)
VALUES 
('张医生', '主任医师', '种植牙,正畸', '从事牙科临床工作20年，擅长种植牙和正畸治疗', 1, 'available'),
('李医生', '副主任医师', '美白,修复', '从事牙科临床工作15年，擅长牙齿美白和修复治疗', 1, 'available'),
('王医生', '主治医师', '牙周病,修复', '从事牙科临床工作10年，擅长牙周病治疗和修复', 2, 'available');

-- 5. 创建示例咨询师
INSERT INTO users (username, email, phone, password_hash, role, is_active, is_verified)
VALUES 
('consultant1', 'consultant1@lydental.com', '13800138002', 'pbkdf2:sha256:1000000$NcSA0T1UhVGz3JQK$80b24f626125302bedf05929ae8e35f995d62a364313df4365c8d950f86f8595', 'fulltime_consultant', TRUE, TRUE),
('consultant2', 'consultant2@lydental.com', '13800138003', 'pbkdf2:sha256:1000000$NcSA0T1UhVGz3JQK$80b24f626125302bedf05929ae8e35f995d62a364313df4365c8d950f86f8595', 'consultant', TRUE, TRUE);

INSERT INTO consultants (user_id, type, verified, store_id, bio, specialties)
VALUES 
(3, 'fulltime', TRUE, 1, '资深牙科咨询师，擅长客户沟通和方案制定', '种植牙,正畸'),
(4, 'parttime', TRUE, 1, '专业牙科咨询师，擅长客户服务', '美白,修复');

-- 6. 创建示例客户
INSERT INTO users (username, email, phone, password_hash, role, is_active, is_verified)
VALUES 
('client1', 'client1@example.com', '13800138004', 'pbkdf2:sha256:1000000$NcSA0T1UhVGz3JQK$80b24f626125302bedf05929ae8e35f995d62a364313df4365c8d950f86f8595', 'client', TRUE, TRUE),
('client2', 'client2@example.com', '13800138005', 'pbkdf2:sha256:1000000$NcSA0T1UhVGz3JQK$80b24f626125302bedf05929ae8e35f995d62a364313df4365c8d950f86f8595', 'client', TRUE, TRUE);

INSERT INTO clients (user_id, name, gender, birth_date, address, contact_info, tags, assigned_consultant_id)
VALUES 
(5, '王先生', '男', '1990-01-01', '上海市浦东新区', '13800138004', '种植牙,正畸', 1),
(6, '李女士', '女', '1992-02-02', '上海市浦东新区', '13800138005', '美白,修复', 2);

-- 7. 创建示例治疗记录
INSERT INTO treatments (client_id, store_id, doctor_id, consultant_id, type, description, fee, status, appointment_date)
VALUES 
(1, 1, 1, 1, '种植牙', '单颗种植牙治疗', 15000.00, 'scheduled', '2024-03-20 10:00:00'),
(2, 1, 2, 2, '牙齿美白', '冷光美白治疗', 3000.00, 'scheduled', '2024-03-21 14:00:00'),
(1, 1, 1, 1, '正畸', '牙齿矫正治疗', 20000.00, 'in_progress', '2024-03-15 09:00:00'),
(2, 2, 3, 2, '牙周病', '牙周病治疗', 5000.00, 'completed', '2024-03-10 15:00:00');

-- 8. 创建示例消息
INSERT INTO messages (sender_id, receiver_id, content, msg_type)
VALUES 
(2, 4, '您好，我是您的专属咨询师，有任何问题都可以随时咨询我', 'text'),
(4, 2, '好的，谢谢', 'text'),
(5, 3, '请问种植牙的费用是多少？', 'text'),
(3, 5, '种植牙的费用根据具体情况而定，一般在15000-30000元之间', 'text'),
(6, 4, '我想预约牙齿美白', 'text'),
(4, 6, '好的，我帮您安排在下周二下午2点', 'text');

-- 9. 创建示例知识库文章
INSERT INTO knowledge_articles (title, content, category, tags, author_id, status)
VALUES 
('种植牙的注意事项', '种植牙术后需要注意口腔卫生，避免剧烈运动...', '种植牙', '种植牙,术后护理', 1, 'approved'),
('牙齿美白的常见问题', '牙齿美白后可能会出现敏感症状，这是正常的...', '美白', '美白,常见问题', 1, 'approved'),
('正畸治疗的过程', '正畸治疗一般需要1-2年时间，期间需要定期复诊...', '正畸', '正畸,治疗过程', 1, 'approved'),
('牙周病的预防', '保持良好的口腔卫生习惯，定期洁牙可以有效预防牙周病...', '牙周病', '牙周病,预防', 1, 'approved');

-- 10. 创建示例知识问答
INSERT INTO knowledge_qa (question, answer, category, tags, status)
VALUES 
('种植牙疼吗？', '种植牙手术过程中会使用麻醉，一般不会感到疼痛...', '种植牙', '种植牙,疼痛', 'approved'),
('牙齿美白后需要注意什么？', '牙齿美白后24小时内避免食用深色食物...', '美白', '美白,注意事项', 'approved'),
('正畸需要多长时间？', '正畸治疗的时间因人而异，一般需要1-2年...', '正畸', '正畸,时间', 'approved'),
('牙周病可以治愈吗？', '牙周病早期可以治愈，晚期需要长期维护...', '牙周病', '牙周病,治疗', 'approved'); 