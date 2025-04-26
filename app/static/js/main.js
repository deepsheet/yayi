// 全局初始化
document.addEventListener('DOMContentLoaded', function() {
    // 按需激活功能模块
    const currentPath = window.location.pathname;
    
    // 激活所有Bootstrap工具提示
    if (document.querySelectorAll('[data-bs-toggle="tooltip"]').length > 0) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // 设置Alert自动关闭
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(function() {
            alerts.forEach(alert => {
                const closeBtn = alert.querySelector('.btn-close');
                if (closeBtn) closeBtn.click();
            });
        }, 5000);
    }
    
    // 初始化日期选择器（只在需要时）
    if (document.querySelector('.datepicker') && typeof flatpickr !== 'undefined') {
        flatpickr(".datepicker", {
            dateFormat: "Y-m-d",
            locale: "zh"
        });
    }
    
    // 初始化地图（只在联系我们页面）
    if (currentPath.includes('/contact')) {
        initMap();
    }
    
    // 初始化聊天功能（只在相关页面）
    if (document.getElementById('chat-container')) {
        chatModule.init();
    }
    
    // 初始化AI助手（只在相关页面）
    if (document.getElementById('ai-suggest-button')) {
        aiAssistant.init();
    }
    
    // 初始化客户管理（只在相关页面）
    if (document.getElementById('client-table')) {
        clientManager.init();
    }
});

// 地图初始化函数
function initMap() {
    const mapContainer = document.getElementById('map-container');
    if (!mapContainer) return;
    
    // 使用惰性加载方式，只在需要时加载地图
    // 这里改为使用延迟加载iframe
    const mapFrame = document.createElement('iframe');
    mapFrame.src = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3411.0342133479027!2d121.59676287631716!3d31.202280563562196!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x35b270f2beca3399%3A0xf128312e89649b91!2z5byg5rGH6auY56eR5oqA5Zut!5e0!3m2!1szh-CN!2scn!4v1714190304037!5m2!1szh-CN!2scn";
    mapFrame.style.border = "0";
    mapFrame.allowfullscreen = true;
    mapFrame.loading = "lazy";
    mapFrame.referrerpolicy = "no-referrer-when-downgrade";
    mapFrame.className = "w-100 h-100";
    
    // 清空容器并添加iframe
    mapContainer.innerHTML = '';
    mapContainer.appendChild(mapFrame);
}

// 聊天相关功能
const chatModule = {
    init: function() {
        const chatContainer = document.getElementById('chat-container');
        if (!chatContainer) return;
        
        this.msgInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-button');
        this.chatHistory = document.getElementById('chat-history');
        
        if (!this.msgInput || !this.sendBtn || !this.chatHistory) return;
        
        // 绑定事件
        this.sendBtn.addEventListener('click', this.sendMessage.bind(this));
        this.msgInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        }.bind(this));
        
        // 初始化时滚动到底部
        this.scrollToBottom();
    },
    
    sendMessage: function() {
        const content = this.msgInput.value.trim();
        if (!content) return;
        
        const clientId = this.sendBtn.getAttribute('data-client-id');
        if (!clientId) return;
        
        // 添加临时消息
        this.addMessage({
            content: content,
            is_self: true,
            time: new Date().toLocaleString(),
            id: 'temp-' + Date.now()
        });
        
        // 清空输入框
        this.msgInput.value = '';
        this.scrollToBottom();
        
        // 发送请求
        fetch('/consultant/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content,
                client_id: clientId,
                msg_type: 'text'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 移除临时消息并添加实际消息
                document.getElementById('temp-' + Date.now())?.remove();
                this.addMessage(data.message);
            } else {
                alert('消息发送失败: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('发送失败，请稍后重试');
        });
    },
    
    addMessage: function(message) {
        const msgDiv = document.createElement('div');
        msgDiv.id = message.id;
        msgDiv.className = `chat-message ${message.is_self ? 'self' : 'other'}`;
        
        const msgContent = document.createElement('div');
        msgContent.className = 'message-content';
        msgContent.textContent = message.content;
        
        const msgTime = document.createElement('small');
        msgTime.className = 'text-muted d-block mt-1';
        msgTime.textContent = message.time;
        
        msgDiv.appendChild(msgContent);
        msgDiv.appendChild(msgTime);
        this.chatHistory.appendChild(msgDiv);
        
        this.scrollToBottom();
    },
    
    scrollToBottom: function() {
        if (this.chatHistory) {
            this.chatHistory.scrollTop = this.chatHistory.scrollHeight;
        }
    },
    
    loadChatHistory: function(history) {
        if (!history || !this.chatHistory) return;
        
        // 清空历史记录
        this.chatHistory.innerHTML = '';
        
        // 添加消息
        history.forEach(this.addMessage.bind(this));
    }
};

// AI助手功能
const aiAssistant = {
    init: function() {
        const askButton = document.getElementById('ai-suggest-button');
        if (!askButton) return;
        
        const questionInput = document.getElementById('question-input');
        const answerDisplay = document.getElementById('ai-answer');
        
        if (!questionInput || !answerDisplay) return;
        
        askButton.addEventListener('click', function() {
            const question = questionInput.value.trim();
            if (!question) return;
            
            // 显示加载状态
            answerDisplay.innerHTML = '<div class="spinner"></div>';
            
            // 发送请求
            fetch('/consultant/ai_suggest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    answerDisplay.textContent = data.answer;
                } else {
                    answerDisplay.textContent = '无法获取回答，请稍后重试';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                answerDisplay.textContent = '发生错误，请稍后重试';
            });
        });
    }
};

// 客户管理功能
const clientManager = {
    init: function() {
        const clientTable = document.getElementById('client-table');
        if (!clientTable) return;
        
        // 初始化表格搜索和排序
        if (typeof $.fn !== 'undefined' && typeof $.fn.DataTable !== 'undefined') {
            $(clientTable).DataTable({
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/Chinese.json'
                }
            });
        }
        
        // 客户标签管理
        const tagButtons = document.querySelectorAll('.client-tag-btn');
        tagButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const clientId = this.getAttribute('data-client-id');
                const tag = this.getAttribute('data-tag');
                this.classList.toggle('active');
                
                // 更新客户标签
                clientManager.updateClientTag(clientId, tag, this.classList.contains('active'));
            });
        });
    },
    
    updateClientTag: function(clientId, tag, isAdding) {
        fetch(`/consultant/clients/${clientId}/tags`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tag: tag,
                add: isAdding
            })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert('标签更新失败');
                // 还原按钮状态
                const btn = document.querySelector(`.client-tag-btn[data-client-id="${clientId}"][data-tag="${tag}"]`);
                if (btn) {
                    btn.classList.toggle('active');
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}; 