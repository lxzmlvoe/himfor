import streamlit as st
import os
import hashlib
import sqlite3
import tempfile
import subprocess
import secrets
import uuid
import json
import time
import random
import re
import base64
import numpy as np
import pandas as pd
import plotly.express as px
import cv2
import requests
import jieba.analyse
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
from gtts import gTTS

st.set_page_config(page_title="小智 - 智能视频助手", page_icon="🤖", layout="wide")

# ========== 数据库初始化 ==========
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT,
        salt TEXT,
        points INTEGER DEFAULT 100,
        admin_level INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        action TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        type TEXT,
        content TEXT,
        media_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        likes INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        tips_total INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        post_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user, post_id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        post_id INTEGER,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user TEXT,
        to_user TEXT,
        post_id INTEGER,
        amount INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS promotions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        user TEXT,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        points_cost INTEGER,
        status TEXT DEFAULT 'active'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        task_id TEXT,
        completed_at TIMESTAMP,
        date DATE
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS welfare_donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        points INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS welfare_points (
        user TEXT PRIMARY KEY,
        total_donated INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

def init_sample_materials():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS video_materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        tags TEXT,
        url TEXT,
        duration INTEGER,
        thumbnail TEXT,
        source TEXT,
        uploader TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS music_materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        tags TEXT,
        url TEXT,
        artist TEXT,
        duration INTEGER,
        source TEXT,
        uploader TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute("SELECT COUNT(*) FROM video_materials")
    if c.fetchone()[0] == 0:
        sample_videos = [
            ("夏日海滩", "夏天,海边,沙滩", "https://www.w3schools.com/html/mov_bbb.mp4", 10, "", "sample", "admin"),
            ("城市夜景", "城市,夜景,灯光", "https://www.w3schools.com/html/movie.mp4", 15, "", "sample", "admin"),
        ]
        for name, tags, url, duration, thumb, source, uploader in sample_videos:
            c.execute("INSERT INTO video_materials (name, tags, url, duration, thumbnail, source, uploader) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (name, tags, url, duration, thumb, source, uploader))
    c.execute("SELECT COUNT(*) FROM music_materials")
    if c.fetchone()[0] == 0:
        sample_music = [
            ("轻快背景", "轻快,背景", "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", "SoundHelix", 30, "sample", "admin"),
        ]
        for name, tags, url, artist, duration, source, uploader in sample_music:
            c.execute("INSERT INTO music_materials (name, tags, url, artist, duration, source, uploader) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (name, tags, url, artist, duration, source, uploader))
    conn.commit()
    conn.close()

def init_tables():
    init_db()
    init_sample_materials()

# ========== 用户认证 ==========
def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return pwd_hash, salt

def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password_hash, salt, points, admin_level FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False, "用户不存在", None, None
    stored_hash, salt, points, admin_level = row
    input_hash, _ = hash_password(password, salt)
    if input_hash == stored_hash:
        return True, "登录成功", points, admin_level
    return False, "密码错误", None, None

def register_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return False, "用户名已存在"
    pwd_hash, salt = hash_password(password)
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    admin_level = 5 if count == 0 else 0
    c.execute("INSERT INTO users (username, password_hash, salt, points, admin_level) VALUES (?, ?, ?, 100, ?)",
              (username, pwd_hash, salt, admin_level))
    conn.commit()
    conn.close()
    return True, "注册成功"

def get_points(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT points FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def spend_points(username, points, reason):
    conn = sqlite3.connect('users.db')
    conn.execute("BEGIN")
    c = conn.cursor()
    c.execute("SELECT points FROM users WHERE username=? FOR UPDATE", (username,))
    row = c.fetchone()
    if not row or row[0] < points:
        conn.rollback()
        conn.close()
        return False
    c.execute("UPDATE users SET points = points - ? WHERE username=?", (points, username))
    c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, reason))
    conn.commit()
    conn.close()
    return True

def add_points(username, amount, reason):
    conn = sqlite3.connect('users.db')
    conn.execute("BEGIN")
    c = conn.cursor()
    c.execute("SELECT points FROM users WHERE username=? FOR UPDATE", (username,))
    row = c.fetchone()
    if not row:
        conn.rollback()
        conn.close()
        return False
    c.execute("UPDATE users SET points = points + ? WHERE username=?", (amount, username))
    c.execute("INSERT INTO user_logs (username, action) VALUES (?, ?)", (username, reason))
    conn.commit()
    conn.close()
    return True

def get_notifications(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("""
        SELECT action, timestamp FROM user_logs 
        WHERE username = ? AND (action LIKE '%点赞%' OR action LIKE '%评论%' OR action LIKE '%购买%')
        ORDER BY timestamp DESC LIMIT 20
    """, (username,))
    interact = c.fetchall()
    system = []
    conn.close()
    return interact, system

def get_welfare_points(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT total_donated FROM welfare_points WHERE user = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def add_welfare_points(username, points):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO welfare_points (user, total_donated) VALUES (?, 0)", (username,))
    c.execute("UPDATE welfare_points SET total_donated = total_donated + ? WHERE user = ?", (points, username))
    c.execute("INSERT INTO welfare_donations (user, points) VALUES (?, ?)", (username, points))
    conn.commit()
    conn.close()

# ========== 视频处理辅助函数 ==========
def save_uploaded_file(uploaded):
    if uploaded is None:
        return None
    suffix = os.path.splitext(uploaded.name)[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded.getbuffer())
    return tmp.name

def get_video_info(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return {"duration": total_frames/fps if fps > 0 else 0}

def cut_video(input_path, start, end, output_path):
    cmd = ["ffmpeg", "-i", input_path, "-ss", str(start), "-to", str(end),
           "-c:v", "libx264", "-preset", "fast", "-crf", "23",
           "-c:a", "aac", "-b:a", "128k", "-y", output_path]
    subprocess.run(cmd, check=True)
    return output_path

def speed_video(input_path, speed, output_path):
    cmd = ["ffmpeg", "-i", input_path, "-filter:v", f"setpts={1/speed}*PTS",
           "-c:a", "aac", "-y", output_path]
    subprocess.run(cmd, check=True)
    return output_path

def video_to_gif(input_path, output_path, start=0, duration=5):
    subprocess.run(["ffmpeg", "-i", input_path, "-ss", str(start), "-t", str(duration),
                    "-vf", "fps=10,scale=320:-1", output_path])

def generate_preview_frames(video_path, num_frames=5):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []
    times = []
    for i in range(num_frames):
        frame_pos = int(total_frames * i / num_frames)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
        ret, frame = cap.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            img_str = base64.b64encode(buffer).decode()
            frames.append(f"data:image/jpeg;base64,{img_str}")
            times.append(frame_pos / fps if fps > 0 else 0)
    cap.release()
    return frames, times

def render_preview_section(video_path):
    frames, times = generate_preview_frames(video_path)
    if not frames:
        return
    st.markdown("#### 🖼️ 关键帧预览")
    cols = st.columns(len(frames))
    for i, (img, t) in enumerate(zip(frames, times)):
        with cols[i]:
            st.image(img, use_column_width=True)
            if st.button(f"{t:.1f}s", key=f"preview_btn_{i}"):
                st.session_state.preview_seek_time = t
                st.rerun()
    if 'preview_seek_time' in st.session_state:
        st.info(f"⏩ 跳转到 {st.session_state.preview_seek_time:.1f} 秒")

# ========== 素材库 ==========
def get_video_materials():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id, name, tags, url, thumbnail FROM video_materials ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "tags": r[2].split(','), "url": r[3], "thumbnail": r[4]} for r in rows]

def get_music_materials():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id, name, tags, url FROM music_materials ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "tags": r[2].split(','), "url": r[3]} for r in rows]

# ========== 页面渲染函数 ==========
def render_clip_page():
    st.markdown("### 🎬 开始创作")
    uploaded = st.file_uploader("上传视频", type=["mp4", "mov", "avi"], key="clip_upload")
    if uploaded:
        video_path = save_uploaded_file(uploaded)
        st.session_state.video_path = video_path
        st.video(video_path)
        st.success("✅ 上传成功！")
    else:
        st.markdown("""
        <div style="text-align:center; padding: 50px; border: 2px dashed #ccc; border-radius: 20px;">
            <div style="font-size: 48px;">📤</div>
            <p>点击或拖拽视频开始创作</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.get('video_path'):
        render_preview_section(st.session_state.video_path)
    
    st.markdown("#### ✂️ 剪辑工具")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("剪切视频", use_container_width=True):
            if st.session_state.get('video_path'):
                dur = get_video_info(st.session_state.video_path)["duration"]
                with st.expander("设置剪切时间", expanded=True):
                    start = st.number_input("开始(秒)", 0.0, dur, 0.0)
                    end = st.number_input("结束(秒)", 0.0, dur, min(5.0, dur))
                    if st.button("确认剪切"):
                        out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
                        cut_video(st.session_state.video_path, start, end, out)
                        with open(out, "rb") as f:
                            st.download_button("下载", f, file_name="cut.mp4")
            else:
                st.warning("请先上传视频")
    with col2:
        if st.button("视频变速", use_container_width=True):
            if st.session_state.get('video_path'):
                with st.expander("选择速度", expanded=True):
                    def apply_speed(s):
                        out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
                        speed_video(st.session_state.video_path, s, out)
                        with open(out, "rb") as f:
                            st.download_button("下载", f, file_name=f"speed_{s}x.mp4")
                    cols_s = st.columns(4)
                    with cols_s[0]:
                        if st.button("0.5x"): apply_speed(0.5)
                    with cols_s[1]:
                        if st.button("1.0x"): apply_speed(1.0)
                    with cols_s[2]:
                        if st.button("1.5x"): apply_speed(1.5)
                    with cols_s[3]:
                        if st.button("2.0x"): apply_speed(2.0)
                    speed = st.number_input("自定义倍数", 0.5, 2.0, 1.0, step=0.1)
                    if st.button("应用自定义"):
                        apply_speed(speed)
            else:
                st.warning("请先上传视频")
    with col3:
        if st.button("导出GIF", use_container_width=True):
            if st.session_state.get('video_path'):
                with st.expander("设置GIF参数", expanded=True):
                    start = st.number_input("开始时间(秒)", 0.0, 10.0, 0.0)
                    duration = st.number_input("时长(秒)", 1.0, 10.0, 3.0)
                    if st.button("确认导出"):
                        out = tempfile.NamedTemporaryFile(suffix=".gif", delete=False).name
                        video_to_gif(st.session_state.video_path, out, start, duration)
                        with open(out, "rb") as f:
                            st.download_button("下载", f, file_name="output.gif")
            else:
                st.info("请先上传视频")

def render_community_page():
    st.markdown("### 🌐 灵感社区")
    st.info("社区功能开发中，敬请期待")

def render_my_page():
    st.markdown("### 👤 我的")
    if st.button("退出登录"):
        st.session_state.clear()
        st.rerun()

def render_auth():
    with st.sidebar:
        st.markdown("### 👤 用户中心")
        if not st.session_state.get('logged_in', False):
            tab = st.radio("", ["登录", "注册"], horizontal=True)
            if tab == "登录":
                username = st.text_input("用户名")
                password = st.text_input("密码", type="password")
                if st.button("登录"):
                    ok, msg, points, admin = login_user(username, password)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.points = points
                        st.session_state.admin_level = admin
                        st.session_state.remember_me = True
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                username = st.text_input("用户名")
                password = st.text_input("密码", type="password")
                confirm = st.text_input("确认密码", type="password")
                if st.button("注册"):
                    if password != confirm:
                        st.error("两次密码不一致")
                    else:
                        ok, msg = register_user(username, password)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            st.stop()
        else:
            points = get_points(st.session_state.username)
            st.success(f"欢迎，{st.session_state.username}")
            st.markdown(f'⭐ 积分：{points}', unsafe_allow_html=True)
            if st.button("退出登录"):
                st.session_state.clear()
                st.rerun()

def main():
    if 'language' not in st.session_state:
        st.session_state.language = 'zh'
    if st.session_state.get('remember_me', False):
        if 'username' in st.session_state:
            st.session_state.logged_in = True

    init_tables()
    
    render_auth()

    if not st.session_state.get('logged_in', False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; border-radius: 30px; text-align: center; margin-bottom: 30px;">
            <div style="font-size: 60px;">🤖</div>
            <h1 style="color: white;">小智 - 智能视频助手</h1>
            <p style="color: rgba(255,255,255,0.9);">你的AI视频创作伙伴</p>
        </div>
        """, unsafe_allow_html=True)
        st.info("👈 请先在左侧登录或注册")
        return

    if 'nav_index' not in st.session_state:
        st.session_state.nav_index = 0

    nav_items = ["🎬 剪辑", "🌐 社区", "👤 我的"]
    cols = st.columns(len(nav_items))
    for i, name in enumerate(nav_items):
        with cols[i]:
            if st.button(name, use_container_width=True):
                st.session_state.nav_index = i
                st.rerun()

    if st.session_state.nav_index == 0:
        render_clip_page()
    elif st.session_state.nav_index == 1:
        render_community_page()
    else:
        render_my_page()

if __name__ == "__main__":
    main()
