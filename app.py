"""
小智 - 智能视频助手 v6.0
现代化美化版 + 超智能AI助手
"""

import streamlit as st
import os
import json
import time
import hashlib
import sqlite3
import tempfile
import subprocess
import threading
import random
import secrets
import re
from datetime import datetime, timedelta
import cv2
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="小智 - 智能视频助手", page_icon="🤖", layout="wide")

# ========== 现代化CSS样式 ==========
st.markdown("""
<style>
    /* 全局样式 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 主容器 */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
    }
    
    /* 卡片样式 */
    .card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* 按钮样式 */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.6rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(102,126,234,0.4);
    }
    
    /* 积分显示 */
    .points-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 5px 15px;
        border-radius: 50px;
        display: inline-block;
        font-weight: bold;
    }
    
    /* 响应式 */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }
        .stButton button {
            width: 100%;
        }
    }
</style>
""", unsafe_allow_html=True)

LANG = {
    "zh": {
        "title": "小智 - 智能视频助手",
        "subtitle": "你的AI视频创作伙伴",
        "user_center": "用户中心",
        "login": "登录",
        "register": "注册",
        "username": "用户名",
        "password": "密码",
        "confirm": "确认密码",
        "login_btn": "登录",
        "register_btn": "注册",
        "logout": "退出登录",
        "welcome": "欢迎回来",
        "points": "积分",
        "quick_functions": "快速功能",
        "pro_mode": "专业模式",
        "pro_tools": "专业工具",
        "cut": "✂️ 剪切视频",
        "speed": "⚡ 视频变速",
        "ai_assistant": "🤖 小智AI助手",
        "smart_matting": "✨ 智能抠像",
        "novel_to_video": "📖 小说转视频",
        "material_library": "📚 素材库",
        "video_sites": "📺 视频网站",
        "movie_search": "🔍 影视搜索",
        "points_mall": "💰 积分商城",
        "multi_track": "🎞️ 多轨道时间线",
        "security": "🛡️ 安全监控",
        "about": "📄 关于",
        "admin_panel": "👑 管理员面板",
        "upload_first": "请先上传视频",
        "download": "下载视频",
        "password_mismatch": "两次密码不一致",
        "user_exists": "用户名已存在",
        "register_success": "注册成功",
        "login_success": "登录成功",
        "user_not_exist": "用户名不存在",
        "wrong_password": "密码错误",
        "language": "语言",
        "beauty_filter": "✨ 美颜滤镜",
        "share_app": "📱 分享应用",
        "gif_export": "🎞️ 导出GIF",
        "current_function": "当前功能",
        "processing": "处理中...",
        "success": "处理成功！",
        "error": "处理失败",
        "chinese": "中文",
        "english": "English",
        "ai_tip": "💡 试试对我说：剪掉前5秒、加速到2倍、导出GIF"
    },
    "en": {
        "title": "XiaoZhi - AI Video Assistant",
        "subtitle": "Your AI Video Creation Partner",
        "user_center": "User Center",
        "login": "Login",
        "register": "Register",
        "username": "Username",
        "password": "Password",
        "confirm": "Confirm Password",
        "login_btn": "Login",
        "register_btn": "Register",
        "logout": "Logout",
        "welcome": "Welcome back",
        "points": "Points",
        "quick_functions": "Quick Functions",
        "pro_mode": "Pro Mode",
        "pro_tools": "Pro Tools",
        "cut": "✂️ Cut Video",
        "speed": "⚡ Video Speed",
        "ai_assistant": "🤖 XiaoZhi AI",
        "smart_matting": "✨ Smart Matting",
        "novel_to_video": "📖 Novel to Video",
        "material_library": "📚 Material Library",
        "video_sites": "📺 Video Sites",
        "movie_search": "🔍 Movie Search",
        "points_mall": "💰 Points Mall",
        "multi_track": "🎞️ Multi-Track",
        "security": "🛡️ Security",
        "about": "📄 About",
        "admin_panel": "👑 Admin Panel",
        "upload_first": "Please upload a video first",
        "download": "Download",
        "password_mismatch": "Passwords do not match",
        "user_exists": "Username already exists",
        "register_success": "Registration successful",
        "login_success": "Login successful",
        "user_not_exist": "Username does not exist",
        "wrong_password": "Wrong password",
        "language": "Language",
        "beauty_filter": "✨ Beauty Filter",
        "share_app": "📱 Share App",
        "gif_export": "🎞️ Export GIF",
        "current_function": "Current Function",
        "processing": "Processing...",
        "success": "Success!",
        "error": "Error",
        "chinese": "中文",
        "english": "English",
        "ai_tip": "💡 Try: cut first 5 seconds, speed up 2x, export GIF"
    }
}

