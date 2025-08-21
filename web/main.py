import asyncio
import json
import datetime
import sys
import io
import os
from collections import deque
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from cli.models import AnalystType
from tradingagents.config import get_config

# 创建FastAPI应用
app = FastAPI(
    title="TradingAgents Web",
    description="TradingAgents Web界面 - 多智能体LLM金融交易框架",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建静态文件目录
static_dir = Path("web/static")
static_dir.mkdir(parents=True, exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 存储WebSocket连接
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Pydantic模型
class AnalysisRequest(BaseModel):
    ticker: str
    analysis_date: str
    analysts: List[str]
    research_depth: int

class AnalysisResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

# 消息缓冲区
class WebMessageBuffer:
    def __init__(self, max_length=100):
        self.messages = deque(maxlen=max_length)
        self.tool_calls = deque(maxlen=max_length)
        self.current_report = None
        self.final_report = None
        self.agent_status = {
            "Market Analyst": "pending",
            "Macro Data Analyst": "pending",
            "News Analyst": "pending",
            "Fundamentals Analyst": "pending",
            "Bull Researcher": "pending",
            "Bear Researcher": "pending",
            "Research Manager": "pending",
            "Trader": "pending",
            "Risky Analyst": "pending",
            "Neutral Analyst": "pending",
            "Safe Analyst": "pending",
            "Portfolio Manager": "pending",
        }
        self.current_agent = None
        self.report_sections = {
            "market_report": None,
            "macro_report": None,
            "news_report": None,
            "fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None,
        }

    def add_message(self, message_type: str, content: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.messages.append((timestamp, message_type, content))

    def add_tool_call(self, tool_name: str, args: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.tool_calls.append((timestamp, tool_name, args))

    def update_agent_status(self, agent: str, status: str):
        if agent in self.agent_status:
            self.agent_status[agent] = status
            self.current_agent = agent

    def update_report_section(self, section_name: str, content: str):
        if section_name in self.report_sections:
            self.report_sections[section_name] = content
            self._update_current_report()

    def _update_current_report(self):
        latest_section = None
        latest_content = None

        for section, content in self.report_sections.items():
            if content is not None:
                latest_section = section
                latest_content = content

        if latest_section and latest_content:
            section_titles = {
                "market_report": "Market Analysis",
                "macro_report": "Macro Data Analysis",
                "news_report": "News Analysis",
                "fundamentals_report": "Fundamentals Analysis",
                "investment_plan": "Research Team Decision",
                "trader_investment_plan": "Trading Team Plan",
                "final_trade_decision": "Portfolio Management Decision",
            }
            self.current_report = (
                f"### {section_titles[latest_section]}\n{latest_content}"
            )

        self._update_final_report()

    def _update_final_report(self):
        report_parts = []

        if any(
            self.report_sections[section]
            for section in [
                "market_report",
                "macro_report",
                "history_report",
                "news_report",
                "fundamentals_report",
            ]
        ):
            report_parts.append("## Analyst Team Reports")
            if self.report_sections["market_report"]:
                report_parts.append(
                    f"### Market Analysis\n{self.report_sections['market_report']}"
                )
            if self.report_sections["macro_report"]:
                report_parts.append(
                    f"### Macro Data Analysis\n"
                    f"{self.report_sections['macro_report']}"
                )
            if self.report_sections["news_report"]:
                report_parts.append(
                    f"### News Analysis\n{self.report_sections['news_report']}"
                )
            if self.report_sections["fundamentals_report"]:
                report_parts.append(
                    f"### Fundamentals Analysis\n"
                    f"{self.report_sections['fundamentals_report']}"
                )

        if self.report_sections["investment_plan"]:
            report_parts.append("## Research Team Decision")
            report_parts.append(f"{self.report_sections['investment_plan']}")

        if self.report_sections["trader_investment_plan"]:
            report_parts.append("## Trading Team Plan")
            report_parts.append(f"{self.report_sections['trader_investment_plan']}")

        if self.report_sections["final_trade_decision"]:
            report_parts.append("## Portfolio Management Decision")
            report_parts.append(f"{self.report_sections['final_trade_decision']}")

        self.final_report = "\n\n".join(report_parts) if report_parts else None

    def get_status_update(self):
        return {
            "agent_status": dict(self.agent_status),
            "current_agent": self.current_agent,
            "messages": list(self.messages),
            "tool_calls": list(self.tool_calls),
            "current_report": self.current_report,
            "final_report": self.final_report,
        }

# 自定义控制台类，用于捕获输出并通过WebSocket发送
class WebSocketConsole:
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.buffer = io.StringIO()
        
    async def write_async(self, text: str):
        """异步写入文本到WebSocket"""
        try:
            await self.manager.broadcast(json.dumps({
                "type": "console_output",
                "data": {
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                    "content": text.strip()
                }
            }))
        except Exception as e:
            print(f"WebSocket发送失败: {e}")
    
    def write(self, text: str):
        """同步写入方法，用于重定向stdout"""
        # 写入到原始stdout
        self.original_stdout.write(text)
        self.original_stdout.flush()
        
        # 异步发送到WebSocket
        if text.strip():
            asyncio.create_task(self.write_async(text))
    
    def flush(self):
        """刷新缓冲区"""
        self.original_stdout.flush()
    
    def start_capture(self):
        """开始捕获输出"""
        sys.stdout = self
        sys.stderr = self
    
    def stop_capture(self):
        """停止捕获输出"""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

# 全局消息缓冲区
web_message_buffer = WebMessageBuffer()

# 全局控制台实例
web_console = None

# 路由
@app.get("/", response_class=HTMLResponse)
async def get_home():
    """返回主页HTML"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TradingAgents Web</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .card { border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
            .status-pending { color: #ffc107; }
            .status-in_progress { color: #007bff; }
            .status-completed { color: #28a745; }
            .status-error { color: #dc3545; }
            .message-container { height: 400px; overflow-y: auto; }
            .report-container { height: 500px; overflow-y: auto; }
            .agent-card { transition: all 0.3s ease; }
            .agent-card:hover { transform: translateY(-2px); }
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <div class="col-12">
                    <div class="card mt-3">
                        <div class="card-header bg-primary text-white">
                            <h3 class="mb-0">
                                <i class="fas fa-chart-line me-2"></i>
                                TradingAgents Web - 多智能体LLM金融交易框架
                            </h3>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4">
                                    <div class="card">
                                        <div class="card-header">
                                            <h5><i class="fas fa-cog me-2"></i>分析配置</h5>
                                        </div>
                                        <div class="card-body">
                                            <form id="analysisForm">
                                                <div class="mb-3">
                                                    <label for="ticker" class="form-label">股票代码</label>
                                                    <input type="text" class="form-control" id="ticker" value="SPY" required>
                                                </div>
                                                <div class="mb-3">
                                                    <label for="analysisDate" class="form-label">分析日期</label>
                                                    <input type="date" class="form-control" id="analysisDate" required>
                                                </div>
                                                <div class="mb-3">
                                                    <label class="form-label">分析师团队</label>
                                                    <div class="form-check">
                                                        <input class="form-check-input" type="checkbox" id="marketAnalyst" checked>
                                                        <label class="form-check-label" for="marketAnalyst">市场分析师</label>
                                                    </div>
                                                    <div class="form-check">
                                                        <input class="form-check-input" type="checkbox" id="macroDataAnalyst" checked>
                                                        <label class="form-check-label" for="macroDataAnalyst">宏观数据分析师</label>
                                                    </div>
                                                    <div class="form-check">
                                                        <input class="form-check-input" type="checkbox" id="newsAnalyst" checked>
                                                        <label class="form-check-label" for="newsAnalyst">新闻分析师</label>
                                                    </div>
                                                    <div class="form-check">
                                                        <input class="form-check-input" type="checkbox" id="fundamentalsAnalyst" checked>
                                                        <label class="form-check-label" for="fundamentalsAnalyst">基本面分析师</label>
                                                    </div>
                                                </div>
                                                <div class="mb-3">
                                                    <label for="researchDepth" class="form-label">研究深度</label>
                                                    <select class="form-select" id="researchDepth">
                                                        <option value="1">1: 浅度 - 快速研究</option>
                                                        <option value="3" selected>2: 中度 - 适中辩论</option>
                                                        <option value="5">3: 深度 - 全面研究</option>
                                                    </select>
                                                </div>
                                                <div class="mb-3">
                                                    <div class="alert alert-info">
                                                        <i class="fas fa-info-circle me-2"></i>
                                                        <strong>LLM配置</strong><br>
                                                        <small>LLM提供商、API URL和模型配置将从项目配置系统自动读取</small>
                                                        <div id="llmConfig" class="mt-2">
                                                            <!-- LLM配置信息将在这里显示 -->
                                                        </div>
                                                    </div>
                                                </div>
                                                <button type="submit" class="btn btn-primary w-100" id="startAnalysis">
                                                    <i class="fas fa-play me-2"></i>开始分析
                                                </button>
                                            </form>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-8">
                                    <div class="row">
                                        <div class="col-12">
                                            <div class="card">
                                                <div class="card-header">
                                                    <h5><i class="fas fa-tasks me-2"></i>智能体状态</h5>
                                                </div>
                                                <div class="card-body">
                                                    <div id="agentStatus" class="row">
                                                        <!-- 智能体状态将在这里动态更新 -->
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="row mt-3">
                                        <div class="col-md-6">
                                            <div class="card">
                                                <div class="card-header">
                                                    <h5><i class="fas fa-comments me-2"></i>消息日志</h5>
                                                </div>
                                                <div class="card-body">
                                                    <div id="messageLog" class="message-container">
                                                        <!-- 消息将在这里显示 -->
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="card">
                                                <div class="card-header">
                                                    <h5><i class="fas fa-file-alt me-2"></i>当前报告</h5>
                                                </div>
                                                <div class="card-body">
                                                    <div id="currentReport" class="report-container">
                                                        <!-- 报告将在这里显示 -->
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            let ws = null;
            let isAnalyzing = false;

            // 设置默认日期为今天
            document.getElementById('analysisDate').value = new Date().toISOString().split('T')[0];

            // 加载LLM配置
            loadLLMConfig();

            // 表单提交处理
            document.getElementById('analysisForm').addEventListener('submit', function(e) {
                e.preventDefault();
                if (isAnalyzing) {
                    alert('分析正在进行中，请等待完成...');
                    return;
                }
                startAnalysis();
            });

            function startAnalysis() {
                const formData = {
                    ticker: document.getElementById('ticker').value,
                    analysis_date: document.getElementById('analysisDate').value,
                    analysts: getSelectedAnalysts(),
                    research_depth: parseInt(document.getElementById('researchDepth').value)
                };

                // 发送分析请求
                fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        connectWebSocket();
                        isAnalyzing = true;
                        document.getElementById('startAnalysis').disabled = true;
                        document.getElementById('startAnalysis').innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>分析中...';
                    } else {
                        alert('启动分析失败: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('启动分析时发生错误');
                });
            }

            function getSelectedAnalysts() {
                const analysts = [];
                if (document.getElementById('marketAnalyst').checked) analysts.push('market');
                if (document.getElementById('macroDataAnalyst').checked) analysts.push('macro_data');
                if (document.getElementById('newsAnalyst').checked) analysts.push('news');
                if (document.getElementById('fundamentalsAnalyst').checked) analysts.push('fundamentals');
                return analysts;
            }

            function connectWebSocket() {
                ws = new WebSocket(`ws://${window.location.host}/ws`);
                
                ws.onopen = function(event) {
                    console.log('WebSocket连接已建立');
                };

                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                };

                ws.onclose = function(event) {
                    console.log('WebSocket连接已关闭');
                    isAnalyzing = false;
                    document.getElementById('startAnalysis').disabled = false;
                    document.getElementById('startAnalysis').innerHTML = '<i class="fas fa-play me-2"></i>开始分析';
                };

                ws.onerror = function(error) {
                    console.error('WebSocket错误:', error);
                };
            }

            function handleWebSocketMessage(data) {
                switch(data.type) {
                    case 'status_update':
                        updateAgentStatus(data.data);
                        // 同步更新当前报告（若有）以避免仅依赖 report_update 事件
                        if (data?.data?.current_report) {
                            updateReport({
                                title: '最新报告',
                                content: data.data.current_report
                            });
                        }
                        break;
                    case 'message':
                        addMessage(data.data);
                        break;
                    case 'report_update':
                        updateReport(data.data);
                        break;
                    case 'console_output':
                        addConsoleOutput(data.data);
                        break;
                    case 'analysis_complete':
                        handleAnalysisComplete(data.data);
                        break;
                }
            }

            function updateAgentStatus(statusData) {
                const container = document.getElementById('agentStatus');
                container.innerHTML = '';

                const teams = {
                    'Analyst Team': ['Market Analyst', 'Macro Data Analyst', 'News Analyst', 'Fundamentals Analyst'],
                    'Research Team': ['Bull Researcher', 'Bear Researcher', 'Research Manager'],
                    'Trading Team': ['Trader'],
                    'Risk Management': ['Risky Analyst', 'Neutral Analyst', 'Safe Analyst'],
                    'Portfolio Management': ['Portfolio Manager']
                };

                Object.entries(teams).forEach(([teamName, agents]) => {
                    const teamDiv = document.createElement('div');
                    teamDiv.className = 'col-md-6 mb-3';
                    
                    const teamCard = document.createElement('div');
                    teamCard.className = 'card agent-card';
                    
                    const cardHeader = document.createElement('div');
                    cardHeader.className = 'card-header';
                    cardHeader.innerHTML = `<h6 class="mb-0">${teamName}</h6>`;
                    
                    const cardBody = document.createElement('div');
                    cardBody.className = 'card-body p-2';
                    
                    agents.forEach(agent => {
                        const status = statusData.agent_status[agent] || 'pending';
                        const statusClass = `status-${status}`;
                        const statusIcon = getStatusIcon(status);
                        
                        const agentDiv = document.createElement('div');
                        agentDiv.className = 'd-flex justify-content-between align-items-center mb-1';
                        agentDiv.innerHTML = `
                            <small>${agent}</small>
                            <span class="${statusClass}">${statusIcon} ${status}</span>
                        `;
                        cardBody.appendChild(agentDiv);
                    });
                    
                    teamCard.appendChild(cardHeader);
                    teamCard.appendChild(cardBody);
                    teamDiv.appendChild(teamCard);
                    container.appendChild(teamDiv);
                });
            }

            function getStatusIcon(status) {
                switch(status) {
                    case 'pending': return '<i class="fas fa-clock"></i>';
                    case 'in_progress': return '<i class="fas fa-spinner fa-spin"></i>';
                    case 'completed': return '<i class="fas fa-check"></i>';
                    case 'error': return '<i class="fas fa-exclamation-triangle"></i>';
                    default: return '<i class="fas fa-question"></i>';
                }
            }

            function addMessage(messageData) {
                const container = document.getElementById('messageLog');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'mb-2 p-2 border rounded';
                messageDiv.innerHTML = `
                    <small class="text-muted">${messageData.timestamp}</small>
                    <span class="badge bg-primary ms-2">${messageData.type}</span>
                    <div class="mt-1">${messageData.content}</div>
                `;
                container.appendChild(messageDiv);
                // 只保留最近200条，提升可读性
                while (container.children.length > 200) {
                    container.removeChild(container.firstChild);
                }
                container.scrollTop = container.scrollHeight;
            }

            function updateReport(reportData) {
                const container = document.getElementById('currentReport');
                if (reportData.content) {
                    container.innerHTML = `
                        <div class="mb-2">
                            <h6>${reportData.title}</h6>
                            <div class="border rounded p-3 bg-light">
                                <pre style="white-space: pre-wrap;">${reportData.content}</pre>
                            </div>
                        </div>
                    `;
                }
            }

            function loadLLMConfig() {
                fetch('/api/config')
                    .then(response => response.json())
                    .then(data => {
                        const configDiv = document.getElementById('llmConfig');
                        configDiv.innerHTML = `
                            <div class="small">
                                <strong>当前配置:</strong><br>
                                提供商: ${data.llm_provider || '未设置'}<br>
                                API URL: ${data.backend_url || '未设置'}<br>
                                快速思考模型: ${data.quick_think_llm || '未设置'}<br>
                                深度思考模型: ${data.deep_think_llm || '未设置'}<br>
                                嵌入模型: ${data.embedding_model || '未设置'}<br>
                                嵌入API URL: ${data.embedding_backend_url || '未设置'}
                            </div>
                        `;
                    })
                    .catch(error => {
                        console.error('加载LLM配置失败:', error);
                        const configDiv = document.getElementById('llmConfig');
                        configDiv.innerHTML = '<div class="text-danger small">加载配置失败</div>';
                    });
            }

            function addConsoleOutput(data) {
                const container = document.getElementById('messageLog');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'mb-2 p-2 border rounded bg-light';
                messageDiv.innerHTML = `
                    <small class="text-muted">${data.timestamp}</small>
                    <span class="badge bg-info ms-2">控制台</span>
                    <div class="mt-1 font-monospace small">${data.content}</div>
                `;
                container.appendChild(messageDiv);
                // 只保留最近200条
                while (container.children.length > 200) {
                    container.removeChild(container.firstChild);
                }
                container.scrollTop = container.scrollHeight;
            }

            function handleAnalysisComplete(data) {
                // 完成后如果携带最终/当前报告，兜底渲染一次
                if (data?.final_report) {
                    updateReport({ title: '最终报告', content: data.final_report });
                } else if (data?.current_report) {
                    updateReport({ title: '最新报告', content: data.current_report });
                }
                if (ws) {
                    ws.close();
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/api/config")
async def get_llm_config():
    """获取LLM配置信息"""
    config = get_config()
    return {
        "llm_provider": config.get("llm_provider"),
        "backend_url": config.get("backend_url"),
        "quick_think_llm": config.get("quick_think_llm"),
        "deep_think_llm": config.get("deep_think_llm"),
        "embedding_model": config.get("embedding_model"),
        "embedding_backend_url": config.get("embedding_backend_url"),
    }

@app.post("/api/analyze")
async def start_analysis(request: AnalysisRequest):
    """启动分析任务"""
    try:
        # 验证分析师选择
        if not request.analysts:
            raise HTTPException(status_code=400, detail="至少选择一个分析师")

        # 验证日期格式
        try:
            datetime.datetime.strptime(request.analysis_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式无效，请使用YYYY-MM-DD格式")

        # 重置消息缓冲区
        global web_message_buffer
        web_message_buffer = WebMessageBuffer()

        # 创建配置
        config = get_config().to_dict()
        config["max_debate_rounds"] = request.research_depth
        config["max_risk_discuss_rounds"] = request.research_depth

        # 转换分析师类型
        analyst_types = []
        analyst_mapping = {
            "market": AnalystType.MARKET,
            "macro_data": AnalystType.MACRO_DATA,
            "news": AnalystType.NEWS,
            "fundamentals": AnalystType.FUNDAMENTALS,
        }
        
        for analyst in request.analysts:
            if analyst in analyst_mapping:
                analyst_types.append(analyst_mapping[analyst])

        # 启动异步分析任务
        asyncio.create_task(
            run_web_analysis(
                request.ticker,
                request.analysis_date,
                analyst_types,
                config
            )
        )

        return AnalysisResponse(
            status="success",
            message="分析任务已启动",
            data={
                "ticker": request.ticker,
                "analysis_date": request.analysis_date,
                "analysts": request.analysts
            }
        )

    except Exception as e:
        # 检查是否是MCP初始化失败
        if "MCP服务器初始化失败" in str(e) or "MCP客户端初始化失败" in str(e):
            error_msg = f"MCP初始化失败，无法继续执行: {str(e)}"
            print(error_msg)
            await manager.broadcast(json.dumps({
                "type": "error",
                "data": {
                    "message": error_msg,
                    "details": "请检查MCP服务器配置和网络连接"
                }
            }))
        else:
            # 发送错误消息
            error_msg = f"分析过程中发生错误: {str(e)}"
            print(error_msg)
            await manager.broadcast(json.dumps({
                "type": "error",
                "data": {
                    "message": error_msg
                }
            }))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接处理"""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def run_web_analysis(
    ticker: str,
    analysis_date: str,
    selected_analysts: List[AnalystType],
    config: Dict[str, Any]
):
    """运行Web分析任务"""
    global web_console
    
    try:
        # 创建WebSocket控制台
        web_console = WebSocketConsole(manager)
        web_console.start_capture()
        
        # 创建结果目录（合并日期与时间：yyyy-mm-dd-HH-MM）
        date_time_dir = f"{analysis_date}-{datetime.datetime.now().strftime('%H-%M')}"
        results_dir = (Path(config.get("results_dir", "./results")) / ticker / date_time_dir)
        results_dir.mkdir(parents=True, exist_ok=True)

        # 发送初始状态
        await manager.broadcast(json.dumps({
            "type": "status_update",
            "data": web_message_buffer.get_status_update()
        }))

        # 发送开始消息
        await manager.broadcast(json.dumps({
            "type": "console_output",
            "data": {
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                "content": f"开始分析 {ticker} 在 {analysis_date}..."
            }
        }))

        # 初始化交易代理图
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        
        print(f"初始化交易代理图...")
        graph = TradingAgentsGraph(
            [analyst.value for analyst in selected_analysts],
            config=config,
            debug=True
        )

        # 异步初始化图
        print("异步初始化图...")
        await graph.async_init()

        # 初始化状态和参数
        print("创建初始状态...")
        init_agent_state = graph.propagator.create_initial_state(ticker, analysis_date)
        args = graph.propagator.get_graph_args()

        # 更新agent状态为进行中
        print("更新智能体状态为进行中...")
        for analyst in selected_analysts:
            # 修复智能体名称映射
            agent_name_mapping = {
                "market": "Market Analyst",
                "macro_data": "Macro Data Analyst", 
                "news": "News Analyst",
                "fundamentals": "Fundamentals Analyst"
            }
            agent_name = agent_name_mapping.get(analyst.value, analyst.value.replace("_", " ").title())
            print(f"更新 {agent_name} 状态为 in_progress")
            web_message_buffer.update_agent_status(agent_name, "in_progress")
            await manager.broadcast(json.dumps({
                "type": "status_update",
                "data": web_message_buffer.get_status_update()
            }))

        # 运行分析（使用流式输出）
        print("开始流式分析...")
        final_state, processed_signal = await graph.propagate(ticker, analysis_date, stream_output=True)

        # 更新agent状态为已完成
        print("更新智能体状态为已完成...")
        for analyst in selected_analysts:
            # 修复智能体名称映射
            agent_name_mapping = {
                "market": "Market Analyst",
                "macro_data": "Macro Data Analyst", 
                "news": "News Analyst",
                "fundamentals": "Fundamentals Analyst"
            }
            agent_name = agent_name_mapping.get(analyst.value, analyst.value.replace("_", " ").title())
            print(f"更新 {agent_name} 状态为 completed")
            web_message_buffer.update_agent_status(agent_name, "completed")
            await manager.broadcast(json.dumps({
                "type": "status_update",
                "data": web_message_buffer.get_status_update()
            }))

        # 保存结果并更新报告
        print("分析完成！保存结果...")
        print(f"final_state keys: {list(final_state.keys())}")
        
        # 英文段落键到中文文件名的映射
        chinese_filename_map = {
            "market_report": "市场分析.md",
            "macro_report": "宏观数据分析.md",
            "news_report": "新闻分析.md",
            "fundamentals_report": "基本面分析.md",
            "investment_plan": "研究团队决策.md",
            "trader_investment_plan": "交易团队计划.md",
            "final_trade_decision": "最终交易决策.md",
            "history_analysis_report": "历史分析报告.md",
        }

        for section_name, content in final_state.items():
            if isinstance(content, str) and content.strip():
                # 保存到文件
                file_name = chinese_filename_map.get(section_name, f"{section_name}.md")
                with open(results_dir / file_name, "w", encoding="utf-8") as f:
                    f.write(content)
                
                print(f"保存文件: {file_name}")
                
                # 更新Web界面报告 - 使用实际的文件名映射
                section_mapping = {
                    "market_report": "market_report",
                    "macro_report": "macro_report", 
                    "news_report": "news_report",
                    "fundamentals_report": "fundamentals_report",
                    "investment_plan": "investment_plan",
                    "trader_investment_plan": "trader_investment_plan",
                    "final_trade_decision": "final_trade_decision"
                }
                
                if section_name in section_mapping:
                    print(f"更新报告部分: {section_name} -> {section_mapping[section_name]}")
                    web_message_buffer.update_report_section(section_mapping[section_name], content)
                    await manager.broadcast(json.dumps({
                        "type": "report_update",
                        "data": {
                            "title": section_name.replace("_", " ").title(),
                            "content": content
                        }
                    }))
                else:
                    print(f"未找到映射: {section_name}")

        print(f"报告已保存到 {results_dir}")

        # 根据生成结果补齐其余团队的状态（研究、交易、风控、投资组合）
        try:
            if isinstance(final_state.get("investment_plan"), str) and final_state.get("investment_plan").strip():
                for researcher in ["Bull Researcher", "Bear Researcher", "Research Manager"]:
                    web_message_buffer.update_agent_status(researcher, "completed")
            if isinstance(final_state.get("trader_investment_plan"), str) and final_state.get("trader_investment_plan").strip():
                web_message_buffer.update_agent_status("Trader", "completed")
            if isinstance(final_state.get("final_trade_decision"), str) and final_state.get("final_trade_decision").strip():
                for risk_agent in ["Risky Analyst", "Neutral Analyst", "Safe Analyst"]:
                    web_message_buffer.update_agent_status(risk_agent, "completed")
                web_message_buffer.update_agent_status("Portfolio Manager", "completed")

            await manager.broadcast(json.dumps({
                "type": "status_update",
                "data": web_message_buffer.get_status_update()
            }))
        except Exception as _e:
            # 状态更新失败不应影响主流程
            print(f"补齐团队状态时发生非致命错误: {_e}")

        # 发送完成消息
        await manager.broadcast(json.dumps({
            "type": "analysis_complete",
            "data": {
                "message": "分析完成",
                "results_dir": str(results_dir),
                # 附带最终报告用于前端兜底渲染
                "final_report": web_message_buffer.final_report,
                "current_report": web_message_buffer.current_report
            }
        }))

    except Exception as e:
        # 检查是否是MCP初始化失败
        if "MCP服务器初始化失败" in str(e) or "MCP客户端初始化失败" in str(e):
            error_msg = f"MCP初始化失败，无法继续执行: {str(e)}"
            print(error_msg)
            await manager.broadcast(json.dumps({
                "type": "error",
                "data": {
                    "message": error_msg,
                    "details": "请检查MCP服务器配置和网络连接"
                }
            }))
        else:
            # 发送错误消息
            error_msg = f"分析过程中发生错误: {str(e)}"
            print(error_msg)
            await manager.broadcast(json.dumps({
                "type": "error",
                "data": {
                    "message": error_msg
                }
            }))
    finally:
        # 停止捕获输出
        if web_console:
            web_console.stop_capture()
            web_console = None

@app.get("/api/report")
async def get_current_and_final_report():
    """提供当前与最终报告的简单查询接口，便于前端兜底渲染与测试。"""
    return {
        "current_report": web_message_buffer.current_report,
        "final_report": web_message_buffer.final_report,
        "report_sections": web_message_buffer.report_sections,
        "agent_status": web_message_buffer.agent_status,
    }

# ====== 测试辅助接口（仅在设置 ENABLE_TEST_ENDPOINTS=1 时启用） ======
if os.environ.get("ENABLE_TEST_ENDPOINTS", "1") == "1":
    class TestBroadcastRequest(BaseModel):
        type: str
        data: Dict[str, Any]

    @app.post("/api/test/reset")
    async def test_reset():
        global web_message_buffer
        web_message_buffer = WebMessageBuffer()
        await manager.broadcast(json.dumps({
            "type": "status_update",
            "data": web_message_buffer.get_status_update()
        }))
        return {"status": "ok"}

    @app.post("/api/test/broadcast")
    async def test_broadcast(req: TestBroadcastRequest):
        await manager.broadcast(json.dumps({
            "type": req.type,
            "data": req.data
        }))
        return {"status": "sent"}

if __name__ == "__main__":
    uvicorn.run(
        "web.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
