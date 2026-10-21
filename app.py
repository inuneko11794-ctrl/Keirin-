import streamlit as st
import streamlit.components.v1 as components

# スマホでも見やすくするため画面を広く使う設定
st.set_page_config(page_title="BYN Race Analyzer", layout="wide", initial_sidebar_state="collapsed")

# ---------------------------------------------------------
# 先ほど作っていただいたHTMLを、Pythonの文字列（"""〜"""）として格納します
# ---------------------------------------------------------
html_code = """
<!DOCTYPE html>
<html lang="ja" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BYN Race Analyzer - 手書き編集強化＆予想重複分析</title>

    <!-- PWA & Mobile Web App Meta Tags -->
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="BYN Race">
    <meta name="theme-color" content="#080c14">

    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Tesseract.js for OCR Screenshot Analysis -->
    <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
    <!-- FontAwesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Teko:wght@600;700&family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">

    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        byn: {
                            dark: '#080c14',
                            card: '#111827',
                            border: '#1f293d',
                            accent: '#2563eb',
                            siteB: '#3b82f6',
                            siteY: '#eab308',
                            siteN: '#ec4899',
                            win: '#10b981',
                            lose: '#ef4444',
                        }
                    },
                    fontFamily: {
                        teko: ['Teko', 'sans-serif'],
                        noto: ['Noto Sans JP', 'sans-serif'],
                    }
                }
            }
        }
    </script>
    <style>
        body {
            font-family: 'Noto Sans JP', sans-serif;
            background-color: #080c14;
            color: #f3f4f6;
        }
        .number-font {
            font-family: 'Teko', sans-serif;
            letter-spacing: 0.05em;
        }
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #080c14;
        }
        ::-webkit-scrollbar-thumb {
            background: #1f293d;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #3b82f6;
        }
        canvas {
            touch-action: none;
        }
    </style>
</head>
<body class="min-h-screen pb-12 flex flex-col">

    <!-- Header Navigation -->
    <header class="bg-byn-card border-b border-byn-border sticky top-0 z-50 shadow-xl backdrop-blur-md bg-opacity-95">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="bg-gradient-to-r from-blue-600 via-yellow-500 to-pink-500 p-0.5 rounded-xl shadow-lg">
                    <div class="bg-byn-dark px-3 py-1 rounded-[10px]">
                        <span class="number-font text-3xl font-extrabold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-yellow-300 to-pink-400">BYN</span>
                    </div>
                </div>
                <div>
                    <h1 class="text-base sm:text-lg font-extrabold text-white leading-tight flex items-center gap-2">
                        RACE ANALYZER
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-gradient-to-r from-blue-500 to-pink-500 text-white shadow">PRO EDIT</span>
                    </h1>
                    <p class="text-[11px] text-gray-400">7パターン予想重複分析 ＆ 手書き自由編集機能</p>
                </div>
            </div>

            <!-- Header Action Controls -->
            <div class="flex items-center gap-2">
                <button onclick="openOcrModal()" class="px-2.5 py-1.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:opacity-90 text-xs text-white font-extrabold rounded-lg transition flex items-center gap-1.5 shadow-lg border border-emerald-400/30">
                    <i class="fa-solid fa-camera font-bold"></i>
                    <span class="hidden sm:inline">画像自動入力(OCR)</span>
                </button>
                <button onclick="openPwaModal()" class="px-2.5 py-1.5 bg-gradient-to-r from-blue-600 via-indigo-600 to-pink-600 hover:opacity-90 text-xs text-white font-extrabold rounded-lg transition flex items-center gap-1.5 shadow-lg border border-blue-400/30">
                    <i class="fa-solid fa-mobile-screen-button"></i>
                    <span class="hidden sm:inline">ホーム追加</span>
                </button>
                <button onclick="loadSampleData()" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-amber-400 font-semibold rounded-lg transition flex items-center gap-1.5 shadow">
                    <i class="fa-solid fa-wand-magic-sparkles"></i>
                    <span class="hidden sm:inline">サンプル投入</span>
                </button>
                <button onclick="exportCSV()" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-emerald-400 font-semibold rounded-lg transition flex items-center gap-1.5 shadow">
                    <i class="fa-solid fa-file-csv"></i>
                    <span class="hidden sm:inline">CSV出力</span>
                </button>
                <label class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-blue-400 font-semibold rounded-lg transition cursor-pointer flex items-center gap-1.5 shadow">
                    <i class="fa-solid fa-file-import"></i>
                    <span class="hidden sm:inline">CSV取込</span>
                    <input type="file" id="csvFileInput" accept=".csv" onchange="importCSV(event)" class="hidden">
                </label>
            </div>
        </div>
    </header>

    <!-- Main Content Layout -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6 space-y-6">

        <!-- Nav Tabs -->
        <div class="flex border-b border-byn-border space-x-2 overflow-x-auto">
            <button id="tab-dashboard-btn" onclick="switchTab('dashboard')" class="tab-btn px-5 py-3 text-sm font-bold border-b-2 border-blue-500 text-blue-400 flex items-center gap-2 transition whitespace-nowrap">
                <i class="fa-solid fa-chart-pie"></i> ダッシュボード・全7パターン検証
            </button>
            <button id="tab-input-btn" onclick="switchTab('input')" class="tab-btn px-5 py-3 text-sm font-bold border-b-2 border-transparent text-gray-400 hover:text-gray-200 flex items-center gap-2 transition whitespace-nowrap">
                <i class="fa-solid fa-square-plus"></i> レース＆手書き買い目登録
            </button>
            <button id="tab-records-btn" onclick="switchTab('records')" class="tab-btn px-5 py-3 text-sm font-bold border-b-2 border-transparent text-gray-400 hover:text-gray-200 flex items-center gap-2 transition whitespace-nowrap">
                <i class="fa-solid fa-list-ul"></i> 組み合わせ・結果一覧 (<span id="record-count-badge">0</span>)
            </button>
        </div>

        <!-- TAB 1: DASHBOARD & PATTERN ANALYSIS -->
        <section id="tab-dashboard" class="space-y-6">
            
            <!-- Global Summary Cards -->
            <div class="grid grid-cols-2 md:grid-cols-5 gap-3 sm:gap-4">
                <div class="bg-byn-card border border-byn-border rounded-xl p-4 shadow-md">
                    <span class="text-xs text-gray-400 block font-medium">総登録レース数</span>
                    <div class="flex items-baseline gap-1 mt-1">
                        <span id="stat-total-races" class="number-font text-3xl font-bold text-white">0</span>
                        <span class="text-xs text-gray-400">件</span>
                    </div>
                </div>

                <div class="bg-byn-card border border-byn-border rounded-xl p-4 shadow-md">
                    <span class="text-xs text-gray-400 block font-medium">総投資額</span>
                    <div class="flex items-baseline gap-1 mt-1">
                        <span id="stat-total-invest" class="number-font text-3xl font-bold text-gray-200">¥0</span>
                    </div>
                </div>

                <div class="bg-byn-card border border-byn-border rounded-xl p-4 shadow-md">
                    <span class="text-xs text-gray-400 block font-medium">総払戻金</span>
                    <div class="flex items-baseline gap-1 mt-1">
                        <span id="stat-total-payout" class="number-font text-3xl font-bold text-gray-200">¥0</span>
                    </div>
                </div>

                <div class="bg-byn-card border border-byn-border rounded-xl p-4 shadow-md">
                    <span class="text-xs text-gray-400 block font-medium">通算損益 (純利益)</span>
                    <div class="flex items-baseline gap-1 mt-1">
                        <span id="stat-total-profit" class="number-font text-3xl font-bold text-white">¥0</span>
                    </div>
                </div>

                <div class="col-span-2 md:col-span-1 bg-gradient-to-br from-byn-card to-slate-900 border border-blue-500/30 rounded-xl p-4 shadow-lg">
                    <div class="flex justify-between items-center">
                        <span class="text-xs text-gray-400 font-medium">トータル回収率</span>
                        <span id="stat-total-hitrate" class="text-xs font-bold text-emerald-400">的中率 0%</span>
                    </div>
                    <div class="flex items-baseline gap-1 mt-1">
                        <span id="stat-total-return" class="number-font text-4xl font-black text-blue-400">0.0%</span>
                    </div>
                </div>
            </div>

            <!-- CORE PATTERN ANALYSIS -->
            <div class="space-y-4">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                    <h2 class="text-lg font-extrabold text-white flex items-center gap-2">
                        <i class="fa-solid fa-cubes-stacked text-amber-400"></i>
                        サイト組み合わせ別 成績比較 (全7パターン詳細)
                    </h2>
                    <span class="text-xs text-gray-400">※B・Y・Nのどの単独・ペア・3サイト重複が最も稼げるか検証</span>
                </div>

                <!-- 3-SITE OVERLAP SECTION -->
                <div class="space-y-2">
                    <div class="text-xs font-bold text-amber-400 flex items-center gap-1.5 uppercase tracking-wider">
                        <i class="fa-solid fa-crown"></i> 3サイト全重複 (1パターン)
                    </div>
                    <div class="grid grid-cols-1 gap-4">
                        <div class="bg-byn-card border-2 border-amber-500/80 rounded-2xl p-5 relative overflow-hidden shadow-2xl bg-gradient-to-r from-amber-500/10 via-byn-card to-byn-card">
                            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                                <div class="flex items-center gap-3">
                                    <div class="flex -space-x-1">
                                        <span class="w-8 h-8 rounded-full bg-blue-500 text-white font-extrabold text-sm flex items-center justify-center border-2 border-slate-900">B</span>
                                        <span class="w-8 h-8 rounded-full bg-amber-500 text-slate-950 font-extrabold text-sm flex items-center justify-center border-2 border-slate-900">Y</span>
                                        <span class="w-8 h-8 rounded-full bg-pink-500 text-white font-extrabold text-sm flex items-center justify-center border-2 border-slate-900">N</span>
                                    </div>
                                    <div>
                                        <h3 class="font-extrabold text-white text-lg">B & Y & N <span class="text-xs font-normal text-amber-300 ml-1">(全重複)</span></h3>
                                        <p class="text-xs text-gray-400">3サイトすべての予想が一致した最高精度レース</p>
                                    </div>
                                </div>

                                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                                    <div class="bg-slate-900/90 p-2.5 rounded-xl border border-slate-800">
                                        <span class="text-[10px] text-gray-400 block font-semibold">回収率 (ROI)</span>
                                        <span id="pat-B_Y_N-return" class="number-font text-2xl font-black text-amber-400">0.0%</span>
                                    </div>
                                    <div class="bg-slate-900/90 p-2.5 rounded-xl border border-slate-800">
                                        <span class="text-[10px] text-gray-400 block font-semibold">的中率</span>
                                        <span id="pat-B_Y_N-hit" class="number-font text-2xl font-bold text-emerald-400">0.0%</span>
                                    </div>
                                    <div class="bg-slate-900/90 p-2.5 rounded-xl border border-slate-800">
                                        <span class="text-[10px] text-gray-400 block font-semibold">レース数</span>
                                        <span id="pat-B_Y_N-count" class="number-font text-2xl font-bold text-white">0件</span>
                                    </div>
                                    <div class="bg-slate-900/90 p-2.5 rounded-xl border border-slate-800">
                                        <span class="text-[10px] text-gray-400 block font-semibold">純損益</span>
                                        <span id="pat-B_Y_N-profit" class="number-font text-2xl font-bold">¥0</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 2-SITE OVERLAP PAIRS SECTION -->
                <div class="space-y-2 pt-2">
                    <div class="text-xs font-bold text-blue-400 flex items-center gap-1.5 uppercase tracking-wider">
                        <i class="fa-solid fa-handshake"></i> 2サイト重複ペア (3パターン)
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <!-- B & Y -->
                        <div class="bg-byn-card border border-blue-500/40 rounded-2xl p-4 shadow-xl bg-gradient-to-b from-blue-500/5 via-byn-card to-byn-card flex flex-col justify-between space-y-3">
                            <div class="flex justify-between items-center">
                                <div class="flex items-center gap-2">
                                    <div class="flex -space-x-1">
                                        <span class="w-6 h-6 rounded-full bg-blue-500 text-white font-bold text-xs flex items-center justify-center border border-slate-900">B</span>
                                        <span class="w-6 h-6 rounded-full bg-amber-500 text-slate-950 font-bold text-xs flex items-center justify-center border border-slate-900">Y</span>
                                    </div>
                                    <h3 class="font-extrabold text-white text-base">B & Y</h3>
                                </div>
                                <span id="pat-B_Y-count" class="text-xs text-gray-400 font-bold">0件</span>
                            </div>
                            <div class="grid grid-cols-2 gap-2">
                                <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">回収率</span>
                                    <span id="pat-B_Y-return" class="number-font text-2xl font-black text-blue-400">0.0%</span>
                                </div>
                                <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">的中率</span>
                                    <span id="pat-B_Y-hit" class="number-font text-2xl font-bold text-emerald-400">0.0%</span>
                                </div>
                            </div>
                            <div class="flex justify-between items-center text-xs text-gray-300 pt-1 border-t border-slate-800/80">
                                <span class="text-gray-400">純損益:</span>
                                <span id="pat-B_Y-profit" class="font-bold">¥0</span>
                            </div>
                        </div>

                        <!-- Y & N -->
                        <div class="bg-byn-card border border-amber-500/40 rounded-2xl p-4 shadow-xl bg-gradient-to-b from-amber-500/5 via-byn-card to-byn-card flex flex-col justify-between space-y-3">
                            <div class="flex justify-between items-center">
                                <div class="flex items-center gap-2">
                                    <div class="flex -space-x-1">
                                        <span class="w-6 h-6 rounded-full bg-amber-500 text-slate-950 font-bold text-xs flex items-center justify-center border border-slate-900">Y</span>
                                        <span class="w-6 h-6 rounded-full bg-pink-500 text-white font-bold text-xs flex items-center justify-center border border-slate-900">N</span>
                                    </div>
                                    <h3 class="font-extrabold text-white text-base">Y & N</h3>
                                </div>
                                <span id="pat-Y_N-count" class="text-xs text-gray-400 font-bold">0件</span>
                            </div>
                            <div class="grid grid-cols-2 gap-2">
                                <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">回収率</span>
                                    <span id="pat-Y_N-return" class="number-font text-2xl font-black text-amber-400">0.0%</span>
                                </div>
                                <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">的中率</span>
                                    <span id="pat-Y_N-hit" class="number-font text-2xl font-bold text-emerald-400">0.0%</span>
                                </div>
                            </div>
                            <div class="flex justify-between items-center text-xs text-gray-300 pt-1 border-t border-slate-800/80">
                                <span class="text-gray-400">純損益:</span>
                                <span id="pat-Y_N-profit" class="font-bold">¥0</span>
                            </div>
                        </div>

                        <!-- B & N -->
                        <div class="bg-byn-card border border-pink-500/40 rounded-2xl p-4 shadow-xl bg-gradient-to-b from-pink-500/5 via-byn-card to-byn-card flex flex-col justify-between space-y-3">
  
