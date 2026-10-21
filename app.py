import streamlit as st
import streamlit.components.v1 as components

# スマホでも見やすくするため画面を広く使う設定
st.set_page_config(page_title="BYN Race Analyzer", layout="wide", initial_sidebar_state="collapsed")

# ---------------------------------------------------------
# 先ほど作っていただいたHTMLを、Pythonの文字列（r"""〜"""）として格納します
# ---------------------------------------------------------
html_code = r"""
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
                            <div class="flex justify-between items-center">
                                <div class="flex items-center gap-2">
                                    <div class="flex -space-x-1">
                                        <span class="w-6 h-6 rounded-full bg-blue-500 text-white font-bold text-xs flex items-center justify-center border border-slate-900">B</span>
                                        <span class="w-6 h-6 rounded-full bg-pink-500 text-white font-bold text-xs flex items-center justify-center border border-slate-900">N</span>
                                    </div>
                                    <h3 class="font-extrabold text-white text-base">B & N</h3>
                                </div>
                                <span id="pat-B_N-count" class="text-xs text-gray-400 font-bold">0件</span>
                            </div>
                            <div class="grid grid-cols-2 gap-2">
                                <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">回収率</span>
                                    <span id="pat-B_N-return" class="number-font text-2xl font-black text-pink-400">0.0%</span>
                                </div>
                                <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">的中率</span>
                                    <span id="pat-B_N-hit" class="number-font text-2xl font-bold text-emerald-400">0.0%</span>
                                </div>
                            </div>
                            <div class="flex justify-between items-center text-xs text-gray-300 pt-1 border-t border-slate-800/80">
                                <span class="text-gray-400">純損益:</span>
                                <span id="pat-B_N-profit" class="font-bold">¥0</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 1-SITE ALONE SECTION -->
                <div class="space-y-2 pt-2">
                    <div class="text-xs font-bold text-gray-400 flex items-center gap-1.5 uppercase tracking-wider">
                        <i class="fa-solid fa-user"></i> 単独サイト (3パターン)
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div class="bg-byn-card border border-byn-border rounded-2xl p-4 shadow-xl flex flex-col justify-between space-y-3">
                            <div class="flex justify-between items-center">
                                <div class="flex items-center gap-2">
                                    <span class="w-6 h-6 rounded-full bg-blue-500 text-white font-bold text-xs flex items-center justify-center">B</span>
                                    <h3 class="font-bold text-white text-base">B のみ</h3>
                                </div>
                                <span id="pat-B-count" class="text-xs text-gray-400 font-bold">0件</span>
                            </div>
                            <div class="grid grid-cols-2 gap-2">
                                <div class="bg-slate-900/50 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">回収率</span>
                                    <span id="pat-B-return" class="number-font text-xl font-bold text-blue-300">0.0%</span>
                                </div>
                                <div class="bg-slate-900/50 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">的中率</span>
                                    <span id="pat-B-hit" class="number-font text-xl font-bold text-emerald-400">0.0%</span>
                                </div>
                            </div>
                            <div class="flex justify-between items-center text-xs text-gray-300 pt-1 border-t border-slate-800/50">
                                <span class="text-gray-400">純損益:</span>
                                <span id="pat-B-profit" class="font-bold">¥0</span>
                            </div>
                        </div>

                        <div class="bg-byn-card border border-byn-border rounded-2xl p-4 shadow-xl flex flex-col justify-between space-y-3">
                            <div class="flex justify-between items-center">
                                <div class="flex items-center gap-2">
                                    <span class="w-6 h-6 rounded-full bg-amber-500 text-slate-950 font-bold text-xs flex items-center justify-center">Y</span>
                                    <h3 class="font-bold text-white text-base">Y のみ</h3>
                                </div>
                                <span id="pat-Y-count" class="text-xs text-gray-400 font-bold">0件</span>
                            </div>
                            <div class="grid grid-cols-2 gap-2">
                                <div class="bg-slate-900/50 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">回収率</span>
                                    <span id="pat-Y-return" class="number-font text-xl font-bold text-amber-300">0.0%</span>
                                </div>
                                <div class="bg-slate-900/50 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">的中率</span>
                                    <span id="pat-Y-hit" class="number-font text-xl font-bold text-emerald-400">0.0%</span>
                                </div>
                            </div>
                            <div class="flex justify-between items-center text-xs text-gray-300 pt-1 border-t border-slate-800/50">
                                <span class="text-gray-400">純損益:</span>
                                <span id="pat-Y-profit" class="font-bold">¥0</span>
                            </div>
                        </div>

                        <div class="bg-byn-card border border-byn-border rounded-2xl p-4 shadow-xl flex flex-col justify-between space-y-3">
                            <div class="flex justify-between items-center">
                                <div class="flex items-center gap-2">
                                    <span class="w-6 h-6 rounded-full bg-pink-500 text-white font-bold text-xs flex items-center justify-center">N</span>
                                    <h3 class="font-bold text-white text-base">N のみ</h3>
                                </div>
                                <span id="pat-N-count" class="text-xs text-gray-400 font-bold">0件</span>
                            </div>
                            <div class="grid grid-cols-2 gap-2">
                                <div class="bg-slate-900/50 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">回収率</span>
                                    <span id="pat-N-return" class="number-font text-xl font-bold text-pink-300">0.0%</span>
                                </div>
                                <div class="bg-slate-900/50 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">的中率</span>
                                    <span id="pat-N-hit" class="number-font text-xl font-bold text-emerald-400">0.0%</span>
                                </div>
                            </div>
                            <div class="flex justify-between items-center text-xs text-gray-300 pt-1 border-t border-slate-800/50">
                                <span class="text-gray-400">純損益:</span>
                                <span id="pat-N-profit" class="font-bold">¥0</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 2: INPUT FORM & HANDWRITING -->
        <section id="tab-input" class="hidden space-y-6">
            <div class="bg-byn-card border border-byn-border rounded-xl p-5 shadow-lg relative">
                
                <h2 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <i class="fa-solid fa-pen-to-square text-blue-500"></i>
                    新規レース登録 ＆ 手書きメモ
                </h2>

                <form id="race-form" onsubmit="saveRace(event)" class="space-y-6">
                    <input type="hidden" id="edit-id" value="">

                    <!-- Step 1: Base Info -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="space-y-1">
                            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wider">日付</label>
                            <input type="date" id="date" required class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500 transition">
                        </div>
                        <div class="space-y-1">
                            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wider">レース識別 (例: 平塚11R)</label>
                            <input type="text" id="race-id" placeholder="競輪場名 や レース番号など" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500 transition">
                        </div>
                    </div>

                    <!-- Step 2: Site Checkboxes -->
                    <div class="space-y-2">
                        <div class="flex justify-between items-end">
                            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wider">推奨サイト (重複チェック)</label>
                            <span id="live-pattern-badge" class="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-gray-400 font-bold border border-slate-700">選択なし</span>
                        </div>
                        <div class="grid grid-cols-3 gap-3">
                            <label class="relative flex items-center justify-center p-3 rounded-xl border-2 border-slate-700 bg-slate-900 cursor-pointer hover:bg-slate-800 transition has-[:checked]:border-blue-500 has-[:checked]:bg-blue-500/10">
                                <input type="checkbox" id="site-B" value="B" onchange="updateLivePattern()" class="peer hidden">
                                <div class="flex items-center gap-2">
                                    <span class="w-6 h-6 rounded-full bg-blue-500 text-white font-bold text-xs flex items-center justify-center opacity-40 peer-checked:opacity-100 transition">B</span>
                                    <span class="font-bold text-sm text-gray-400 peer-checked:text-white transition">Bサイト</span>
                                </div>
                            </label>

                            <label class="relative flex items-center justify-center p-3 rounded-xl border-2 border-slate-700 bg-slate-900 cursor-pointer hover:bg-slate-800 transition has-[:checked]:border-amber-500 has-[:checked]:bg-amber-500/10">
                                <input type="checkbox" id="site-Y" value="Y" onchange="updateLivePattern()" class="peer hidden">
                                <div class="flex items-center gap-2">
                                    <span class="w-6 h-6 rounded-full bg-amber-500 text-slate-950 font-bold text-xs flex items-center justify-center opacity-40 peer-checked:opacity-100 transition">Y</span>
                                    <span class="font-bold text-sm text-gray-400 peer-checked:text-white transition">Yサイト</span>
                                </div>
                            </label>

                            <label class="relative flex items-center justify-center p-3 rounded-xl border-2 border-slate-700 bg-slate-900 cursor-pointer hover:bg-slate-800 transition has-[:checked]:border-pink-500 has-[:checked]:bg-pink-500/10">
                                <input type="checkbox" id="site-N" value="N" onchange="updateLivePattern()" class="peer hidden">
                                <div class="flex items-center gap-2">
                                    <span class="w-6 h-6 rounded-full bg-pink-500 text-white font-bold text-xs flex items-center justify-center opacity-40 peer-checked:opacity-100 transition">N</span>
                                    <span class="font-bold text-sm text-gray-400 peer-checked:text-white transition">Nサイト</span>
                                </div>
                            </label>
                        </div>
                    </div>

                    <hr class="border-byn-border">
                    <!-- Step 3: Multi-Ticket Input -->
                    <div class="space-y-3">
                        <div class="flex justify-between items-center">
                            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wider">
                                <i class="fa-solid fa-ticket text-emerald-500"></i> 購入買い目リスト
                            </label>
                            <button type="button" onclick="addTicketRow()" class="text-xs text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1 bg-blue-500/10 px-2 py-1 rounded">
                                <i class="fa-solid fa-plus"></i> 行を追加
                            </button>
                        </div>
                        
                        <div id="tickets-container" class="space-y-2"></div>
                        
                        <div class="flex justify-end pt-1">
                            <div class="text-sm font-bold text-gray-300">
                                合計投資額: <span id="live-total-invest" class="text-white text-lg number-font">¥0</span>
                            </div>
                        </div>
                    </div>

                    <hr class="border-byn-border">

                    <!-- Step 4: Handwriting Memo -->
                    <div class="space-y-2">
                        <div class="flex justify-between items-end mb-1">
                            <label class="block text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
                                <i class="fa-solid fa-signature text-amber-500"></i> 展開・買い目メモ (手書き)
                            </label>
                            <div class="flex items-center gap-2">
                                <div class="flex bg-slate-800 rounded-lg p-0.5">
                                    <button type="button" onclick="setCanvasColor('#38bdf8', this)" class="color-btn w-6 h-6 rounded-md bg-sky-400 ring-2 ring-white m-0.5"></button>
                                    <button type="button" onclick="setCanvasColor('#f43f5e', this)" class="color-btn w-6 h-6 rounded-md bg-rose-500 m-0.5"></button>
                                    <button type="button" onclick="setCanvasColor('#facc15', this)" class="color-btn w-6 h-6 rounded-md bg-yellow-400 m-0.5"></button>
                                    <button type="button" onclick="setCanvasColor('#10b981', this)" class="color-btn w-6 h-6 rounded-md bg-emerald-500 m-0.5"></button>
                                </div>
                                <button type="button" onclick="clearCanvas()" class="text-xs text-gray-400 hover:text-rose-400 px-2 py-1 rounded bg-slate-800">
                                    <i class="fa-solid fa-eraser"></i> クリア
                                </button>
                            </div>
                        </div>
                        
                        <div class="border-2 border-slate-700 rounded-xl overflow-hidden bg-slate-900 relative">
                            <canvas id="handwriting-canvas" class="w-full h-[200px] sm:h-[250px] touch-none cursor-crosshair"></canvas>
                            <div class="absolute bottom-2 right-2 pointer-events-none text-[10px] text-slate-500 font-bold">自由に書き込めます</div>
                        </div>
                    </div>

                    <hr class="border-byn-border">

                    <!-- Step 5: Result & Payout -->
                    <div class="space-y-4 bg-slate-900 p-4 rounded-xl border border-slate-700/50">
                        <label class="block text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1.5 mb-2">
                            <i class="fa-solid fa-flag-checkered text-white"></i> レース結果 (事後入力)
                        </label>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div class="space-y-1">
                                <label class="block text-[11px] text-gray-500">決定着順 (例: 5-1-6)</label>
                                <input type="text" id="result-combo" placeholder="未決定" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500 transition text-center font-bold">
                            </div>
                            <div class="space-y-1">
                                <label class="block text-[11px] text-gray-500">3連単配当 (円)</label>
                                <div class="relative">
                                    <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 font-bold">¥</span>
                                    <input type="number" id="payout-amount" placeholder="0" class="w-full bg-slate-800 border border-slate-700 rounded-lg pl-7 pr-3 py-2 text-white focus:outline-none focus:border-blue-500 transition text-right number-font font-bold text-lg">
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Submit -->
                    <div class="flex gap-3 pt-2">
                        <button type="submit" id="save-btn" class="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:opacity-90 text-white font-extrabold py-3.5 px-4 rounded-xl shadow-lg transition flex justify-center items-center gap-2">
                            <i class="fa-solid fa-floppy-disk"></i> <span id="save-btn-text">このレースを保存する</span>
                        </button>
                        <button type="button" onclick="resetForm()" class="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-gray-300 py-3.5 px-5 rounded-xl font-bold transition">
                            リセット
                        </button>
                    </div>
                </form>
            </div>
        </section>

        <!-- TAB 3: RECORDS LIST -->
        <section id="tab-records" class="hidden space-y-4">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-byn-card p-4 rounded-xl border border-byn-border shadow-md">
                <div class="flex items-center gap-2">
                    <i class="fa-solid fa-filter text-blue-500"></i>
                    <span class="text-sm font-bold text-gray-300">フィルター絞り込み</span>
                </div>
                <div class="flex flex-wrap items-center gap-2">
                    <select id="filter-pattern" onchange="renderRecords()" class="bg-slate-900 border border-slate-700 text-sm text-white rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500">
                        <option value="ALL">全パターン表示</option>
                        <option value="B_Y_N">B & Y & N (全重複)</option>
                        <option value="B_Y">B & Y (2重)</option>
                        <option value="Y_N">Y & N (2重)</option>
                        <option value="B_N">B & N (2重)</option>
                        <option value="B">B 単独</option>
                        <option value="Y">Y 単独</option>
                        <option value="N">N 単独</option>
                    </select>
                </div>
            </div>

            <div id="records-container" class="space-y-3"></div>
        </section>
    </main>

    <!-- PWA Install Modal -->
    <div id="pwa-modal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-[100] hidden flex items-center justify-center p-4">
        <div class="bg-byn-card border border-byn-border rounded-2xl max-w-sm w-full p-6 shadow-2xl relative">
            <button onclick="closePwaModal()" class="absolute top-4 right-4 text-gray-500 hover:text-white transition">
                <i class="fa-solid fa-xmark text-xl"></i>
            </button>
            <div class="text-center space-y-4">
                <div class="w-16 h-16 bg-gradient-to-r from-blue-500 to-pink-500 rounded-2xl mx-auto flex items-center justify-center shadow-lg">
                    <i class="fa-solid fa-mobile-screen-button text-2xl text-white"></i>
                </div>
                <h3 class="text-xl font-bold text-white">アプリとして追加</h3>
                <p class="text-sm text-gray-400 leading-relaxed">
                    ホーム画面に追加すると、フルスクリーンでアプリのように快適に利用できます。
                </p>
                <div class="bg-slate-900 p-4 rounded-xl border border-slate-700 text-left space-y-2">
                    <p class="text-xs text-gray-300"><i class="fa-brands fa-apple text-gray-400 w-4"></i> <b>iOS (Safari):</b> 下部の共有ボタンから「ホーム画面に追加」</p>
                    <p class="text-xs text-gray-300"><i class="fa-brands fa-android text-emerald-400 w-4"></i> <b>Android (Chrome):</b> メニューから「ホーム画面に追加」</p>
                </div>
                <button onclick="closePwaModal()" class="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-xl transition border border-slate-700">
                    閉じる
                </button>
            </div>
        </div>
    </div>

    <!-- OCR Modal -->
    <div id="ocr-modal" class="fixed inset-0 bg-black/90 backdrop-blur-sm z-[100] hidden flex items-center justify-center p-4">
        <div class="bg-byn-card border border-byn-border rounded-2xl max-w-2xl w-full flex flex-col max-h-[90vh] shadow-2xl">
            <div class="flex justify-between items-center p-4 border-b border-slate-800">
                <h3 class="text-lg font-bold text-white flex items-center gap-2">
                    <i class="fa-solid fa-camera text-emerald-500"></i> 画像から自動入力 (OCR)
                </h3>
                <button onclick="closeOcrModal()" class="text-gray-500 hover:text-white transition">
                    <i class="fa-solid fa-xmark text-xl"></i>
                </button>
            </div>
            <div class="p-4 sm:p-6 overflow-y-auto space-y-5">
                <p class="text-xs text-gray-400 text-center">
                    スマートフォンのスクリーンショットをアップロードまたはペーストすると、文字を自動認識してフォームに入力します。
                </p>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div id="ocr-box-arrival" class="border-2 border-dashed border-indigo-500/50 hover:border-indigo-500 rounded-xl p-4 flex flex-col items-center justify-center text-center cursor-pointer transition bg-indigo-500/5 min-h-[160px] relative" onclick="document.getElementById('ocr-input-arrival').click()">
                        <input type="file" id="ocr-input-arrival" accept="image/*" class="hidden" onchange="handleOcrImage(event, 'arrival')">
                        <div id="ocr-idle-arrival" class="space-y-2 pointer-events-none">
                            <i class="fa-solid fa-flag-checkered text-3xl text-indigo-400"></i>
                            <div>
                                <p class="text-sm font-bold text-indigo-200">① 着順スクリーンショット</p>
                                <p class="text-[10px] text-gray-500 mt-1">タップして選択 または コピペ</p>
                            </div>
                        </div>
                        <div id="ocr-loading-arrival" class="hidden flex-col items-center space-y-3">
                            <i class="fa-solid fa-circle-notch fa-spin text-3xl text-amber-500"></i>
                            <p class="text-xs font-bold text-amber-400">文字を解析中...</p>
                        </div>
                        <div id="ocr-preview-arrival" class="hidden w-full h-full flex flex-col items-center justify-center relative">
                            <img id="ocr-img-arrival" src="" class="max-h-24 object-contain rounded shadow border border-slate-700 mb-2">
                            <span class="text-[10px] bg-indigo-600/80 text-white px-2 py-1 rounded font-bold">着順 読取完了</span>
                            <button type="button" onclick="event.stopPropagation(); clearOcrBox('arrival')" class="absolute top-0 right-0 w-6 h-6 bg-slate-800 rounded-full text-gray-400 hover:text-rose-500 flex items-center justify-center -mr-2 -mt-2 border border-slate-600 shadow">
                                <i class="fa-solid fa-times text-xs"></i>
                            </button>
                        </div>
                    </div>
                    <div id="ocr-box-payout" class="border-2 border-dashed border-emerald-500/50 hover:border-emerald-500 rounded-xl p-4 flex flex-col items-center justify-center text-center cursor-pointer transition bg-emerald-500/5 min-h-[160px] relative" onclick="document.getElementById('ocr-input-payout').click()">
                        <input type="file" id="ocr-input-payout" accept="image/*" class="hidden" onchange="handleOcrImage(event, 'payout')">
                        <div id="ocr-idle-payout" class="space-y-2 pointer-events-none">
                            <i class="fa-solid fa-sack-dollar text-3xl text-emerald-400"></i>
                            <div>
                                <p class="text-sm font-bold text-emerald-200">② 配当スクリーンショット</p>
                                <p class="text-[10px] text-gray-500 mt-1">タップして選択 または コピペ</p>
                            </div>
                        </div>
                        <div id="ocr-loading-payout" class="hidden flex-col items-center space-y-3">
                            <i class="fa-solid fa-circle-notch fa-spin text-3xl text-amber-500"></i>
                            <p class="text-xs font-bold text-amber-400">文字を解析中...</p>
                        </div>
                        <div id="ocr-preview-payout" class="hidden w-full h-full flex flex-col items-center justify-center relative">
                            <img id="ocr-img-payout" src="" class="max-h-24 object-contain rounded shadow border border-slate-700 mb-2">
                            <span class="text-[10px] bg-emerald-600/80 text-white px-2 py-1 rounded font-bold">配当 読取完了</span>
                            <button type="button" onclick="event.stopPropagation(); clearOcrBox('payout')" class="absolute top-0 right-0 w-6 h-6 bg-slate-800 rounded-full text-gray-400 hover:text-rose-500 flex items-center justify-center -mr-2 -mt-2 border border-slate-600 shadow">
                                <i class="fa-solid fa-times text-xs"></i>
                            </button>
                        </div>
                    </div>
                </div>
                <div class="bg-slate-900 border border-slate-700 rounded-xl p-3">
                    <h4 class="text-xs font-bold text-gray-400 mb-2 border-b border-slate-800 pb-1">抽出結果 (修正可能)</h4>
                    <div id="ocr-results-container" class="space-y-2 max-h-[150px] overflow-y-auto">
                        <p class="text-xs text-gray-600 text-center py-4">画像をアップロードするとここに結果が表示されます</p>
                    </div>
                </div>
            </div>
            <div class="p-4 border-t border-slate-800 flex justify-end gap-2 bg-slate-900/50 rounded-b-2xl">
                <button type="button" onclick="closeOcrModal()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-sm font-bold rounded-lg transition border border-slate-700">
                    キャンセル
                </button>
                <button type="button" id="ocr-apply-btn" onclick="applyOcrToForm()" disabled class="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-bold rounded-lg transition flex items-center gap-2 shadow-lg">
                    <i class="fa-solid fa-check"></i> この結果を入力フォームへ適用
                </button>
            </div>
        </div>
    </div>
    <!-- Application Script -->
    <script>
        const STORAGE_KEY = 'BYN_RACE_DATA_PRO';
        let races = [];
        let chartInstance = null;
        let canvas, ctx;
        let isDrawing = false;
        let currentBrushColor = '#38bdf8';
        let ocrParsedData = { arrival: {}, payout: {} };

        document.addEventListener('DOMContentLoaded', () => {
            loadData();
            initCanvas();
            renderDashboard();
            renderRecords();
            updateRecordCountBadge();
            document.getElementById('date').value = new Date().toISOString().split('T')[0];
            addTicketRow();
            window.addEventListener('paste', handleGlobalPaste);
        });

        function loadData() {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved) {
                try { races = JSON.parse(saved); } catch(e) { races = []; }
            }
        }

        function saveData() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(races));
            renderDashboard();
            renderRecords();
            updateRecordCountBadge();
        }

        function getPatternKey(sites) {
            if (sites.includes('B') && sites.includes('Y') && sites.includes('N')) return 'B_Y_N';
            if (sites.includes('B') && sites.includes('Y')) return 'B_Y';
            if (sites.includes('Y') && sites.includes('N')) return 'Y_N';
            if (sites.includes('B') && sites.includes('N')) return 'B_N';
            if (sites.includes('B')) return 'B';
            if (sites.includes('Y')) return 'Y';
            if (sites.includes('N')) return 'N';
            return 'NONE';
        }

        function switchTab(tabId) {
            ['dashboard', 'input', 'records'].forEach(id => {
                document.getElementById(`tab-${id}`).classList.add('hidden');
                const btn = document.getElementById(`tab-${id}-btn`);
                btn.classList.remove('border-blue-500', 'text-blue-400');
                btn.classList.add('border-transparent', 'text-gray-400');
            });
            document.getElementById(`tab-${tabId}`).classList.remove('hidden');
            const activeBtn = document.getElementById(`tab-${tabId}-btn`);
            activeBtn.classList.remove('border-transparent', 'text-gray-400');
            activeBtn.classList.add('border-blue-500', 'text-blue-400');

            if (tabId === 'input' && !document.getElementById('edit-id').value) {
                setTimeout(() => {
                    const tempImg = canvas.toDataURL();
                    canvas.width = canvas.parentElement.clientWidth;
                    const img = new Image();
                    img.onload = () => ctx.drawImage(img, 0, 0);
                    img.src = tempImg;
                    updateTotalInvest();
                }, 50);
            }
        }

        function updateLivePattern() {
            const sites = getSelectedSites();
            const badge = document.getElementById('live-pattern-badge');
            if (sites.length === 0) {
                badge.textContent = "選択なし";
                badge.className = "text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-gray-400 font-bold border border-slate-700";
                return;
            }
            const key = getPatternKey(sites);
            let label = "", colorClass = "";
            switch(key) {
                case 'B_Y_N': label = "B & Y & N (全重複)"; colorClass = "bg-amber-500/20 text-amber-400 border-amber-500/50"; break;
                case 'B_Y': label = "B & Y"; colorClass = "bg-blue-500/20 text-blue-400 border-blue-500/50"; break;
                case 'Y_N': label = "Y & N"; colorClass = "bg-amber-500/20 text-amber-400 border-amber-500/50"; break;
                case 'B_N': label = "B & N"; colorClass = "bg-pink-500/20 text-pink-400 border-pink-500/50"; break;
                case 'B': label = "B 単独"; colorClass = "bg-blue-500/10 text-blue-300 border-blue-500/30"; break;
                case 'Y': label = "Y 単独"; colorClass = "bg-amber-500/10 text-amber-300 border-amber-500/30"; break;
                case 'N': label = "N 単独"; colorClass = "bg-pink-500/10 text-pink-300 border-pink-500/30"; break;
            }
            badge.textContent = label;
            badge.className = `text-xs px-2.5 py-0.5 rounded-full font-bold border transition-colors ${colorClass}`;
        }

        function getSelectedSites() {
            const sites = [];
            if (document.getElementById('site-B').checked) sites.push('B');
            if (document.getElementById('site-Y').checked) sites.push('Y');
            if (document.getElementById('site-N').checked) sites.push('N');
            return sites;
        }

        function addTicketRow(comboStr = '', amountVal = 100) {
            const container = document.getElementById('tickets-container');
            const rowId = 'ticket-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
            const div = document.createElement('div');
            div.id = rowId;
            div.className = 'flex items-center gap-2 bg-slate-900/50 p-1.5 rounded-lg border border-slate-700/50 focus-within:border-blue-500/50 transition';
            div.innerHTML = `
                <div class="relative flex-1">
                    <span class="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500"><i class="fa-solid fa-list-ol text-[10px]"></i></span>
                    <input type="text" placeholder="例: 1-2-3" value="${comboStr}" class="ticket-combo w-full bg-slate-800 border-none rounded md py-1.5 pl-7 pr-2 text-sm font-bold text-white focus:outline-none focus:ring-1 focus:ring-blue-500 number-font">
                </div>
                <div class="relative w-1/3 min-w-[100px]">
                    <span class="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500 text-xs font-bold">¥</span>
                    <input type="number" min="100" step="100" value="${amountVal}" oninput="updateTotalInvest()" class="ticket-amount w-full bg-slate-800 border-none rounded md py-1.5 pl-6 pr-2 text-sm font-bold text-white focus:outline-none focus:ring-1 focus:ring-blue-500 number-font text-right">
                                </div>
                <button type="button" onclick="removeTicketRow('${rowId}')" class="text-gray-500 hover:text-rose-500 px-2 py-1 transition">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            `;
            container.appendChild(div);
            updateTotalInvest();
        }

        function removeTicketRow(id) {
            const row = document.getElementById(id);
            if (row) {
                row.remove();
                updateTotalInvest();
                if (document.querySelectorAll('.ticket-amount').length === 0) addTicketRow();
            }
        }

        function updateTotalInvest() {
            let total = 0;
            document.querySelectorAll('.ticket-amount').forEach(input => {
                total += parseInt(input.value) || 0;
            });
            document.getElementById('live-total-invest').textContent = `¥${total.toLocaleString()}`;
        }

        function getTicketsData() {
            const tickets = [];
            const rows = document.querySelectorAll('#tickets-container > div');
            rows.forEach(row => {
                const combo = row.querySelector('.ticket-combo').value.trim();
                const amount = parseInt(row.querySelector('.ticket-amount').value) || 0;
                if (combo || amount > 0) tickets.push({ combo, amount });
            });
            return tickets;
        }

        function saveRace(e) {
            e.preventDefault();
            const sites = getSelectedSites();
            if (sites.length === 0) return alert("推奨サイトを少なくとも1つ選択してください。");
            const tickets = getTicketsData();
            const totalInvest = tickets.reduce((sum, t) => sum + t.amount, 0);
            if (totalInvest === 0 && !confirm("投資額が0円ですが保存しますか？")) return;

            const resultCombo = document.getElementById('result-combo').value.trim();
            const payoutAmount = parseInt(document.getElementById('payout-amount').value) || 0;
            let isHit = false, totalReturn = 0;
            
            if (resultCombo) {
                const hitTicket = tickets.find(t => t.combo === resultCombo);
                if (hitTicket) {
                    isHit = true;
                    totalReturn = (hitTicket.amount / 100) * payoutAmount;
                }
            }

            const raceData = {
                id: document.getElementById('edit-id').value || 'RACE_' + Date.now(),
                date: document.getElementById('date').value,
                raceIdStr: document.getElementById('race-id').value,
                sites: sites,
                patternKey: getPatternKey(sites),
                tickets: tickets,
                totalInvest: totalInvest,
                resultCombo: resultCombo,
                payoutAmount: payoutAmount,
                isHit: isHit,
                totalReturn: totalReturn,
                drawingData: canvas.toDataURL(),
                timestamp: Date.now()
            };

            const existingIndex = races.findIndex(r => r.id === raceData.id);
            if (existingIndex >= 0) races[existingIndex] = raceData;
            else races.unshift(raceData);

            saveData();
            resetForm();
            switchTab('records');
            alert(isHit ? `🎯 的中！ ${totalReturn.toLocaleString()}円の払戻を記録しました` : '保存しました');
        }

        function resetForm() {
            document.getElementById('race-form').reset();
            document.getElementById('edit-id').value = '';
            document.getElementById('save-btn-text').textContent = 'このレースを保存する';
            document.getElementById('date').value = new Date().toISOString().split('T')[0];
            document.getElementById('tickets-container').innerHTML = '';
            addTicketRow();
            updateLivePattern();
            clearCanvas();
        }

        function editRace(id) {
            const race = races.find(r => r.id === id);
            if (!race) return;
            resetForm();
            document.getElementById('edit-id').value = race.id;
            document.getElementById('date').value = race.date;
            document.getElementById('race-id').value = race.raceIdStr || '';
            document.getElementById('site-B').checked = race.sites.includes('B');
            document.getElementById('site-Y').checked = race.sites.includes('Y');
            document.getElementById('site-N').checked = race.sites.includes('N');
            updateLivePattern();
            const tContainer = document.getElementById('tickets-container');
            tContainer.innerHTML = '';
            if (race.tickets && race.tickets.length > 0) race.tickets.forEach(t => addTicketRow(t.combo, t.amount));
            else addTicketRow();
            document.getElementById('result-combo').value = race.resultCombo || '';
            document.getElementById('payout-amount').value = race.payoutAmount || '';
            if (race.drawingData) {
                const img = new Image();
                img.onload = () => { ctx.clearRect(0, 0, canvas.width, canvas.height); ctx.drawImage(img, 0, 0); };
                img.src = race.drawingData;
            }
            document.getElementById('save-btn-text').textContent = '変更を更新する';
            switchTab('input');
        }

        function deleteRace(id) {
            if (confirm("本当にこのレースデータを削除しますか？")) {
                races = races.filter(r => r.id !== id);
                saveData();
            }
        }
        function initCanvas() {
            canvas = document.getElementById('handwriting-canvas');
            ctx = canvas.getContext('2d');
            const rect = canvas.parentElement.getBoundingClientRect();
            canvas.width = rect.width;
            canvas.height = rect.height;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            updateBrush();
            const start = (e) => { isDrawing = true; const pos = getPos(e); ctx.beginPath(); ctx.moveTo(pos.x, pos.y); };
            const move = (e) => { if (!isDrawing) return; e.preventDefault(); const pos = getPos(e); ctx.lineTo(pos.x, pos.y); ctx.stroke(); };
            const stop = () => { isDrawing = false; ctx.closePath(); };
            canvas.addEventListener('mousedown', start); canvas.addEventListener('mousemove', move); canvas.addEventListener('mouseup', stop); canvas.addEventListener('mouseout', stop);
            canvas.addEventListener('touchstart', start, {passive: false}); canvas.addEventListener('touchmove', move, {passive: false}); canvas.addEventListener('touchend', stop);
            window.addEventListener('resize', () => {
                const temp = canvas.toDataURL();
                const pRect = canvas.parentElement.getBoundingClientRect();
                canvas.width = pRect.width; canvas.height = pRect.height;
                updateBrush();
                const img = new Image();
                img.onload = () => ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                img.src = temp;
            });
            document.querySelector('.color-btn').classList.add('ring-2', 'ring-white');
        }

        function getPos(e) {
            const rect = canvas.getBoundingClientRect();
            const clientX = e.touches ? e.touches[0].clientX : e.clientX;
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;
            return { x: clientX - rect.left, y: clientY - rect.top };
        }

        function setCanvasColor(color, btn) {
            currentBrushColor = color; updateBrush();
            document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('ring-2', 'ring-white'));
            if(btn) btn.classList.add('ring-2', 'ring-white');
        }

        function updateBrush() { if(!ctx) return; ctx.strokeStyle = currentBrushColor; ctx.lineWidth = 4; }
        function clearCanvas() { if(ctx && canvas) ctx.clearRect(0, 0, canvas.width, canvas.height); }

        const PATTERNS = [
            { id: 'B_Y_N', label: 'B & Y & N', badgeClass: 'bg-amber-500/20 text-amber-400 border-amber-500/50' },
            { id: 'B_Y', label: 'B & Y', badgeClass: 'bg-blue-500/20 text-blue-400 border-blue-500/50' },
            { id: 'Y_N', label: 'Y & N', badgeClass: 'bg-amber-500/20 text-amber-400 border-amber-500/50' },
            { id: 'B_N', label: 'B & N', badgeClass: 'bg-pink-500/20 text-pink-400 border-pink-500/50' },
            { id: 'B', label: 'B 単独', badgeClass: 'bg-blue-500/10 text-blue-300 border-blue-500/30' },
            { id: 'Y', label: 'Y 単独', badgeClass: 'bg-amber-500/10 text-amber-300 border-amber-500/30' },
            { id: 'N', label: 'N 単独', badgeClass: 'bg-pink-500/10 text-pink-300 border-pink-500/30' }
        ];

        function calculateStats() {
            let totalInvest = 0, totalReturn = 0, totalHits = 0, completedRaces = 0;
            const patternStats = {};
            PATTERNS.forEach(p => patternStats[p.id] = { count: 0, completed: 0, hits: 0, invest: 0, returnAmt: 0 });
            races.forEach(r => {
                const key = r.patternKey;
                if (!patternStats[key]) return;
                patternStats[key].count++;
                if (r.resultCombo) {
                    completedRaces++; totalInvest += r.totalInvest; totalReturn += r.totalReturn;
                    if (r.isHit) totalHits++;
                    patternStats[key].completed++; patternStats[key].invest += r.totalInvest; patternStats[key].returnAmt += r.totalReturn;
                    if (r.isHit) patternStats[key].hits++;
                }
            });
            return { totalInvest, totalReturn, totalHits, completedRaces, patternStats };
        }

        function renderDashboard() {
            const stats = calculateStats();
            const totalProfit = stats.totalReturn - stats.totalInvest;
            const totalHitRate = stats.completedRaces > 0 ? ((stats.totalHits / stats.completedRaces) * 100) : 0;
            const totalRoi = stats.totalInvest > 0 ? ((stats.totalReturn / stats.totalInvest) * 100) : 0;

            document.getElementById('stat-total-races').textContent = races.length;
            document.getElementById('stat-total-invest').textContent = `¥${stats.totalInvest.toLocaleString()}`;
            document.getElementById('stat-total-payout').textContent = `¥${stats.totalReturn.toLocaleString()}`;
            const elProfit = document.getElementById('stat-total-profit');
            elProfit.textContent = `${totalProfit >= 0 ? '+' : ''}¥${totalProfit.toLocaleString()}`;
            elProfit.className = `number-font text-3xl font-bold ${totalProfit > 0 ? 'text-emerald-400' : (totalProfit < 0 ? 'text-rose-400' : 'text-white')}`;
            const elRoi = document.getElementById('stat-total-return');
            elRoi.textContent = `${totalRoi.toFixed(1)}%`;
            elRoi.className = `number-font text-4xl font-black ${totalRoi >= 100 ? 'text-amber-400' : 'text-blue-400'}`;
            document.getElementById('stat-total-hitrate').textContent = `的中率 ${totalHitRate.toFixed(1)}%`;

            const tbody = document.getElementById('patternTableBody');
            if(tbody) tbody.innerHTML = '';
            
            const chartLabels = [], chartRoiData = [], chartHitData = [];
            PATTERNS.forEach(p => {
                const s = stats.patternStats[p.id];
                const roi = s.invest > 0 ? ((s.returnAmt / s.invest) * 100) : 0;
                const hitRate = s.completed > 0 ? ((s.hits / s.completed) * 100) : 0;
                const profit = s.returnAmt - s.invest;

                const elCount = document.getElementById(`pat-${p.id}-count`);
                if (elCount) {
                    elCount.textContent = `${s.count}件`;
                    document.getElementById(`pat-${p.id}-return`).textContent = `${roi.toFixed(1)}%`;
                    document.getElementById(`pat-${p.id}-hit`).textContent = `${hitRate.toFixed(1)}%`;
                    const elProf = document.getElementById(`pat-${p.id}-profit`);
                    elProf.textContent = `${profit >= 0 ? '+' : ''}¥${profit.toLocaleString()}`;
                    elProf.className = `number-font text-2xl font-bold ${profit > 0 ? 'text-emerald-400' : (profit < 0 ? 'text-rose-400' : 'text-white')}`;
                }

                if(tbody) {
                    tbody.innerHTML += `<tr class="border-b border-slate-700/50 hover:bg-slate-800/30 transition"><td class="py-2.5 px-2"><span class="text-xs px-2 py-0.5 rounded border font-bold ${p.badgeClass}">${p.label}</span></td><td class="text-center font-bold text-gray-300">${s.count}</td><td class="text-right number-font text-lg text-emerald-400">${hitRate.toFixed(1)}%</td><td class="text-right number-font text-lg font-bold ${roi >= 100 ? 'text-amber-400' : 'text-gray-300'}">${roi.toFixed(1)}%</td></tr>`;
                }

                chartLabels.push(p.label.replace(/ \(.+\)/, '')); chartRoiData.push(roi); chartHitData.push(hitRate);
            });

            if(document.getElementById('comparisonChart')) renderChart(chartLabels, chartRoiData, chartHitData);
        }

        function renderChart(labels, roiData, hitData) {
            const ctx = document.getElementById('comparisonChart').getContext('2d');
            if (chartInstance) chartInstance.destroy();
            const baselinePlugin = {
                id: 'baseline',
                beforeDraw: (chart) => {
                    const ctx = chart.ctx, yAxis = chart.scales.y, xAxis = chart.scales.x, y100 = yAxis.getPixelForValue(100);
                    if(y100 > yAxis.top && y100 < yAxis.bottom) {
                        ctx.save(); ctx.beginPath(); ctx.moveTo(xAxis.left, y100); ctx.lineTo(xAxis.right, y100); ctx.lineWidth = 1; ctx.strokeStyle = 'rgba(251, 191, 36, 0.5)'; ctx.setLineDash([5, 5]); ctx.stroke();
                        ctx.fillStyle = 'rgba(251, 191, 36, 0.8)'; ctx.font = '10px sans-serif'; ctx.fillText('100% LINE', xAxis.right - 50, y100 - 5); ctx.restore();
                    }
                }
            };
            chartInstance = new Chart(ctx, {
                type: 'bar',
                data: { labels: labels, datasets: [{ label: '回収率 (ROI %)', data: roiData, backgroundColor: 'rgba(59, 130, 246, 0.7)', borderColor: 'rgba(59, 130, 246, 1)', borderWidth: 1, borderRadius: 4, order: 2 }, { label: '的中率 (%)', data: hitData, type: 'line', backgroundColor: 'rgba(16, 185, 129, 1)', borderColor: 'rgba(16, 185, 129, 1)', borderWidth: 2, pointBackgroundColor: 'rgba(16, 185, 129, 1)', pointRadius: 4, tension: 0.3, order: 1 }] },
                options: { responsive: true, maintainAspectRatio: false, interaction: { mode: 'index', intersect: false }, scales: { y: { beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#9ca3af', font: {family: 'Teko', size: 14} } }, x: { grid: { display: false }, ticks: { color: '#9ca3af', font: {size: 10} } } }, plugins: { legend: { labels: { color: '#e5e7eb', font: { size: 11, family: 'Noto Sans JP' } } }, tooltip: { backgroundColor: 'rgba(17, 24, 39, 0.9)', titleFont: { family: 'Noto Sans JP' }, bodyFont: { family: 'Teko', size: 16 } } } },
                plugins: [baselinePlugin]
            });
        }
        function updateRecordCountBadge() { document.getElementById('record-count-badge').textContent = races.length; }

        function renderRecords() {
            const container = document.getElementById('records-container');
            const filter = document.getElementById('filter-pattern').value;
            const sortedRaces = [...races].sort((a, b) => { if (b.date !== a.date) return new Date(b.date) - new Date(a.date); return (b.timestamp || 0) - (a.timestamp || 0); });
            const filtered = sortedRaces.filter(r => filter === 'ALL' || r.patternKey === filter);
            
            container.innerHTML = '';
            if (filtered.length === 0) {
                container.innerHTML = `<div class="text-center py-10 bg-slate-900/50 rounded-xl border border-slate-700/50 text-gray-500"><i class="fa-solid fa-box-open text-3xl mb-2"></i><p class="text-sm">表示するデータがありません</p></div>`; return;
            }

            filtered.forEach(r => {
                const pat = PATTERNS.find(p => p.id === r.patternKey) || { label: '不明', badgeClass: 'bg-slate-700' };
                const net = r.totalReturn - r.totalInvest;
                let ticketSummary = '<span class="text-gray-500 text-xs">買い目なし</span>';
                if (r.tickets && r.tickets.length > 0) {
                    const topTickets = r.tickets.slice(0, 3).map(t => `<span class="bg-slate-800 px-1.5 py-0.5 rounded font-mono">${t.combo}</span>`).join(' ');
                    ticketSummary = topTickets + (r.tickets.length > 3 ? ` <span class="text-[10px] text-gray-500">+${r.tickets.length - 3}</span>` : '');
                }

                container.innerHTML += `
                    <div class="bg-byn-card border border-byn-border rounded-xl p-3 sm:p-4 shadow hover:border-slate-600 transition group flex flex-col sm:flex-row gap-4 relative overflow-hidden">
                        ${r.isHit ? '<div class="absolute top-0 right-0 w-12 h-12 bg-emerald-500/20 transform rotate-45 translate-x-6 -translate-y-6"></div>' : ''}
                        <div class="hidden sm:block w-24 h-24 bg-slate-900 rounded-lg border border-slate-700 shrink-0 overflow-hidden relative cursor-pointer" onclick="openImageModal('${r.drawingData}')">
                            ${r.drawingData ? `<img src="${r.drawingData}" class="w-full h-full object-cover opacity-80 hover:opacity-100 transition">` : `<div class="w-full h-full flex items-center justify-center text-slate-700"><i class="fa-solid fa-image-slash"></i></div>`}
                            <div class="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 hover:opacity-100 transition text-white text-xs"><i class="fa-solid fa-magnifying-glass-plus"></i></div>
                        </div>
                        <div class="flex-1 flex flex-col justify-between">
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <div class="flex items-center gap-2 mb-1"><span class="text-[10px] px-2 py-0.5 rounded border font-bold ${pat.badgeClass}">${pat.label}</span><span class="text-xs text-gray-400 font-medium">${r.date}</span></div>
                                    <h4 class="font-bold text-white text-sm sm:text-base">${r.raceIdStr || '未設定レース'}</h4>
                                </div>
                                <div class="flex items-center gap-1 opacity-100 sm:opacity-0 group-hover:opacity-100 transition">
                                    <button onclick="editRace('${r.id}')" class="w-8 h-8 rounded bg-slate-800 text-blue-400 hover:bg-blue-900 hover:text-white transition flex items-center justify-center"><i class="fa-solid fa-pen text-xs"></i></button>
                                    <button onclick="deleteRace('${r.id}')" class="w-8 h-8 rounded bg-slate-800 text-rose-400 hover:bg-rose-900 hover:text-white transition flex items-center justify-center"><i class="fa-solid fa-trash text-xs"></i></button>
                                </div>
                            </div>
                            <div class="flex flex-col sm:flex-row justify-between items-end sm:items-center gap-2 pt-2 border-t border-slate-800">
                                <div class="w-full sm:w-auto text-xs text-gray-400 flex items-center gap-2"><i class="fa-solid fa-ticket"></i> ${ticketSummary}</div>
                                <div class="w-full sm:w-auto flex items-center justify-between sm:justify-end gap-3 bg-slate-900 sm:bg-transparent p-2 sm:p-0 rounded-lg">
                                    <div class="text-right"><span class="block text-[10px] text-gray-500">結果・配当</span><span class="font-bold text-sm ${r.resultCombo ? (r.isHit ? 'text-amber-400' : 'text-gray-400') : 'text-indigo-400'}">${r.resultCombo ? `${r.resultCombo} (${r.payoutAmount.toLocaleString()}円)` : '⏳ 結果待ち'}</span></div>
                                    <div class="text-right pl-3 border-l border-slate-700"><span class="block text-[10px] text-gray-500">損益</span><span class="number-font font-bold text-lg ${net >= 0 ? 'text-emerald-400' : 'text-rose-400'}">${net > 0 ? '+' : ''}${net.toLocaleString()}</span></div>
                                </div>
                            </div>
                        </div>
                    </div>`;
            });
        }

        function openImageModal(dataUrl) {
            if (!dataUrl) return;
            const modal = document.createElement('div');
            modal.className = 'fixed inset-0 bg-black/95 z-[200] flex items-center justify-center p-4 opacity-0 transition-opacity duration-300';
            modal.onclick = () => { modal.classList.remove('opacity-100'); setTimeout(() => modal.remove(), 300); };
            const img = document.createElement('img'); img.src = dataUrl;
            img.className = 'max-w-full max-h-[90vh] object-contain rounded-lg border border-slate-700 shadow-2xl';
            img.style.transform = 'scale(0.95)'; img.style.transition = 'transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            modal.appendChild(img); document.body.appendChild(modal);
            void modal.offsetWidth; modal.classList.add('opacity-100'); img.style.transform = 'scale(1)';
        }

        function openOcrModal() { document.getElementById('ocr-modal').classList.remove('hidden'); clearOcrBox('arrival'); clearOcrBox('payout'); }
        function closeOcrModal() { document.getElementById('ocr-modal').classList.add('hidden'); }
        function handleGlobalPaste(e) {
            if (!document.getElementById('ocr-modal').classList.contains('hidden')) {
                const items = (e.clipboardData || e.originalEvent.clipboardData).items;
                for (let item of items) {
                    if (item.type.indexOf('image') !== -1) {
                        const file = item.getAsFile();
                        if (!ocrParsedData.arrival.raw) processOcrFile(file, 'arrival'); else processOcrFile(file, 'payout');
                        break;
                    }
                }
            }
        }

        function handleOcrImage(e, type) { if (e.target.files && e.target.files.length > 0) processOcrFile(e.target.files[0], type); }

        async function processOcrFile(file, type) {
            const idle = document.getElementById(`ocr-idle-${type}`), loading = document.getElementById(`ocr-loading-${type}`), preview = document.getElementById(`ocr-preview-${type}`), imgTag = document.getElementById(`ocr-img-${type}`), box = document.getElementById(`ocr-box-${type}`);
            idle.classList.add('hidden'); loading.classList.remove('hidden'); box.classList.remove('border-dashed', 'border-indigo-500/50', 'border-emerald-500/50'); box.classList.add('border-solid', 'border-amber-500');
            const reader = new FileReader(); reader.onload = (e) => { imgTag.src = e.target.result; }; reader.readAsDataURL(file);

            try {
                const { data: { text } } = await Tesseract.recognize(file, 'jpn+eng');
                const lines = text.split('\n'); let currentR = 1; ocrParsedData[type] = { raw: text, races: {} };
                
                lines.forEach(line => {
                    if (type === 'arrival') {
                        if (line.includes('中止')) { ocrParsedData.arrival.races[currentR] = '中止'; currentR++; }
                        else { 
                            const cMatch = line.match(/([1-9])[^0-9\-ー‐]*[-ー‐][^0-9]*([1-9])[^0-9\-ー‐]*[-ー‐][^0-9]*([1-9])/); 
                            if (cMatch && currentR <= 12) { 
                                ocrParsedData.arrival.races[currentR] = `${cMatch[1]}-${cMatch[2]}-${cMatch[3]}`; 
                                currentR++; 
                            } 
                        }
                    } else if (type === 'payout') {
                        if (line.includes('全返還') || line.includes('中止')) { 
                            if (currentR <= 12) {
                                ocrParsedData.payout.races[currentR] = 0; 
                                currentR++; 
                            }
                        }
                        else { 
                            const pMatches = line.match(/([0-9,]+)\s*円/g); 
                            if (pMatches && pMatches.length > 0 && currentR <= 12) { 
                                const lastMatch = pMatches[pMatches.length - 1];
                                const val = parseInt(lastMatch.replace(/[^0-9]/g, '')) || 0; 
                                if (val > 0) { 
                                    ocrParsedData.payout.races[currentR] = val; 
                                    currentR++; 
                                }
                            } 
                        }
                    }
                });
                
                loading.classList.add('hidden'); preview.classList.remove('hidden'); box.classList.remove('border-amber-500');
                if (type === 'arrival') box.classList.add('border-indigo-500'); else box.classList.add('border-emerald-500');
                renderOcrResults();
            } catch(err) {
                loading.classList.add('hidden'); idle.classList.remove('hidden'); box.classList.remove('border-solid', 'border-amber-500'); box.classList.add('border-dashed', 'border-rose-500/50'); alert("画像の読み取りに失敗しました。");
            }
        }

        function clearOcrBox(type) {
            ocrParsedData[type] = {}; document.getElementById(`ocr-input-${type}`).value = ''; document.getElementById(`ocr-preview-${type}`).classList.add('hidden'); document.getElementById(`ocr-idle-${type}`).classList.remove('hidden');
            const box = document.getElementById(`ocr-box-${type}`); box.classList.remove('border-solid', 'border-indigo-500', 'border-emerald-500'); box.className = `border-2 border-dashed border-${type==='arrival'?'indigo':'emerald'}-500/50 hover:border-${type==='arrival'?'indigo':'emerald'}-500 rounded-xl p-4 flex flex-col items-center justify-center text-center cursor-pointer transition bg-${type==='arrival'?'indigo':'emerald'}-500/5 min-h-[160px] relative`;
            renderOcrResults();
        }

        function renderOcrResults() {
            const container = document.getElementById('ocr-results-container'), applyBtn = document.getElementById('ocr-apply-btn'), arrRaces = ocrParsedData.arrival.races || {}, payRaces = ocrParsedData.payout.races || {};
            const allKeys = Array.from(new Set([...Object.keys(arrRaces), ...Object.keys(payRaces)])).map(Number).sort((a,b)=>a-b);
            if (allKeys.length === 0) { container.innerHTML = '<p class="text-xs text-gray-600 text-center py-4">画像をアップロードするとここに結果が表示されます</p>'; applyBtn.disabled = true; return; }
            container.innerHTML = ''; applyBtn.disabled = false;
            allKeys.forEach(r => {
                const c = arrRaces[r] || '', p = payRaces[r] !== undefined ? payRaces[r] : '';
                container.innerHTML += `<div class="flex items-center gap-2 p-2 bg-slate-900 border border-slate-700 rounded-lg"><span class="w-8 text-center font-bold text-white text-xs bg-slate-800 py-1 rounded">${r}R</span><div class="flex-1 flex gap-2"><div class="relative flex-1"><span class="absolute left-2 top-1/2 -translate-y-1/2 text-[10px] text-gray-500">着順</span><input type="text" id="ocr-res-c-${r}" value="${c}" class="w-full bg-slate-800 border-none rounded py-1 pl-8 pr-2 text-xs text-white font-mono focus:ring-1 focus:ring-emerald-500"></div><div class="relative flex-1"><span class="absolute left-2 top-1/2 -translate-y-1/2 text-[10px] text-gray-500">配当</span><input type="number" id="ocr-res-p-${r}" value="${p}" class="w-full bg-slate-800 border-none rounded py-1 pl-8 pr-2 text-xs text-white font-mono text-right focus:ring-1 focus:ring-emerald-500"></div></div></div>`;
            });
        }

        function applyOcrToForm() {
            const arrRaces = ocrParsedData.arrival.races || {}, payRaces = ocrParsedData.payout.races || {};
            const allKeys = Array.from(new Set([...Object.keys(arrRaces), ...Object.keys(payRaces)])).map(Number).sort((a,b)=>a-b);
            if (allKeys.length === 0) return;
            const date = document.getElementById('date').value; let updated = 0;
            allKeys.forEach(r => {
                const combo = document.getElementById(`ocr-res-c-${r}`)?.value.trim() || '', payout = parseInt(document.getElementById(`ocr-res-p-${r}`)?.value) || 0;
                if (!combo && !payout) return;
                const raceIdStr = `${r}R`;
                let target = races.find(x => x.date === date && (x.raceIdStr === raceIdStr || x.raceIdStr.includes(`${r}R`)));
                if (!target) { target = { id: 'RACE_' + Date.now() + Math.random().toString().slice(2, 6), date: date, raceIdStr: raceIdStr, sites: [], patternKey: 'NONE', tickets: [], totalInvest: 100, resultCombo: '', payoutAmount: 0, isHit: false, totalReturn: 0, drawingData: '', timestamp: Date.now() }; races.unshift(target); }
                target.resultCombo = combo; target.payoutAmount = payout;
                if (target.tickets.length > 0 && combo) {
                    const hitTicket = target.tickets.find(t => t.combo === combo);
                    if (hitTicket) { target.isHit = true; target.totalReturn = (hitTicket.amount / 100) * payout; } else { target.isHit = false; target.totalReturn = 0; }
                }
                target.status = 'COMPLETED'; updated++;
            });
            saveData(); closeOcrModal(); switchTab('records'); alert(`${updated}件のレース結果を適用・保存しました！`);
        }

        function exportCSV() {
            if (races.length === 0) return alert('出力するデータがありません');
            let csv = 'ID,日付,レース名,推奨サイト,パターン,投資額,結果着順,3連単配当,払戻金,的中判定\n';
            races.forEach(r => csv += `"${r.id}","${r.date}","${r.raceIdStr}","${r.sites.join('/')}","${r.patternKey}","${r.totalInvest}","${r.resultCombo}","${r.payoutAmount}","${r.totalReturn}","${r.isHit ? '1' : '0'}"\n`);
            const blob = new Blob([new Uint8Array([0xEF, 0xBB, 0xBF]), csv], { type: 'text/csv;charset=utf-8;' }); const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = `byn_pro_analyzer_${new Date().toISOString().split('T')[0]}.csv`; link.click();
        }

        function importCSV(event) {
            const file = event.target.files[0]; if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {
                const text = e.target.result, lines = text.split('\n'); if (lines.length < 2) return alert("データがありません");
                let imported = 0;
                for (let i = 1; i < lines.length; i++) {
                    if (!lines[i].trim()) continue;
                    const row = lines[i].match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g); if (!row || row.length < 10) continue;
                    const clean = (str) => str ? str.replace(/^"|"$/g, '') : '', id = clean(row[0]);
                    if (races.some(r => r.id === id)) continue;
                    const sitesRaw = clean(row[3]), sites = sitesRaw ? sitesRaw.split('/') : [];
                    races.push({ id: id || 'RACE_IMP_' + Date.now() + i, date: clean(row[1]), raceIdStr: clean(row[2]), sites: sites, patternKey: clean(row[4]) || 'NONE', totalInvest: parseInt(clean(row[5])) || 0, tickets: [], resultCombo: clean(row[6]), payoutAmount: parseInt(clean(row[7])) || 0, totalReturn: parseInt(clean(row[8])) || 0, isHit: clean(row[9]) === '1', drawingData: '', timestamp: Date.now() }); imported++;
                }
                if (imported > 0) { saveData(); alert(`${imported}件のデータをインポートしました`); } else alert("インポートできる新しいデータがありませんでした");
                event.target.value = '';
            };
            reader.readAsText(file);
        }

        function loadSampleData() {
            if (!confirm('現在のデータにサンプルデータを追加しますか？')) return;
            races = [...[{ id: 'S1', date: '2026-10-21', raceIdStr: '平塚11R', sites: ['B','Y','N'], patternKey: 'B_Y_N', totalInvest: 3000, tickets: [{combo:'5-1-6', amount: 1000}, {combo:'1-5-6', amount: 2000}], resultCombo: '5-1-6', payoutAmount: 12500, totalReturn: 125000, isHit: true, drawingData: '', timestamp: Date.now()-1000 }, { id: 'S2', date: '2026-10-21', raceIdStr: '平塚12R', sites: ['B','Y'], patternKey: 'B_Y', totalInvest: 1000, tickets: [{combo:'2-4-5', amount: 1000}], resultCombo: '1-2-3', payoutAmount: 980, totalReturn: 0, isHit: false, drawingData: '', timestamp: Date.now() }], ...races];
            saveData(); switchTab('dashboard');
        }

        function openPwaModal() { document.getElementById('pwa-modal').classList.remove('hidden'); }
        function closePwaModal() { document.getElementById('pwa-modal').classList.add('hidden'); }
    </script>
</body>
</html>
"""

# Streamlit上でHTMLを表示（高さは1000pxなどに指定し、スクロール可能にする）
components.html(html_code, height=1000, scrolling=True)