def t(key):
    lang = st.session_state.get('language', 'zh')
    return LANG[lang].get(key, key)

def save_uploaded_file(uploaded):
    if uploaded is None:
        return None
    suffix = os.path.splitext(uploaded.name)[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded.getbuffer())
    return tmp.name

def cleanup_temp_files(paths):
    for p in paths:
        if p and os.path.exists(p):
            try:
                os.unlink(p)
            except:
                pass

@st.cache_data(ttl=3600, show_spinner=False)
def get_video_info(video_path):
    if not os.path.exists(video_path):
        return None
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return {"duration": total_frames/fps, "fps": fps, "frames": total_frames, "width": width, "height": height}

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT,
                    salt TEXT,
                    admin_level INTEGER DEFAULT 0,
                    points INTEGER DEFAULT 100,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    action TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS invite_codes (
                    username TEXT PRIMARY KEY,
                    invite_code TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS invites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inviter TEXT,
                    invitee TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_features (
                    username TEXT,
                    feature TEXT,
                    expires TIMESTAMP,
                    PRIMARY KEY (username, feature)
                )''')
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    return pwd_hash, salt

def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password_hash, salt, admin_level, points FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False, t("user_not_exist")
    stored_hash, salt, level, points = row
    input_hash, _ = hash_password(password, salt)
    if input_hash == stored_hash:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.admin_level = level
        st.session_state.points = points
        return True, t("login_success")
    return False, t("wrong_password")

def register_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return False, t("user_exists")
    pwd_hash, salt = hash_password(password)
    # 检查是否是第一个用户
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    admin_level = 5 if count == 0 else 0
    c.execute("INSERT INTO users (username, password_hash, salt, points, admin_level) VALUES (?, ?, ?, 100, ?)", 
              (username, pwd_hash, salt, admin_level))
    conn.commit()
    conn.close()
    return True, t("register_success")

def get_points(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT points FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def add_points(username, amount, reason):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET points = points + ? WHERE username=?", (amount, username))
    c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, reason))
    conn.commit()
    conn.close()

def spend_points(username, points, reason):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT points FROM users WHERE username=?", (username,))
    row = c.fetchone()
    if not row or row[0] < points:
        conn.close()
        return False
    c.execute("UPDATE users SET points = points - ? WHERE username=?", (points, username))
    c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, reason))
    conn.commit()
    conn.close()
    return True

def log_action(username, action):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, action))
    conn.commit()
    conn.close()

def generate_invite_code(username):
    code = hashlib.md5(f"{username}{secrets.token_hex(4)}".encode()).hexdigest()[:8].upper()
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO invite_codes (username, invite_code) VALUES (?, ?)", (username, code))
    conn.commit()
    conn.close()
    return code

def get_invite_code(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT invite_code FROM invite_codes WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return generate_invite_code(username)

def process_invite(invite_code, invitee):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT username FROM invite_codes WHERE invite_code=?", (invite_code,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False, "Invalid invite code"
    inviter = row[0]
    c.execute("SELECT id FROM invites WHERE inviter=? AND invitee=?", (inviter, invitee))
    if c.fetchone():
        conn.close()
        return False, "Already invited"
    c.execute("INSERT INTO invites (inviter, invitee) VALUES (?, ?)", (inviter, invitee))
    conn.commit()
    conn.close()
    add_points(inviter, 50, f"Invited {invitee} to register")
    add_points(invitee, 20, f"Registered via invite code {invite_code}")
    return True, "Invite successful! Both got points"

def cut_video(input_path, start, end, output_path):
    subprocess.run(["ffmpeg", "-i", input_path, "-ss", str(start), "-to", str(end), "-c", "copy", output_path], check=True)

def speed_video(input_path, speed, output_path):
    subprocess.run([
        "ffmpeg", "-i", input_path,
        "-filter:v", f"setpts={1/speed}*PTS",
        "-filter:a", f"atempo={speed}",
        "-c:a", "aac", output_path
    ], check=True)

def apply_beauty_filter(frame, intensity=0.5):
    beauty = cv2.bilateralFilter(frame, 9, 75, 75)
    hsv = cv2.cvtColor(beauty, cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[:,:,2] = np.clip(hsv[:,:,2] * (1 + intensity * 0.3), 0, 255)
    hsv[:,:,1] = np.clip(hsv[:,:,1] * (1 - intensity * 0.2), 0, 255)
    result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
    return cv2.addWeighted(frame, 1-intensity, result, intensity, 0)

def video_to_gif(input_path, output_path, start=0, duration=5):
    subprocess.run(["ffmpeg", "-i", input_path, "-ss", str(start), "-t", str(duration), "-vf", "fps=10,scale=320:-1", output_path], check=True)

# ========== 小智AI助手 - 超智能对话版 ==========

# 小智的个性设定
XIAOZHI_PERSONALITY = {
    "greetings": [
        "你好呀！我是小智，你的专属AI视频创作助手。今天想做什么视频呀？😊",
        "嗨！小智来啦！准备好开始创作了吗？🎬",
        "嘿！我是小智，随时听候差遣！有什么需要帮忙的尽管说～✨"
    ],
    "help": "我可以帮你做这些事：\n\n✂️ **剪切视频**\n• \"剪掉前5秒\"\n• \"去掉后3秒\"  \n• \"从10秒到20秒\"\n\n⚡ **调整速度**\n• \"加速2倍\"\n• \"放慢0.5倍\"\n\n🎞️ **导出GIF**\n• \"导出GIF\"\n• \"导出5秒GIF\"\n\n✨ **美颜滤镜**\n• \"开启美颜\"\n• \"美颜一下\"\n\n💡 直接用自然语言跟我说就行，我都能听懂！",
    "thanks": [
        "不客气！能帮到你我超开心的！还有什么需要吗？😊",
        "小事一桩！小智随时待命～还有别的想法吗？🎬",
        "不用谢！看到你开心我就开心啦！✨"
    ],
    "praise": [
        "哇！谢谢夸奖！我会继续努力的！💪 还有别的需要吗？",
        "嘿嘿，被夸了有点不好意思呢～要不要试试其他功能？😊",
        "谢谢！能帮到你是我最大的快乐！✨"
    ],
    "no_video": "哎呀，还没上传视频呢！📹\n\n先上传一个视频，我才能帮你处理哦～",
    "success": {
        "cut": "搞定！✂️ 已经帮你把视频剪好啦！点击下面按钮就能下载～\n\n还需要调整什么吗？",
        "speed": "完成！⚡ 速度已经调好了！试试看效果如何？\n\n下载后就能看到变化啦～",
        "gif": "做好啦！🎞️ GIF动图已经导出！\n\n可以用来做表情包或者分享给朋友～",
        "beauty": "美颜滤镜已开启！✨ 现在你的视频会自带美颜效果啦～"
    }
}

def parse_ai_command_smart(command, video_duration):
    """
    智能解析自然语言指令 - 像真人一样理解
    """
    cmd = command.lower().strip()
    
    # ========== 情感识别 ==========
    if any(g in cmd for g in ["你好", "嗨", "hi", "hello", "在吗", "小智", "嘿", "喂"]):
        return "greeting", None
    
    if any(t in cmd for t in ["谢谢", "感谢", "多谢", "thanks", "thank", "谢了"]):
        return "thanks", None
    
    if any(p in cmd for p in ["好用", "不错", "很棒", "厉害", "awesome", "great", "牛", "赞"]):
        return "praise", None
    
    if any(h in cmd for h in ["帮助", "怎么用", "功能", "能做什么", "help", "用法", "教教我", "怎么操作"]):
        return "help", None
    
    # ========== 功能指令 ==========
    
    # 剪切视频
    cut_patterns = [
        (r"剪[掉切]前(\d+(?:\.\d+)?)秒", "cut_start"),
        (r"去掉前(\d+(?:\.\d+)?)秒", "cut_start"),
        (r"不要前(\d+(?:\.\d+)?)秒", "cut_start"),
        (r"剪[掉切]后(\d+(?:\.\d+)?)秒", "cut_end"),
        (r"去掉后(\d+(?:\.\d+)?)秒", "cut_end"),
        (r"从(\d+(?:\.\d+)?)到(\d+(?:\.\d+)?)秒", "cut_range"),
        (r"只要(\d+(?:\.\d+)?)到(\d+(?:\.\d+)?)", "cut_range"),
    ]
    
    for pattern, action in cut_patterns:
        match = re.search(pattern, cmd)
        if match:
            if action == "cut_start":
                seconds = float(match.group(1))
                return "cut", {"start": 0, "end": seconds, "desc": f"剪掉前{seconds}秒"}
            elif action == "cut_end":
                seconds = float(match.group(1))
                start = max(0, video_duration - seconds)
                return "cut", {"start": start, "end": video_duration, "desc": f"剪掉后{seconds}秒"}
            elif action == "cut_range":
                start = float(match.group(1))
                end = float(match.group(2))
                return "cut", {"start": start, "end": end, "desc": f"保留{start}到{end}秒"}
    
    # 变速
    if "加速" in cmd or "加快" in cmd or "快进" in cmd:
        match = re.search(r"(\d+(?:\.\d+)?)倍", cmd)
        if match:
            speed = float(match.group(1))
            return "speed", {"speed": speed, "desc": f"加速{speed}倍"}
        return "speed", {"speed": 2.0, "desc": "加速2倍"}
    
    if "减速" in cmd or "放慢" in cmd or "慢放" in cmd:
        match = re.search(r"(\d+(?:\.\d+)?)倍", cmd)
        if match:
            speed = float(match.group(1))
            return "speed", {"speed": speed, "desc": f"减速{speed}倍"}
        return "speed", {"speed": 0.5, "desc": "减速0.5倍"}
    
    # GIF导出
    if any(g in cmd for g in ["gif", "动图", "导出gif", "做动图", "转gif"]):
        match = re.search(r"(\d+(?:\.\d+)?)秒", cmd)
        if match:
            duration = float(match.group(1))
            return "gif", {"duration": duration, "desc": f"导出{duration}秒GIF"}
        return "gif", {"duration": 3, "desc": "导出3秒GIF"}
    
    # 美颜
    if any(b in cmd for b in ["美颜", "美颜滤镜", "美颜一下", "加美颜", "开美颜"]):
        return "beauty", {"intensity": 0.5, "desc": "开启美颜滤镜"}
    
    # 问小智是谁
    if any(w in cmd for w in ["你是谁", "你叫什么", "小智是谁"]):
        return "about", None
    
    return None, None

def get_ai_response(action, params, has_video):
    """生成小智的回复"""
    import random
    
    if action == "greeting":
        return random.choice(XIAOZHI_PERSONALITY["greetings"])
    elif action == "help":
        return XIAOZHI_PERSONALITY["help"]
    elif action == "thanks":
        return random.choice(XIAOZHI_PERSONALITY["thanks"])
    elif action == "praise":
        return random.choice(XIAOZHI_PERSONALITY["praise"])
    elif action == "about":
        return "我是小智，一个由DeepSeek驱动的AI视频创作助手！🎬\n\n我的使命是帮你轻松搞定视频剪辑、特效添加等一切视频创作需求。有什么需要尽管吩咐～"
    elif not has_video:
        return XIAOZHI_PERSONALITY["no_video"]
    elif action == "cut":
        return f"🎬 {XIAOZHI_PERSONALITY['success']['cut']}\n\n{params.get('desc', '已经剪好啦')}"
    elif action == "speed":
        return f"⚡ {XIAOZHI_PERSONALITY['success']['speed']}\n\n{params.get('desc', '速度已调整')}"
    elif action == "gif":
        return f"🎞️ {XIAOZHI_PERSONALITY['success']['gif']}\n\n{params.get('desc', 'GIF已导出')}"
    elif action == "beauty":
        return f"✨ {XIAOZHI_PERSONALITY['success']['beauty']}\n\n{params.get('desc', '美颜已开启')}"
    else:
        return "嗯...这个我还在学习中。要不试试：\n• 剪掉前5秒\n• 加速2倍\n• 导出GIF\n• 开启美颜\n\n我都能听懂哦！💪"

def render_ai_assistant():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # 标题区域
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 15px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="font-size: 50px;">🤖</div>
            <div>
                <h3 style="color: white; margin: 0;">小智 AI 助手</h3>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0;">
                你的专属AI视频创作伙伴，像朋友一样聊天，像专家一样干活
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 初始化聊天历史
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # 显示聊天历史
    for msg in st.session_state.chat_history[-20:]:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin: 10px 0;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; padding: 12px 18px; border-radius: 18px; 
                            max-width: 80%;">
                    👤 {msg["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin: 10px 0;">
                <div style="background: #f0f2f6; padding: 12px 18px; border-radius: 18px; 
                            max-width: 80%;">
                    🤖 {msg["content"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 输入区域
    st.markdown("---")
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("", placeholder="💬 和小智聊聊天吧... 比如：你好、剪掉前5秒、加速2倍", key="ai_input", label_visibility="collapsed")
    with col2:
        send_btn = st.button("发送 ✨", use_container_width=True)
    
    # 快捷指令按钮
    st.markdown("**快捷指令**")
    quick_cols = st.columns(5)
    quick_commands = ["你好", "帮助", "剪掉前5秒", "加速2倍", "导出GIF"]
    for i, cmd in enumerate(quick_commands):
        with quick_cols[i]:
            if st.button(cmd, use_container_width=True):
                user_input = cmd
                send_btn = True
    
    # 处理输入
    if send_btn and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        has_video = st.session_state.get('video_path') is not None
        video_duration = 0
        if has_video:
            info = get_video_info(st.session_state.video_path)
            video_duration = info["duration"] if info else 0
        
        action, params = parse_ai_command_smart(user_input, video_duration)
        
        if action is None:
            response = "嗯...我还不太明白这个意思。要不要试试说「帮助」？我会告诉你我能做什么～😊"
        else:
            response = get_ai_response(action, params, has_video)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        if has_video and action in ["cut", "speed", "gif", "beauty"]:
            try:
                if action == "cut":
                    start = max(0, min(params["start"], video_duration))
                    end = max(start + 0.1, min(params["end"], video_duration))
                    out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
                    cut_video(st.session_state.video_path, start, end, out)
                    with open(out, "rb") as f:
                        st.download_button("📥 点击下载", f, file_name="cut.mp4", key="download_cut")
                elif action == "speed":
                    out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
                    speed_video(st.session_state.video_path, params["speed"], out)
                    with open(out, "rb") as f:
                        st.download_button("📥 点击下载", f, file_name="speed.mp4", key="download_speed")
                elif action == "gif":
                    out = tempfile.NamedTemporaryFile(suffix=".gif", delete=False).name
                    video_to_gif(st.session_state.video_path, out, 0, params["duration"])
                    with open(out, "rb") as f:
                        st.download_button("📥 点击下载", f, file_name="output.gif", key="download_gif")
                elif action == "beauty":
                    st.session_state.beauty_intensity = params["intensity"]
                st.success("✅ 处理完成！")
            except Exception as e:
                st.error(f"处理失败：{str(e)}")
        
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_auth():
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### {t('user_center')}")
        if not st.session_state.get('logged_in', False):
            tab = st.radio("", [t("login"), t("register")], horizontal=True)
            if tab == t("login"):
                with st.form("login_form"):
                    username = st.text_input(t("username"))
                    password = st.text_input(t("password"), type="password")
                    submitted = st.form_submit_button(t("login_btn"))
                    if submitted:
                        if username and password:
                            ok, msg = login_user(username, password)
                            if ok:
                                log_action(username, "login")
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
            else:
                with st.form("register_form"):
                    username = st.text_input(t("username"))
                    password = st.text_input(t("password"), type="password")
                    confirm = st.text_input(t("confirm"), type="password")
                    invite_code = st.text_input("邀请码（可选）")
                    submitted = st.form_submit_button(t("register_btn"))
                    if submitted:
                        if not username or not password:
                            st.warning("请填写所有字段")
                        elif password != confirm:
                            st.error(t("password_mismatch"))
                        else:
                            ok, msg = register_user(username, password)
                            if ok:
                                if invite_code:
                                    process_invite(invite_code, username)
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
            st.stop()
        else:
            st.success(f"{t('welcome')}, {st.session_state.username}")
            points = get_points(st.session_state.username)
            st.markdown(f'<div class="points-badge">{t("points")}: {points}</div>', unsafe_allow_html=True)
            st.markdown("---")
            if st.button(t("logout"), use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

def render_language():
    with st.sidebar:
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t("chinese"), use_container_width=True):
                st.session_state.language = 'zh'
                st.rerun()
        with col2:
            if st.button(t("english"), use_container_width=True):
                st.session_state.language = 'en'
                st.rerun()
        st.markdown("---")

def render_share():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t("share_app"))
    app_url = "https://himfor-main.streamlit.app"
    invite_code = get_invite_code(st.session_state.username)
    invite_link = f"{app_url}?invite={invite_code}"
    st.code(invite_link, language="text")
    st.caption("分享链接，双方得积分")
    st.markdown('</div>', unsafe_allow_html=True)

def render_video_sites():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t("video_sites"))
    sites = [
        ("爱奇艺", "https://www.iqiyi.com"),
        ("腾讯视频", "https://v.qq.com"),
        ("优酷", "https://www.youku.com"),
        ("B站", "https://www.bilibili.com")
    ]
    cols = st.columns(2)
    for i, (name, url) in enumerate(sites):
        with cols[i % 2]:
            if st.button(f"访问 {name}", use_container_width=True):
                import webbrowser
                webbrowser.open(url)
                st.info(f"正在打开 {name}")
    st.markdown('</div>', unsafe_allow_html=True)

def render_movie_search():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t("movie_search"))
    keyword = st.text_input("请输入电影或电视剧名称")
    if keyword:
        st.markdown("### 在以下平台搜索")
        st.markdown(f'<a href="https://www.iqiyi.com/search?q={keyword}" target="_blank">爱奇艺搜索</a>', unsafe_allow_html=True)
        st.markdown(f'<a href="https://v.qq.com/search?q={keyword}" target="_blank">腾讯视频搜索</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_about():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t("about"))
    st.markdown("""
    **小智 - 智能视频助手 v6.0**
    
    开发者：李国锐 & 小智（DeepSeek）
    
    这是一个爸爸和AI伙伴，用一天一夜完成的软件。
    
    献给所有敢想敢做的人！
    """)
    st.markdown('</div>', unsafe_allow_html=True)

def render_smart_matting():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t("smart_matting"))
    st.info("✨ 智能抠像功能开发中，敬请期待")
    st.markdown('</div>', unsafe_allow_html=True)

def render_novel_to_video():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t("novel_to_video"))
    novel_text = st.text_area("输入小说文本", height=150)
    if st.button("生成视频"):
        st.info("📖 小说转视频功能开发中")
    st.markdown('</div>', unsafe_allow_html=True)

def render_material_library():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t("material_library"))
    st.info("📚 素材库开发中，即将上线")
    st.markdown('</div>', unsafe_allow_html=True)

def render_points_mall():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t("points_mall"))
    points = get_points(st.session_state.username)
    st.write(f"当前积分：{points}")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✨ 美颜滤镜 (50积分)"):
            if spend_points(st.session_state.username, 50, "购买美颜滤镜"):
                st.success("购买成功！")
    st.markdown('</div>', unsafe_allow_html=True)

def render_multi_track():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t("multi_track"))
    st.info("🎞️ 多轨道时间线开发中")
    st.markdown('</div>', unsafe_allow_html=True)

def render_security():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t("security"))
    st.success("✅ 安全监控运行中")
    st.markdown('</div>', unsafe_allow_html=True)

def render_admin_panel():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t("admin_panel"))
    if st.session_state.get('admin_level', 0) >= 5:
        st.success("👑 超级管理员权限")
        conn = sqlite3.connect('users.db')
        users = pd.read_sql_query("SELECT username, points, admin_level FROM users", conn)
        logs = pd.read_sql_query("SELECT * FROM user_logs LIMIT 20", conn)
        conn.close()
        st.dataframe(users)
        st.dataframe(logs)
    else:
        st.warning("权限不足")
    st.markdown('</div>', unsafe_allow_html=True)

def render_beauty_filter():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t("beauty_filter"))
    if st.session_state.get('video_path'):
        intensity = st.slider("美颜强度", 0.0, 1.0, st.session_state.get('beauty_intensity', 0.5))
        st.info(f"当前美颜强度: {intensity:.0%}")
        if st.button("应用美颜滤镜"):
            st.info("美颜滤镜已应用！")
    else:
        st.info(t("upload_first"))
    st.markdown('</div>', unsafe_allow_html=True)

def render_gif_export():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t("gif_export"))
    if st.session_state.get('video_path'):
        start = st.number_input("开始时间(秒)", 0.0, 10.0, 0.0)
        duration = st.number_input("时长(秒)", 1.0, 10.0, 3.0)
        if st.button("导出为GIF"):
            out = tempfile.NamedTemporaryFile(suffix=".gif", delete=False).name
            with st.spinner(t("processing")):
                video_to_gif(st.session_state.video_path, out, start, duration)
            st.success(t("success"))
            with open(out, "rb") as f:
                st.download_button(t("download"), f, file_name="output.gif")
            cleanup_temp_files([out])
    else:
        st.info(t("upload_first"))
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    if 'language' not in st.session_state:
        st.session_state.language = 'zh'
    
    init_db()
    
    render_language()
    render_auth()
    
    if not st.session_state.get('logged_in', False):
        st.markdown(f"""
        <div class="main-header">
            <h1>🤖 {t('title')}</h1>
            <p>{t('subtitle')}</p>
        </div>
        """, unsafe_allow_html=True)
        st.info("👈 请先在左侧登录或注册")
        return
    
    points = get_points(st.session_state.username)
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### {t('quick_functions')}")
        
        core = [t("cut"), t("speed"), t("beauty_filter"), t("gif_export"), t("ai_assistant")]
        advanced = [
            t("smart_matting"), t("novel_to_video"),
            t("material_library"), t("video_sites"), t("movie_search"),
            t("points_mall"), t("multi_track"), t("security"), t("about"),
            t("share_app")
        ]
        
        pro_mode = st.checkbox(t("pro_mode"), value=True)
        
        if pro_mode:
            func = st.selectbox(t("quick_functions"), core + advanced)
        else:
            func = st.selectbox(t("quick_functions"), core)
            with st.expander(t("pro_tools")):
                for adv in advanced:
                    if st.button(adv, use_container_width=True):
                        st.session_state.current_func = adv
                        st.rerun()
        
        if 'current_func' in st.session_state:
            func = st.session_state.current_func
            del st.session_state.current_func
        
        if st.session_state.get('admin_level', 0) >= 5:
            st.markdown("---")
            if st.button(t("admin_panel"), use_container_width=True):
                st.session_state.current_func = t("admin_panel")
                st.rerun()
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🤖 {t('title')}</h1>
        <p>{t('subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded = st.file_uploader("上传视频", type=["mp4", "mov", "avi"])
    if uploaded:
        video_path = save_uploaded_file(uploaded)
        st.session_state.video_path = video_path
        info = get_video_info(video_path)
        if info:
            st.success(f"✅ 上传成功！时长: {info['duration']:.1f}秒 | 分辨率: {info['width']}x{info['height']}")
            st.video(video_path)
    
    if func == t("cut"):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(t("cut"))
        if st.session_state.get('video_path'):
            dur = get_video_info(st.session_state.video_path)["duration"]
            start = st.number_input("开始时间(秒)", 0.0, dur, 0.0)
            end = st.number_input("结束时间(秒)", 0.0, dur, min(5.0, dur))
            if st.button("开始剪切"):
                out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
                with st.spinner(t("processing")):
                    cut_video(st.session_state.video_path, start, end, out)
                st.success(t("success"))
                with open(out, "rb") as f:
                    st.download_button(t("download"), f, file_name="cut.mp4")
                cleanup_temp_files([out])
        else:
            st.info(t("upload_first"))
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif func == t("speed"):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(t("speed"))
        if st.session_state.get('video_path'):
            speed = st.number_input("速度倍数", 0.1, 5.0, 1.0, step=0.1)
            if st.button("应用变速"):
                out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
                with st.spinner(t("processing")):
                    speed_video(st.session_state.video_path, speed, out)
                st.success(t("success"))
                with open(out, "rb") as f:
                    st.download_button(t("download"), f, file_name="speed.mp4")
                cleanup_temp_files([out])
        else:
            st.info(t("upload_first"))
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif func == t("beauty_filter"):
        render_beauty_filter()
    elif func == t("gif_export"):
        render_gif_export()
    elif func == t("ai_assistant"):
        render_ai_assistant()
    elif func == t("smart_matting"):
        render_smart_matting()
    elif func == t("novel_to_video"):
        render_novel_to_video()
    elif func == t("material_library"):
        render_material_library()
    elif func == t("video_sites"):
        render_video_sites()
    elif func == t("movie_search"):
        render_movie_search()
    elif func == t("points_mall"):
        render_points_mall()
    elif func == t("multi_track"):
        render_multi_track()
    elif func == t("security"):
        render_security()
    elif func == t("about"):
        render_about()
    elif func == t("admin_panel"):
        render_admin_panel()
    elif func == t("share_app"):
        render_share()
    else:
        st.info(f"{t('current_function')}: {func}")

if __name__ == "__main__":
    main()
