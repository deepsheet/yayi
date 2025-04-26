"""add new fields to consultant model

Revision ID: 3f563ffc5d68
Revises: 
Create Date: 2024-03-19 19:02:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3f563ffc5d68'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 先删除外键约束
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.drop_constraint('clients_ibfk_1', type_='foreignkey')
    
    # 添加新字段到consultants表
    with op.batch_alter_table('consultants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('contact_info', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('wechat', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('working_hours', sa.String(length=256), nullable=True))
        batch_op.add_column(sa.Column('education', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('certifications', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('experience', sa.Text(), nullable=True))
    
    # 重新添加外键约束
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.create_foreign_key('clients_ibfk_1', 'consultants', ['assigned_consultant_id'], ['id'])

    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
        batch_op.alter_column('name',
               existing_type=mysql.VARCHAR(length=64),
               nullable=True)
        batch_op.alter_column('tags',
               existing_type=mysql.VARCHAR(length=256),
               comment=None,
               existing_comment='客户标签，逗号分隔',
               existing_nullable=True)
        batch_op.alter_column('is_orphan',
               existing_type=mysql.TINYINT(display_width=1),
               comment=None,
               existing_comment='是否为孤儿客户',
               existing_nullable=True,
               existing_server_default=sa.text("'0'"))
        batch_op.create_foreign_key(None, 'consultants', ['assigned_consultant_id'], ['id'])
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'])

    with op.batch_alter_table('consultants', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
        batch_op.alter_column('type',
               existing_type=mysql.VARCHAR(length=20),
               comment=None,
               existing_comment='fulltime 或 parttime',
               existing_nullable=True)
        batch_op.alter_column('certification',
               existing_type=mysql.TEXT(),
               comment=None,
               existing_comment='JSON存储认证信息',
               existing_nullable=True)
        batch_op.alter_column('bio',
               existing_type=mysql.TEXT(),
               comment=None,
               existing_comment='个人简介',
               existing_nullable=True)
        batch_op.alter_column('specialties',
               existing_type=mysql.VARCHAR(length=256),
               comment=None,
               existing_comment='专业领域，逗号分隔',
               existing_nullable=True)
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'])
        batch_op.create_foreign_key(None, 'stores', ['store_id'], ['id'])
        batch_op.create_foreign_key(None, 'consultants', ['supervisor_id'], ['id'])

    with op.batch_alter_table('doctors', schema=None) as batch_op:
        batch_op.alter_column('title',
               existing_type=mysql.VARCHAR(length=64),
               comment=None,
               existing_comment='如主任医师、副主任医师等',
               existing_nullable=True)
        batch_op.alter_column('specialty',
               existing_type=mysql.VARCHAR(length=128),
               comment=None,
               existing_comment='专业领域，如种植、正畸等',
               existing_nullable=True)
        batch_op.alter_column('bio',
               existing_type=mysql.TEXT(),
               comment=None,
               existing_comment='个人简介',
               existing_nullable=True)
        batch_op.alter_column('status',
               existing_type=mysql.VARCHAR(length=20),
               comment=None,
               existing_comment='available, busy, off_duty',
               existing_nullable=True,
               existing_server_default=sa.text("'available'"))
        batch_op.create_foreign_key(None, 'stores', ['store_id'], ['id'])

    with op.batch_alter_table('group_messages', schema=None) as batch_op:
        batch_op.alter_column('sender_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
        batch_op.alter_column('content',
               existing_type=mysql.TEXT(),
               nullable=True)
        batch_op.alter_column('target_type',
               existing_type=mysql.VARCHAR(length=20),
               comment=None,
               existing_comment='all_clients, tagged_clients',
               existing_nullable=True)
        batch_op.alter_column('target_tags',
               existing_type=mysql.VARCHAR(length=256),
               comment=None,
               existing_comment='如果是tagged_clients，存储目标标签',
               existing_nullable=True)
        batch_op.alter_column('status',
               existing_type=mysql.VARCHAR(length=20),
               comment=None,
               existing_comment='pending, sending, sent, failed',
               existing_nullable=True,
               existing_server_default=sa.text("'pending'"))
        batch_op.create_foreign_key(None, 'users', ['sender_id'], ['id'])

    with op.batch_alter_table('knowledge_articles', schema=None) as batch_op:
        batch_op.alter_column('category',
               existing_type=mysql.VARCHAR(length=64),
               comment=None,
               existing_comment='如种植、正畸、美白等',
               existing_nullable=True)
        batch_op.alter_column('tags',
               existing_type=mysql.VARCHAR(length=256),
               comment=None,
               existing_comment='标签，逗号分隔',
               existing_nullable=True)
        batch_op.alter_column('author_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
        batch_op.alter_column('status',
               existing_type=mysql.VARCHAR(length=20),
               comment=None,
               existing_comment='pending, approved, rejected',
               existing_nullable=True,
               existing_server_default=sa.text("'pending'"))
        batch_op.create_foreign_key(None, 'users', ['author_id'], ['id'])

    with op.batch_alter_table('knowledge_qa', schema=None) as batch_op:
        batch_op.alter_column('source',
               existing_type=mysql.VARCHAR(length=20),
               comment=None,
               existing_comment='preset, conversation',
               existing_nullable=True,
               existing_server_default=sa.text("'preset'"))
        batch_op.alter_column('source_id',
               existing_type=mysql.INTEGER(),
               comment=None,
               existing_comment='如果来自对话，存储对话ID',
               existing_nullable=True)
        batch_op.alter_column('status',
               existing_type=mysql.VARCHAR(length=20),
               comment=None,
               existing_comment='pending, approved, rejected',
               existing_nullable=True,
               existing_server_default=sa.text("'pending'"))

    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.alter_column('sender_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
        batch_op.alter_column('receiver_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
        batch_op.alter_column('content',
               existing_type=mysql.TEXT(),
               nullable=True)
        batch_op.alter_column('msg_type',
               existing_type=mysql.VARCHAR(length=20),
               comment=None,
               existing_comment='text, image, file, system',
               existing_nullable=True,
               existing_server_default=sa.text("'text'"))
        batch_op.alter_column('sentiment_score',
               existing_type=mysql.FLOAT(),
               comment=None,
               existing_comment='消息情感值（AI分析）-1.0到1.0',
               existing_nullable=True)
        batch_op.create_foreign_key(None, 'users', ['sender_id'], ['id'])
        batch_op.create_foreign_key(None, 'users', ['receiver_id'], ['id'])

    with op.batch_alter_table('stores', schema=None) as batch_op:
        batch_op.alter_column('business_hours',
               existing_type=mysql.TEXT(),
               comment=None,
               existing_comment='JSON格式存储营业时间',
               existing_nullable=True)
        batch_op.alter_column('photos',
               existing_type=mysql.TEXT(),
               comment=None,
               existing_comment='JSON数组存储门店照片',
               existing_nullable=True)
        batch_op.alter_column('specialties',
               existing_type=mysql.VARCHAR(length=256),
               comment=None,
               existing_comment='专长领域，逗号分隔',
               existing_nullable=True)
        batch_op.alter_column('status',
               existing_type=mysql.VARCHAR(length=20),
               comment=None,
               existing_comment='active, inactive',
               existing_nullable=True,
               existing_server_default=sa.text("'active'"))

    with op.batch_alter_table('treatments', schema=None) as batch_op:
        batch_op.alter_column('client_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
        batch_op.alter_column('store_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
        batch_op.alter_column('doctor_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
        batch_op.alter_column('type',
               existing_type=mysql.VARCHAR(length=64),
               comment=None,
               existing_comment='如种植、正畸、美白等',
               existing_nullable=True)
        batch_op.alter_column('payment_status',
               existing_type=mysql.VARCHAR(length=20),
               comment=None,
               existing_comment='unpaid, partial, paid',
               existing_nullable=True,
               existing_server_default=sa.text("'unpaid'"))
        batch_op.alter_column('status',
               existing_type=mysql.VARCHAR(length=20),
               comment=None,
               existing_comment='scheduled, in_progress, completed, cancelled',
               existing_nullable=True,
               existing_server_default=sa.text("'scheduled'"))
        batch_op.create_foreign_key(None, 'doctors', ['doctor_id'], ['id'])
        batch_op.create_foreign_key(None, 'clients', ['client_id'], ['id'])
        batch_op.create_foreign_key(None, 'stores', ['store_id'], ['id'])
        batch_op.create_foreign_key(None, 'consultants', ['consultant_id'], ['id'])
        batch_op.drop_column('rating')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=mysql.VARCHAR(length=64),
               nullable=True)
        batch_op.alter_column('password_hash',
               existing_type=mysql.VARCHAR(length=128),
               nullable=True)
        batch_op.alter_column('role',
               existing_type=mysql.VARCHAR(length=20),
               comment=None,
               existing_comment='client, consultant, fulltime_consultant, admin',
               existing_nullable=True,
               existing_server_default=sa.text("'client'"))
        batch_op.drop_index('email')
        batch_op.drop_index('phone')
        batch_op.drop_index('username')
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_phone'), ['phone'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # 删除外键约束
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.drop_constraint('clients_ibfk_1', type_='foreignkey')
    
    # 删除新添加的字段
    with op.batch_alter_table('consultants', schema=None) as batch_op:
        batch_op.drop_column('experience')
        batch_op.drop_column('certifications')
        batch_op.drop_column('education')
        batch_op.drop_column('working_hours')
        batch_op.drop_column('wechat')
        batch_op.drop_column('contact_info')
    
    # 重新添加外键约束
    with op.batch_alter_table('clients', schema=None) as batch_op:
        batch_op.create_foreign_key('clients_ibfk_1', 'consultants', ['assigned_consultant_id'], ['id'])

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_phone'))
        batch_op.drop_index(batch_op.f('ix_users_email'))
        batch_op.create_index('username', ['username'], unique=True)
        batch_op.create_index('phone', ['phone'], unique=True)
        batch_op.create_index('email', ['email'], unique=True)
        batch_op.alter_column('role',
               existing_type=mysql.VARCHAR(length=20),
               comment='client, consultant, fulltime_consultant, admin',
               existing_nullable=True,
               existing_server_default=sa.text("'client'"))
        batch_op.alter_column('password_hash',
               existing_type=mysql.VARCHAR(length=128),
               nullable=False)
        batch_op.alter_column('username',
               existing_type=mysql.VARCHAR(length=64),
               nullable=False)

    with op.batch_alter_table('treatments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rating', mysql.FLOAT(), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('status',
               existing_type=mysql.VARCHAR(length=20),
               comment='scheduled, in_progress, completed, cancelled',
               existing_nullable=True,
               existing_server_default=sa.text("'scheduled'"))
        batch_op.alter_column('payment_status',
               existing_type=mysql.VARCHAR(length=20),
               comment='unpaid, partial, paid',
               existing_nullable=True,
               existing_server_default=sa.text("'unpaid'"))
        batch_op.alter_column('type',
               existing_type=mysql.VARCHAR(length=64),
               comment='如种植、正畸、美白等',
               existing_nullable=True)
        batch_op.alter_column('doctor_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
        batch_op.alter_column('store_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
        batch_op.alter_column('client_id',
               existing_type=mysql.INTEGER(),
               nullable=False)

    with op.batch_alter_table('stores', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=mysql.VARCHAR(length=20),
               comment='active, inactive',
               existing_nullable=True,
               existing_server_default=sa.text("'active'"))
        batch_op.alter_column('specialties',
               existing_type=mysql.VARCHAR(length=256),
               comment='专长领域，逗号分隔',
               existing_nullable=True)
        batch_op.alter_column('photos',
               existing_type=mysql.TEXT(),
               comment='JSON数组存储门店照片',
               existing_nullable=True)
        batch_op.alter_column('business_hours',
               existing_type=mysql.TEXT(),
               comment='JSON格式存储营业时间',
               existing_nullable=True)

    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('sentiment_score',
               existing_type=mysql.FLOAT(),
               comment='消息情感值（AI分析）-1.0到1.0',
               existing_nullable=True)
        batch_op.alter_column('msg_type',
               existing_type=mysql.VARCHAR(length=20),
               comment='text, image, file, system',
               existing_nullable=True,
               existing_server_default=sa.text("'text'"))
        batch_op.alter_column('content',
               existing_type=mysql.TEXT(),
               nullable=False)
        batch_op.alter_column('receiver_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
        batch_op.alter_column('sender_id',
               existing_type=mysql.INTEGER(),
               nullable=False)

    with op.batch_alter_table('knowledge_qa', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=mysql.VARCHAR(length=20),
               comment='pending, approved, rejected',
               existing_nullable=True,
               existing_server_default=sa.text("'pending'"))
        batch_op.alter_column('source_id',
               existing_type=mysql.INTEGER(),
               comment='如果来自对话，存储对话ID',
               existing_nullable=True)
        batch_op.alter_column('source',
               existing_type=mysql.VARCHAR(length=20),
               comment='preset, conversation',
               existing_nullable=True,
               existing_server_default=sa.text("'preset'"))

    with op.batch_alter_table('knowledge_articles', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('status',
               existing_type=mysql.VARCHAR(length=20),
               comment='pending, approved, rejected',
               existing_nullable=True,
               existing_server_default=sa.text("'pending'"))
        batch_op.alter_column('author_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
        batch_op.alter_column('tags',
               existing_type=mysql.VARCHAR(length=256),
               comment='标签，逗号分隔',
               existing_nullable=True)
        batch_op.alter_column('category',
               existing_type=mysql.VARCHAR(length=64),
               comment='如种植、正畸、美白等',
               existing_nullable=True)

    with op.batch_alter_table('group_messages', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('status',
               existing_type=mysql.VARCHAR(length=20),
               comment='pending, sending, sent, failed',
               existing_nullable=True,
               existing_server_default=sa.text("'pending'"))
        batch_op.alter_column('target_tags',
               existing_type=mysql.VARCHAR(length=256),
               comment='如果是tagged_clients，存储目标标签',
               existing_nullable=True)
        batch_op.alter_column('target_type',
               existing_type=mysql.VARCHAR(length=20),
               comment='all_clients, tagged_clients',
               existing_nullable=True)
        batch_op.alter_column('content',
               existing_type=mysql.TEXT(),
               nullable=False)
        batch_op.alter_column('sender_id',
               existing_type=mysql.INTEGER(),
               nullable=False)

    with op.batch_alter_table('doctors', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('status',
               existing_type=mysql.VARCHAR(length=20),
               comment='available, busy, off_duty',
               existing_nullable=True,
               existing_server_default=sa.text("'available'"))
        batch_op.alter_column('bio',
               existing_type=mysql.TEXT(),
               comment='个人简介',
               existing_nullable=True)
        batch_op.alter_column('specialty',
               existing_type=mysql.VARCHAR(length=128),
               comment='专业领域，如种植、正畸等',
               existing_nullable=True)
        batch_op.alter_column('title',
               existing_type=mysql.VARCHAR(length=64),
               comment='如主任医师、副主任医师等',
               existing_nullable=True)

    with op.batch_alter_table('consultants', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('specialties',
               existing_type=mysql.VARCHAR(length=256),
               comment='专业领域，逗号分隔',
               existing_nullable=True)
        batch_op.alter_column('bio',
               existing_type=mysql.TEXT(),
               comment='个人简介',
               existing_nullable=True)
        batch_op.alter_column('certification',
               existing_type=mysql.TEXT(),
               comment='JSON存储认证信息',
               existing_nullable=True)
        batch_op.alter_column('type',
               existing_type=mysql.VARCHAR(length=20),
               comment='fulltime 或 parttime',
               existing_nullable=True)
        batch_op.alter_column('user_id',
               existing_type=mysql.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
