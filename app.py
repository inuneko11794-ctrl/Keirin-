```html
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
                            siteB: '#3b82f6', // B: Blue
                            siteY: '#eab308', // Y: Yellow
                            siteN: '#ec4899', // N: Pink
                            win: '#10b981',   // Green
                            lose: '#ef4444',  // Red
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
        /* Custom Scrollbar */
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

            <!-- CORE PATTERN ANALYSIS: 7 Detailed Combinations (3-Site / 2-Site / 1-Site) -->
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
                        <!-- B & Y & N Card -->
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
                        <!-- B & Y Pair -->
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

                        <!-- Y & N Pair -->
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

                        <!-- B & N Pair -->
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

                <!-- 1-SITE ONLY SECTION -->
                <div class="space-y-2 pt-2">
                    <div class="text-xs font-bold text-slate-400 flex items-center gap-1.5 uppercase tracking-wider">
                        <i class="fa-solid fa-user"></i> 1サイト単独推奨 (3パターン)
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <!-- B Only -->
                        <div class="bg-byn-card border border-slate-800 rounded-2xl p-4 shadow-md space-y-3">
                            <div class="flex justify-between items-center">
                                <div class="flex items-center gap-2">
                                    <span class="w-6 h-6 rounded-full bg-blue-500/30 text-blue-400 border border-blue-500/50 font-bold text-xs flex items-center justify-center">B</span>
                                    <h3 class="font-extrabold text-white text-base">B のみ</h3>
                                </div>
                                <span id="pat-B-count" class="text-xs text-gray-400 font-bold">0件</span>
                            </div>

                            <div class="grid grid-cols-2 gap-2">
                                <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">回収率</span>
                                    <span id="pat-B-return" class="number-font text-2xl font-black text-slate-300">0.0%</span>
                                </div>
                                <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">的中率</span>
                                    <span id="pat-B-hit" class="number-font text-2xl font-bold text-emerald-400">0.0%</span>
                                </div>
                            </div>

                            <div class="flex justify-between items-center text-xs text-gray-300 pt-1 border-t border-slate-800/80">
                                <span class="text-gray-400">純損益:</span>
                                <span id="pat-B-profit" class="font-bold">¥0</span>
                            </div>
                        </div>

                        <!-- Y Only -->
                        <div class="bg-byn-card border border-slate-800 rounded-2xl p-4 shadow-md space-y-3">
                            <div class="flex justify-between items-center">
                                <div class="flex items-center gap-2">
                                    <span class="w-6 h-6 rounded-full bg-amber-500/30 text-amber-400 border border-amber-500/50 font-bold text-xs flex items-center justify-center">Y</span>
                                    <h3 class="font-extrabold text-white text-base">Y のみ</h3>
                                </div>
                                <span id="pat-Y-count" class="text-xs text-gray-400 font-bold">0件</span>
                            </div>

                            <div class="grid grid-cols-2 gap-2">
                                <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">回収率</span>
                                    <span id="pat-Y-return" class="number-font text-2xl font-black text-slate-300">0.0%</span>
                                </div>
                                <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">的中率</span>
                                    <span id="pat-Y-hit" class="number-font text-2xl font-bold text-emerald-400">0.0%</span>
                                </div>
                            </div>

                            <div class="flex justify-between items-center text-xs text-gray-300 pt-1 border-t border-slate-800/80">
                                <span class="text-gray-400">純損益:</span>
                                <span id="pat-Y-profit" class="font-bold">¥0</span>
                            </div>
                        </div>

                        <!-- N Only -->
                        <div class="bg-byn-card border border-slate-800 rounded-2xl p-4 shadow-md space-y-3">
                            <div class="flex justify-between items-center">
                                <div class="flex items-center gap-2">
                                    <span class="w-6 h-6 rounded-full bg-pink-500/30 text-pink-400 border border-pink-500/50 font-bold text-xs flex items-center justify-center">N</span>
                                    <h3 class="font-extrabold text-white text-base">N のみ</h3>
                                </div>
                                <span id="pat-N-count" class="text-xs text-gray-400 font-bold">0件</span>
                            </div>

                            <div class="grid grid-cols-2 gap-2">
                                <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">回収率</span>
                                    <span id="pat-N-return" class="number-font text-2xl font-black text-slate-300">0.0%</span>
                                </div>
                                <div class="bg-slate-900/80 p-2 rounded-xl border border-slate-800 text-center">
                                    <span class="text-[10px] text-gray-400 block">的中率</span>
                                    <span id="pat-N-hit" class="number-font text-2xl font-bold text-emerald-400">0.0%</span>
                                </div>
                            </div>

                            <div class="flex justify-between items-center text-xs text-gray-300 pt-1 border-t border-slate-800/80">
                                <span class="text-gray-400">純損益:</span>
                                <span id="pat-N-profit" class="font-bold">¥0</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Pattern Comparison Table -->
            <div class="bg-byn-card border border-byn-border rounded-2xl p-5 shadow-lg space-y-3">
                <h3 class="text-sm font-bold text-gray-200 flex items-center gap-2">
                    <i class="fa-solid fa-table-list text-blue-400"></i>
                    全7パターン 一覧比較テーブル
                </h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b border-slate-800 text-gray-400 font-semibold bg-slate-900/60">
                                <th class="p-2.5">パターン</th>
                                <th class="p-2.5">分類</th>
                                <th class="p-2.5 text-right">レース数</th>
                                <th class="p-2.5 text-right">的中数</th>
                                <th class="p-2.5 text-right">的中率</th>
                                <th class="p-2.5 text-right">総投資額</th>
                                <th class="p-2.5 text-right">総払戻額</th>
                                <th class="p-2.5 text-right">純損益</th>
                                <th class="p-2.5 text-right">回収率 (ROI)</th>
                            </tr>
                        </thead>
                        <tbody id="pattern-table-body" class="divide-y divide-slate-800/60 text-gray-300">
                            <!-- Dynamically generated rows -->
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Charts & Difficulty Class Breakdown -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Visual Chart (All 7 Patterns) -->
                <div class="bg-byn-card border border-byn-border rounded-2xl p-5 shadow-lg flex flex-col justify-between">
                    <h3 class="text-sm font-bold text-gray-200 mb-4 flex items-center gap-2">
                        <i class="fa-solid fa-chart-column text-blue-400"></i>
                        全7パターン 回収率・的中率のビジュアルグラフ
                    </h3>
                    <div class="h-64 relative w-full">
                        <canvas id="patternChart"></canvas>
                    </div>
                </div>

                <!-- Difficulty Class Breakdown ("荒れ", "普通", "固い") -->
                <div class="bg-byn-card border border-byn-border rounded-2xl p-5 shadow-lg flex flex-col justify-between">
                    <div>
                        <h3 class="text-sm font-bold text-gray-200 mb-4 flex items-center gap-2">
                            <i class="fa-solid fa-fire text-red-500"></i>
                            レース荒れ度（難易度）別 成績分析
                        </h3>

                        <div class="space-y-4">
                            <!-- 荒れ -->
                            <div class="bg-slate-900/90 p-3.5 rounded-xl border border-red-500/30">
                                <div class="flex justify-between items-center mb-1">
                                    <span class="text-xs font-bold text-red-400 flex items-center gap-1.5">
                                        <i class="fa-solid fa-volcano"></i> 荒れ狙い (波乱・高配当狙い)
                                    </span>
                                    <span id="trend-are-summary" class="text-xs text-gray-300 font-medium">0件 (的中率 0%)</span>
                                </div>
                                <div class="flex justify-between items-baseline">
                                    <span class="text-xs text-gray-400">回収率</span>
                                    <span id="trend-are-return" class="number-font text-2xl font-black text-red-400">0.0%</span>
                                </div>
                                <div class="w-full bg-slate-800 h-2 rounded-full mt-2 overflow-hidden">
                                    <div id="trend-are-bar" class="bg-red-500 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
                                </div>
                            </div>

                            <!-- 普通 -->
                            <div class="bg-slate-900/90 p-3.5 rounded-xl border border-amber-500/30">
                                <div class="flex justify-between items-center mb-1">
                                    <span class="text-xs font-bold text-amber-400 flex items-center gap-1.5">
                                        <i class="fa-solid fa-scale-balanced"></i> 普通 (中穴・中配当)
                                    </span>
                                    <span id="trend-futsu-summary" class="text-xs text-gray-300 font-medium">0件 (的中率 0%)</span>
                                </div>
                                <div class="flex justify-between items-baseline">
                                    <span class="text-xs text-gray-400">回収率</span>
                                    <span id="trend-futsu-return" class="number-font text-2xl font-black text-amber-400">0.0%</span>
                                </div>
                                <div class="w-full bg-slate-800 h-2 rounded-full mt-2 overflow-hidden">
                                    <div id="trend-futsu-bar" class="bg-amber-500 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
                                </div>
                            </div>

                            <!-- 固い -->
                            <div class="bg-slate-900/90 p-3.5 rounded-xl border border-emerald-500/30">
                                <div class="flex justify-between items-center mb-1">
                                    <span class="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                                        <i class="fa-solid fa-shield-halved"></i> 固い (本命・低配当)
                                    </span>
                                    <span id="trend-katai-summary" class="text-xs text-gray-300 font-medium">0件 (的中率 0%)</span>
                                </div>
                                <div class="flex justify-between items-baseline">
                                    <span class="text-xs text-gray-400">回収率</span>
                                    <span id="trend-katai-return" class="number-font text-2xl font-black text-emerald-400">0.0%</span>
                                </div>
                                <div class="w-full bg-slate-800 h-2 rounded-full mt-2 overflow-hidden">
                                    <div id="trend-katai-bar" class="bg-emerald-500 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 2: DETAILED TICKET & RACE ENTRY / EDIT -->
        <section id="tab-input" class="hidden max-w-4xl mx-auto space-y-6">
            <form id="raceForm" onsubmit="handleFormSubmit(event)" class="bg-byn-card border border-byn-border rounded-2xl p-5 sm:p-7 shadow-2xl space-y-6">
                
                <div class="border-b border-byn-border pb-4 flex justify-between items-center">
                    <h2 class="text-lg font-bold text-white flex items-center gap-2">
                        <i class="fa-solid fa-pen-nib text-blue-500"></i>
                        レース結果 ＆ 買い目手書き修正・登録
                    </h2>
                    <div class="flex items-center gap-2">
                        <button type="button" onclick="openOcrModal()" class="px-3 py-1 bg-gradient-to-r from-emerald-600 to-teal-600 hover:opacity-90 text-white text-xs font-bold rounded-lg transition flex items-center gap-1 shadow">
                            <i class="fa-solid fa-camera"></i> 画像読み込み (AI/OCR)
                        </button>
                    </div>
                </div>

                <!-- 1. Site Selection (B, Y, N) -->
                <div>
                    <div class="flex justify-between items-center mb-2">
                        <label class="block text-xs font-bold text-gray-300 uppercase tracking-wider">
                            1. 推奨サイトの選択 (複数選択可) <span class="text-red-400">*</span>
                        </label>
                        <span id="overlap-count-badge" class="text-xs text-gray-400 font-medium px-3 py-1 rounded-lg bg-slate-800 border border-slate-700">
                            サイトを選択してください
                        </span>
                    </div>

                    <div class="grid grid-cols-3 gap-3">
                        <button type="button" id="site-btn-B" onclick="toggleSite('B')" class="site-toggle py-3 rounded-xl border-2 font-black text-base transition flex flex-col items-center justify-center gap-1 border-slate-800 bg-slate-900 text-blue-400 hover:border-blue-500">
                            <span>サイト B</span>
                            <span class="text-[10px] font-normal text-gray-400">推奨</span>
                        </button>

                        <button type="button" id="site-btn-Y" onclick="toggleSite('Y')" class="site-toggle py-3 rounded-xl border-2 font-black text-base transition flex flex-col items-center justify-center gap-1 border-slate-800 bg-slate-900 text-amber-400 hover:border-amber-500">
                            <span>サイト Y</span>
                            <span class="text-[10px] font-normal text-gray-400">推奨</span>
                        </button>

                        <button type="button" id="site-btn-N" onclick="toggleSite('N')" class="site-toggle py-3 rounded-xl border-2 font-black text-base transition flex flex-col items-center justify-center gap-1 border-slate-800 bg-slate-900 text-pink-400 hover:border-pink-500">
                            <span>サイト N</span>
                            <span class="text-[10px] font-normal text-gray-400">推奨</span>
                        </button>
                    </div>
                </div>

                <!-- 2. Race Difficulty Class ("荒れ", "普通", "固い") -->
                <div>
                    <label class="block text-xs font-bold text-gray-300 mb-2 uppercase tracking-wider">
                        2. レースの難易度・荒れ具合 <span class="text-red-400">*</span>
                    </label>
                    <div class="grid grid-cols-3 gap-3">
                        <button type="button" id="trend-btn-are" onclick="selectTrend('荒れ')" class="trend-toggle py-3 px-2 rounded-xl border-2 font-bold text-sm flex items-center justify-center gap-2 transition border-slate-800 bg-slate-900 text-gray-400 hover:border-red-500">
                            <i class="fa-solid fa-volcano text-red-400"></i>
                            <span>荒れ</span>
                        </button>
                        <button type="button" id="trend-btn-futsu" onclick="selectTrend('普通')" class="trend-toggle py-3 px-2 rounded-xl border-2 font-bold text-sm flex items-center justify-center gap-2 transition border-slate-800 bg-slate-900 text-gray-400 hover:border-amber-500">
                            <i class="fa-solid fa-scale-balanced text-amber-400"></i>
                            <span>普通</span>
                        </button>
                        <button type="button" id="trend-btn-katai" onclick="selectTrend('固い')" class="trend-toggle py-3 px-2 rounded-xl border-2 font-bold text-sm flex items-center justify-center gap-2 transition border-slate-800 bg-slate-900 text-gray-400 hover:border-emerald-500">
                            <i class="fa-solid fa-shield-halved text-emerald-400"></i>
                            <span>固い</span>
                        </button>
                    </div>
                </div>

                <!-- 3. Basic Race Details (Date, Track, Race No) -->
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                        <label class="block text-xs font-semibold text-gray-300 mb-1">日付</label>
                        <input type="date" id="input-date" required class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-300 mb-1">開催場 (例: 平塚, 立川)</label>
                        <input type="text" id="input-venue" placeholder="平塚" required class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-300 mb-1">レース番号 (例: 11R)</label>
                        <input type="text" id="input-raceNo" placeholder="11R" required class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
                    </div>
                </div>

                <!-- 4. Detailed Ticket Combinations Builder (買い目詳細) -->
                <div class="space-y-3 bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
                    <div class="flex justify-between items-center">
                        <label class="block text-xs font-bold text-gray-200 uppercase tracking-wider flex items-center gap-1.5">
                            <i class="fa-solid fa-ticket text-amber-400"></i>
                            4. 買い目組み合わせ（券種・組み合わせ・購入額）
                        </label>
                        <button type="button" onclick="addTicketRow()" class="px-2.5 py-1 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-lg transition flex items-center gap-1">
                            <i class="fa-solid fa-plus"></i> 買い目行を追加
                        </button>
                    </div>

                    <!-- Dynamic Ticket Rows Container -->
                    <div id="ticket-rows-container" class="space-y-2">
                        <!-- Default Ticket Row 1 -->
                    </div>

                    <!-- Direct Batch Text Option -->
                    <div class="pt-2 border-t border-slate-800">
                        <label class="block text-[11px] text-gray-400 mb-1">一括買い目メモ（自由入力）</label>
                        <input type="text" id="input-ticket-batch" placeholder="例: 3連単 1-2-3, 1-3-5 各500円" class="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500">
                    </div>
                </div>

                <!-- 5. Advanced Handwriting Canvas with Full Editing Toolbar -->
                <div class="bg-slate-900/80 p-4 rounded-2xl border border-slate-800 space-y-3 shadow-inner">
                    <div class="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-2">
                        <span class="text-xs font-extrabold text-white flex items-center gap-1.5">
                            <i class="fa-solid fa-paintbrush text-pink-400"></i> 手書きメモ ＆ 展開予想キャンバス (消しゴム・修正機能付)
                        </span>

                        <!-- Action Toolbar (Undo, Redo, Clear) -->
                        <div class="flex items-center gap-1.5">
                            <button type="button" onclick="undoCanvas()" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-gray-300 rounded-lg text-xs font-bold transition flex items-center gap-1 border border-slate-700">
                                <i class="fa-solid fa-rotate-left text-blue-400"></i> 元に戻す
                            </button>
                            <button type="button" onclick="redoCanvas()" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-gray-300 rounded-lg text-xs font-bold transition flex items-center gap-1 border border-slate-700">
                                <i class="fa-solid fa-rotate-right text-blue-400"></i> やり直し
                            </button>
                            <button type="button" onclick="clearCanvas()" class="px-2.5 py-1 bg-slate-800 hover:bg-red-900/50 text-red-400 rounded-lg text-xs font-bold transition border border-slate-700">
                                <i class="fa-solid fa-trash-can"></i> 全消去
                            </button>
                        </div>
                    </div>

                    <!-- Tool Modes & Color Palette -->
                    <div class="flex flex-wrap items-center justify-between gap-3 text-xs bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                        <!-- Mode Selector (Pen vs Eraser) -->
                        <div class="flex items-center gap-2">
                            <button type="button" id="tool-pen-btn" onclick="setDrawingTool('pen')" class="px-3 py-1.5 rounded-lg font-bold border transition flex items-center gap-1.5 bg-blue-600 text-white border-blue-400 shadow">
                                <i class="fa-solid fa-pen"></i> ペン
                            </button>
                            <button type="button" id="tool-eraser-btn" onclick="setDrawingTool('eraser')" class="px-3 py-1.5 rounded-lg font-bold border transition flex items-center gap-1.5 bg-slate-800 text-gray-400 border-slate-700 hover:bg-slate-700">
                                <i class="fa-solid fa-eraser text-amber-400"></i> 消しゴム
                            </button>
                        </div>

                        <!-- Pen/Eraser Size Slider -->
                        <div class="flex items-center gap-2 bg-slate-900 px-3 py-1 rounded-lg border border-slate-800">
                            <span class="text-[10px] text-gray-400 font-semibold">太さ:</span>
                            <input type="range" id="penSizeSlider" min="1" max="30" value="3" oninput="setPenSize(this.value)" class="w-20 accent-blue-500 cursor-pointer">
                            <span id="penSizeDisplay" class="number-font text-xs font-bold text-amber-400 w-6">3px</span>
                        </div>

                        <!-- Color Palette -->
                        <div class="flex items-center gap-1.5">
                            <span class="text-[10px] text-gray-400 font-semibold mr-1">色:</span>
                            <button type="button" onclick="selectColor('#ffffff')" class="w-6 h-6 rounded-full bg-white border-2 border-slate-600 focus:scale-110 transition shadow"></button>
                            <button type="button" onclick="selectColor('#f87171')" class="w-6 h-6 rounded-full bg-red-400 border-2 border-slate-600 focus:scale-110 transition shadow"></button>
                            <button type="button" onclick="selectColor('#60a5fa')" class="w-6 h-6 rounded-full bg-blue-400 border-2 border-slate-600 focus:scale-110 transition shadow"></button>
                            <button type="button" onclick="selectColor('#fbbf24')" class="w-6 h-6 rounded-full bg-amber-400 border-2 border-slate-600 focus:scale-110 transition shadow"></button>
                            <button type="button" onclick="selectColor('#34d399')" class="w-6 h-6 rounded-full bg-emerald-400 border-2 border-slate-600 focus:scale-110 transition shadow"></button>
                            <button type="button" onclick="selectColor('#f472b6')" class="w-6 h-6 rounded-full bg-pink-400 border-2 border-slate-600 focus:scale-110 transition shadow"></button>
                        </div>
                    </div>

                    <!-- Canvas Box -->
                    <div class="relative bg-slate-950 rounded-xl border border-slate-800 overflow-hidden h-44 shadow-inner">
                        <canvas id="handwritingCanvas" class="w-full h-full cursor-crosshair"></canvas>
                    </div>
                </div>

                <!-- 6. Investment, Result & Payout -->
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 border-t border-byn-border">
                    <div>
                        <label class="block text-xs font-semibold text-gray-300 mb-1">総投資金額 (円) <span class="text-red-400">*</span></label>
                        <input type="number" id="input-investment" value="1000" min="0" step="100" required class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 font-bold">
                        <div class="flex gap-1 mt-1.5">
                            <button type="button" onclick="addInvestment(1000)" class="px-2 py-0.5 bg-slate-800 text-[10px] text-gray-300 rounded hover:bg-slate-700">+1,000</button>
                            <button type="button" onclick="addInvestment(5000)" class="px-2 py-0.5 bg-slate-800 text-[10px] text-gray-300 rounded hover:bg-slate-700">+5,000</button>
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-semibold text-gray-300 mb-1">勝敗結果</label>
                        <div class="grid grid-cols-2 gap-2">
                            <button type="button" id="result-btn-win" onclick="setResult(true)" class="py-2 rounded-xl border font-bold text-xs transition border-slate-700 bg-slate-800 text-gray-400">
                                <i class="fa-solid fa-circle-check text-emerald-400 mr-1"></i> 的中
                            </button>
                            <button type="button" id="result-btn-lose" onclick="setResult(false)" class="py-2 rounded-lg border font-bold text-xs transition border-slate-700 bg-slate-800 text-gray-400">
                                <i class="fa-solid fa-circle-xmark text-red-400 mr-1"></i> 不的中
                            </button>
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-semibold text-gray-300 mb-1">払戻金額・配当 (円)</label>
                        <input type="number" id="input-payout" value="0" min="0" step="10" required class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 font-bold text-emerald-400">
                    </div>
                </div>

                <!-- Win Result text -->
                <div>
                    <label class="block text-xs font-semibold text-gray-300 mb-1">的中着順・決定買い目 (任意メモ)</label>
                    <input type="text" id="input-winning-combination" placeholder="例: 1着-2着-3着 1-2-3 (配当 48,000円)" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500">
                </div>

                <!-- Submit Button -->
                <button type="submit" id="form-submit-btn" class="w-full py-4 bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:from-blue-500 hover:to-indigo-600 text-white font-extrabold rounded-xl shadow-xl transition text-base flex items-center justify-center gap-2">
                    <i class="fa-solid fa-floppy-disk"></i>
                    レース結果・買い目を保存する
                </button>
            </form>
        </section>

        <!-- TAB 3: RECORDS LIST & FILTER (組み合わせと結果一覧) -->
        <section id="tab-records" class="hidden space-y-4">
            
            <!-- Filters Bar -->
            <div class="bg-byn-card border border-byn-border rounded-2xl p-4 flex flex-wrap gap-3 items-center justify-between shadow-md">
                <div class="flex flex-wrap items-center gap-2">
                    <span class="text-xs text-gray-400 font-medium">絞り込み条件:</span>
                    
                    <!-- Pattern Filter -->
                    <select id="filter-pattern" onchange="renderRecords()" class="bg-slate-900 border border-slate-700 text-xs text-white rounded-lg px-3 py-1.5 focus:outline-none">
                        <option value="ALL">全パターン (7種類)</option>
                        <option value="B_Y_N">3サイト全重複 (B & Y & N)</option>
                        <option value="B_Y">2サイト: B & Y</option>
                        <option value="Y_N">2サイト: Y & N</option>
                        <option value="B_N">2サイト: B & N</option>
                        <option value="B">1サイト: Bのみ</option>
                        <option value="Y">1サイト: Yのみ</option>
                        <option value="N">1サイト: Nのみ</option>
                    </select>

                    <!-- Difficulty Filter -->
                    <select id="filter-trend" onchange="renderRecords()" class="bg-slate-900 border border-slate-700 text-xs text-white rounded-lg px-3 py-1.5 focus:outline-none">
                        <option value="ALL">全ての荒れ度</option>
                        <option value="荒れ">荒れ狙い</option>
                        <option value="普通">普通</option>
                        <option value="固い">固い</option>
                    </select>

                    <!-- Win Filter -->
                    <select id="filter-win" onchange="renderRecords()" class="bg-slate-900 border border-slate-700 text-xs text-white rounded-lg px-3 py-1.5 focus:outline-none">
                        <option value="ALL">全勝敗結果</option>
                        <option value="WIN">的中のみ</option>
                        <option value="LOSE">不的中のみ</option>
                    </select>
                </div>

                <div class="flex items-center gap-2">
                    <button onclick="clearAllData()" class="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 text-xs rounded-lg transition flex items-center gap-1 font-semibold">
                        <i class="fa-solid fa-trash-can"></i> 全データ初期化
                    </button>
                </div>
            </div>

            <!-- Records List Grid -->
            <div id="records-container" class="space-y-3">
                <!-- Dynamically Rendered -->
            </div>
        </section>

    </main>

    <!-- Modal for Handwriting Zoom View -->
    <div id="imageModal" class="fixed inset-0 bg-black/80 z-50 hidden flex items-center justify-center p-4 backdrop-blur-sm" onclick="closeModal()">
        <div class="bg-byn-card border border-byn-border rounded-2xl max-w-lg w-full p-4 space-y-3 shadow-2xl" onclick="event.stopPropagation()">
            <div class="flex justify-between items-center border-b border-byn-border pb-2">
                <h3 class="text-sm font-bold text-white flex items-center gap-1.5">
                    <i class="fa-solid fa-paintbrush text-pink-400"></i> 手書き買い目メモ拡大
                </h3>
                <button onclick="closeModal()" class="text-gray-400 hover:text-white p-1"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>
            <div class="bg-slate-950 p-2 rounded-xl border border-slate-800">
                <img id="modalImg" src="" alt="Handwriting Memo" class="w-full h-auto rounded-lg">
            </div>
            <div class="flex justify-end gap-2 pt-2">
                <button id="modalEditBtn" onclick="" class="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white font-bold rounded-xl text-xs flex items-center gap-1.5 shadow">
                    <i class="fa-solid fa-pen-to-square"></i> このメモをキャンバスに呼び出して修正する
                </button>
            </div>
        </div>
    </div>

    <!-- Modal for PWA / Add to Home Screen Guidance -->
    <div id="pwaModal" class="fixed inset-0 bg-black/80 z-50 hidden flex items-center justify-center p-4 backdrop-blur-sm" onclick="closePwaModal()">
        <div class="bg-byn-card border border-byn-border rounded-2xl max-w-md w-full p-5 space-y-4 shadow-2xl" onclick="event.stopPropagation()">
            <div class="flex justify-between items-center border-b border-byn-border pb-3">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-xl bg-gradient-to-r from-blue-500 via-amber-500 to-pink-500 flex items-center justify-center text-white font-black text-xs shadow">BYN</div>
                    <h3 class="text-base font-bold text-white">ホーム画面に追加・アプリ化</h3>
                </div>
                <button onclick="closePwaModal()" class="text-gray-400 hover:text-white p-1"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>

            <div class="space-y-3 text-xs text-gray-300">
                <p>ホーム画面に追加すると、専用アプリ感覚で一瞬でアプリを起動できます。</p>
                <div class="bg-slate-900 p-3 rounded-xl border border-slate-800 space-y-2">
                    <div class="font-bold text-blue-400">iPhone (Safari):</div>
                    <p class="text-[11px] text-gray-300">1. 下部の共有ボタン <i class="fa-solid fa-arrow-up-from-bracket"></i> をタップ<br>2. 「ホーム画面に追加」を選択</p>
                </div>
                <div class="bg-slate-900 p-3 rounded-xl border border-slate-800 space-y-2">
                    <div class="font-bold text-amber-400">Android (Chrome):</div>
                    <p class="text-[11px] text-gray-300">1. 右上のメニュー <i class="fa-solid fa-ellipsis-vertical"></i> をタップ<br>2. 「ホーム画面に追加」または「アプリをインストール」を選択</p>
                </div>
            </div>

            <button onclick="closePwaModal()" class="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-gray-300 font-bold rounded-xl text-xs">閉じる</button>
        </div>
    </div>

    <!-- Modal for OCR Screenshot Image Analysis -->
    <div id="ocrModal" class="fixed inset-0 bg-black/80 z-50 hidden flex items-center justify-center p-4 backdrop-blur-sm" onclick="closeOcrModal()">
        <div class="bg-byn-card border border-byn-border rounded-2xl max-w-lg w-full p-5 space-y-4 shadow-2xl overflow-y-auto max-h-[90vh]" onclick="event.stopPropagation()">
            <div class="flex justify-between items-center border-b border-byn-border pb-3">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 flex items-center justify-center text-white font-black text-xs shadow">
                        <i class="fa-solid fa-camera text-sm"></i>
                    </div>
                    <div>
                        <h3 class="text-base font-bold text-white">画像スキャン自動入力 (AI/OCR)</h3>
                        <p class="text-[10px] text-gray-400">着順・配当のスクリーンショットから自動抽出</p>
                    </div>
                </div>
                <button onclick="closeOcrModal()" class="text-gray-400 hover:text-white p-1"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>

            <!-- Upload / Paste Dropzone -->
            <div id="ocrDropZone" class="border-2 border-dashed border-slate-700 hover:border-emerald-500 rounded-xl p-5 text-center cursor-pointer transition bg-slate-900/60 flex flex-col items-center justify-center gap-2" onclick="document.getElementById('ocrFileInput').click()">
                <i class="fa-solid fa-cloud-arrow-up text-3xl text-emerald-400"></i>
                <p class="text-xs font-bold text-gray-200">スクリーンショットを選択 または 貼り付け(Ctrl+V)</p>
                <p class="text-[10px] text-gray-400">着順表・配当表の画像 (複数枚同時読み込み可)</p>
                <input type="file" id="ocrFileInput" accept="image/*" multiple class="hidden" onchange="handleOcrFiles(this.files)">
            </div>

            <!-- Previews Container -->
            <div id="ocrImagePreviews" class="flex flex-wrap gap-2 hidden"></div>

            <!-- Progress Bar -->
            <div id="ocrProgressBox" class="hidden space-y-1.5">
                <div class="flex justify-between text-xs text-gray-300">
                    <span id="ocrProgressStatus" class="font-bold flex items-center gap-1">
                        <i class="fa-solid fa-spinner fa-spin text-emerald-400"></i> 画像を解析中...
                    </span>
                    <span id="ocrProgressPercent" class="number-font font-bold text-emerald-400">0%</span>
                </div>
                <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div id="ocrProgressBar" class="bg-gradient-to-r from-emerald-500 to-teal-400 h-full w-0 transition-all duration-200"></div>
                </div>
            </div>

            <!-- Extracted Results Preview & Confirm Form -->
            <div id="ocrResultsBox" class="hidden space-y-3 bg-slate-900/90 p-4 rounded-xl border border-slate-800">
                <h4 class="text-xs font-bold text-emerald-400 flex items-center gap-1.5 border-b border-slate-800 pb-2">
                    <i class="fa-solid fa-wand-magic-sparkles"></i> 抽出されたレース情報
                </h4>

                <div class="grid grid-cols-2 gap-3 text-xs">
                    <div>
                        <label class="block text-gray-400 text-[10px] mb-1">レース番号</label>
                        <input type="text" id="ocr-res-raceNo" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white font-bold text-xs focus:border-emerald-500">
                    </div>
                    <div>
                        <label class="block text-gray-400 text-[10px] mb-1">決定着順 (3連単など)</label>
                        <input type="text" id="ocr-res-combo" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-emerald-400 font-bold text-xs focus:border-emerald-500">
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3 text-xs">
                    <div>
                        <label class="block text-gray-400 text-[10px] mb-1">3連単配当 (円)</label>
                        <input type="number" id="ocr-res-payout3" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white font-bold text-xs focus:border-emerald-500">
                    </div>
                    <div>
                        <label class="block text-gray-400 text-[10px] mb-1">2車単配当 (円)</label>
                        <input type="number" id="ocr-res-payout2" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white font-bold text-xs focus:border-emerald-500">
                    </div>
                </div>

                <div>
                    <label class="block text-gray-400 text-[10px] mb-1">読み取り結果テキスト (参考)</label>
                    <textarea id="ocr-res-raw" rows="2" readonly class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-[10px] text-gray-400 font-mono resize-none"></textarea>
                </div>

                <button onclick="applyOcrToForm()" class="w-full py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:opacity-90 text-white font-extrabold rounded-xl text-xs shadow-lg flex items-center justify-center gap-2">
                    <i class="fa-solid fa-check-double"></i> この内容をフォームに反映する
                </button>
            </div>
        </div>
    </div>

    <!-- JavaScript Application Logic -->
    <script>
        // Pattern Metadata Definitions for 7 Combinations
        const PATTERNS = {
            'B_Y_N': { key: 'B_Y_N', label: 'B & Y & N', group: '3サイト全重複', sites: ['B', 'Y', 'N'], bg: 'bg-amber-500/20', border: 'border-amber-500/40', text: 'text-amber-400' },
            'B_Y':   { key: 'B_Y',   label: 'B & Y',     group: '2サイト重複',   sites: ['B', 'Y'],      bg: 'bg-blue-500/20',  border: 'border-blue-500/40',  text: 'text-blue-400' },
            'Y_N':   { key: 'Y_N',   label: 'Y & N',     group: '2サイト重複',   sites: ['Y', 'N'],      bg: 'bg-amber-500/20', border: 'border-amber-500/40', text: 'text-amber-400' },
            'B_N':   { key: 'B_N',   label: 'B & N',     group: '2サイト重複',   sites: ['B', 'N'],      bg: 'bg-pink-500/20',  border: 'border-pink-500/40',  text: 'text-pink-400' },
            'B':     { key: 'B',     label: 'Bのみ',     group: '1サイト単独',   sites: ['B'],           bg: 'bg-slate-800',    border: 'border-slate-700',    text: 'text-blue-400' },
            'Y':     { key: 'Y',     label: 'Yのみ',     group: '1サイト単独',   sites: ['Y'],           bg: 'bg-slate-800',    border: 'border-slate-700',    text: 'text-amber-400' },
            'N':     { key: 'N',     label: 'Nのみ',     group: '1サイト単独',   sites: ['N'],           bg: 'bg-slate-800',    border: 'border-slate-700',    text: 'text-pink-400' }
        };

        // Application State
        let raceRecords = [];
        let selectedSites = [];
        let selectedTrend = '';
        let isWinResult = true;
        let editingRecordId = null; // ID if editing existing race

        // Advanced Canvas State (Undo/Redo & Eraser)
        let canvas, ctx;
        let isDrawing = false;
        let currentTool = 'pen'; // 'pen' or 'eraser'
        let currentColor = '#ffffff';
        let currentPenSize = 3;
        let undoStack = [];
        let redoStack = [];
        const MAX_UNDO = 20;

        let chartInstance = null;
        let deferredPrompt = null;

        window.onload = function() {
            setupPWA();

            const today = new Date().toISOString().split('T')[0];
            document.getElementById('input-date').value = today;

            setupCanvas();
            addTicketRow();
            loadRecordsFromStorage();
            setResult(true);
            initChart();
            updateAll();
        };

        // Clipboard Paste Listener for Image OCR
        window.addEventListener('paste', function(e) {
            const items = (e.clipboardData || e.originalEvent.clipboardData).items;
            const files = [];
            for (let i = 0; i < items.length; i++) {
                if (items[i].type.indexOf('image') !== -1) {
                    files.push(items[i].getAsFile());
                }
            }
            if (files.length > 0) {
                openOcrModal();
                handleOcrFiles(files);
            }
        });

        // Setup Canvas and Advanced Handwriting Toolset
        function setupCanvas() {
            canvas = document.getElementById('handwritingCanvas');
            if (!canvas) return;
            ctx = canvas.getContext('2d');

            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width || 400;
            canvas.height = rect.height || 176;

            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';

            // Event Listeners for Drawing
            canvas.onmousedown = startDrawing;
            canvas.onmousemove = draw;
            canvas.onmouseup = stopDrawing;
            canvas.onmouseleave = stopDrawing;

            canvas.ontouchstart = handleTouchStart;
            canvas.ontouchmove = handleTouchMove;
            canvas.ontouchend = stopDrawing;

            // Save initial clean state for Undo
            saveCanvasState();
        }

        function setDrawingTool(tool) {
            currentTool = tool;
            const penBtn = document.getElementById('tool-pen-btn');
            const eraserBtn = document.getElementById('tool-eraser-btn');

            if (tool === 'pen') {
                penBtn.className = "px-3 py-1.5 rounded-lg font-bold border transition flex items-center gap-1.5 bg-blue-600 text-white border-blue-400 shadow";
                eraserBtn.className = "px-3 py-1.5 rounded-lg font-bold border transition flex items-center gap-1.5 bg-slate-800 text-gray-400 border-slate-700 hover:bg-slate-700";
            } else {
                eraserBtn.className = "px-3 py-1.5 rounded-lg font-bold border transition flex items-center gap-1.5 bg-amber-600 text-white border-amber-400 shadow";
                penBtn.className = "px-3 py-1.5 rounded-lg font-bold border transition flex items-center gap-1.5 bg-slate-800 text-gray-400 border-slate-700 hover:bg-slate-700";
            }
        }

        function selectColor(color) {
            currentColor = color;
            setDrawingTool('pen');
        }

        function setPenSize(val) {
            currentPenSize = parseInt(val);
            document.getElementById('penSizeDisplay').textContent = `${val}px`;
        }

        function saveCanvasState() {
            if (!ctx || !canvas) return;
            if (undoStack.length >= MAX_UNDO) undoStack.shift();
            undoStack.push(ctx.getImageData(0, 0, canvas.width, canvas.height));
            redoStack = []; // Clear Redo stack on new action
        }

        function undoCanvas() {
            if (undoStack.length > 1) {
                redoStack.push(undoStack.pop());
                const prevState = undoStack[undoStack.length - 1];
                ctx.putImageData(prevState, 0, 0);
            } else if (undoStack.length === 1) {
                redoStack.push(undoStack.pop());
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
        }

        function redoCanvas() {
            if (redoStack.length > 0) {
                const nextState = redoStack.pop();
                undoStack.push(nextState);
                ctx.putImageData(nextState, 0, 0);
            }
        }

        function clearCanvas() {
            if (ctx && canvas) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                saveCanvasState();
            }
        }

        function startDrawing(e) {
            isDrawing = true;
            ctx.beginPath();
            const pos = getPos(e);
            ctx.moveTo(pos.x, pos.y);
        }

        function draw(e) {
            if (!isDrawing) return;
            const pos = getPos(e);

            if (currentTool === 'eraser') {
                ctx.globalCompositeOperation = 'destination-out';
                ctx.lineWidth = currentPenSize * 3; // Eraser slightly wider
            } else {
                ctx.globalCompositeOperation = 'source-over';
                ctx.strokeStyle = currentColor;
                ctx.lineWidth = currentPenSize;
            }

            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
        }

        function stopDrawing() {
            if (isDrawing) {
                isDrawing = false;
                ctx.beginPath();
                saveCanvasState();
            }
        }

        function handleTouchStart(e) {
            e.preventDefault();
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent("mousedown", { clientX: touch.clientX, clientY: touch.clientY });
            canvas.dispatchEvent(mouseEvent);
        }

        function handleTouchMove(e) {
            e.preventDefault();
            const touch = e.touches[0];
            const mouseEvent = new MouseEvent("mousemove", { clientX: touch.clientX, clientY: touch.clientY });
            canvas.dispatchEvent(mouseEvent);
        }

        function getPos(e) {
            const rect = canvas.getBoundingClientRect();
            return {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
        }

        // Load saved DataURL onto Canvas for re-editing
        function loadCanvasFromDataUrl(dataUrl) {
            if (!dataUrl) {
                clearCanvas();
                return;
            }
            const img = new Image();
            img.onload = function() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.globalCompositeOperation = 'source-over';
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                undoStack = [];
                saveCanvasState();
            };
            img.src = dataUrl;
        }

        // Edit Existing Race Record (Recall Saved Data & Handwriting)
        function editRecord(id) {
            const record = raceRecords.find(r => r.id === id);
            if (!record) return;

            editingRecordId = record.id;

            // Fill basic fields
            document.getElementById('input-date').value = record.date;
            document.getElementById('input-venue').value = record.venue;
            document.getElementById('input-raceNo').value = record.raceNo;

            selectedSites = [...record.sites];
            updateSiteButtons();

            selectTrend(record.trend);

            // Rebuild tickets
            const container = document.getElementById('ticket-rows-container');
            container.innerHTML = '';
            if (record.tickets && record.tickets.length > 0) {
                record.tickets.forEach(t => addTicketRow(t.type, t.combo, t.amount, t.odds));
            } else {
                addTicketRow();
            }

            document.getElementById('input-ticket-batch').value = record.batchText || '';
            document.getElementById('input-winning-combination').value = record.winningCombo || '';
            document.getElementById('input-investment').value = record.investment;
            document.getElementById('input-payout').value = record.payout;

            setResult(record.isWin);

            switchTab('input');

            // Load Handwriting into Canvas
            setTimeout(() => {
                setupCanvas();
                if (record.handwriting) {
                    loadCanvasFromDataUrl(record.handwriting);
                } else {
                    clearCanvas();
                }
            }, 150);

            // Update UI Banner
            let editBadge = document.getElementById('editing-mode-badge');
            if (!editBadge) {
                editBadge = document.createElement('div');
                editBadge.id = 'editing-mode-badge';
                document.getElementById('raceForm').prepend(editBadge);
            }
            editBadge.className = "bg-amber-500/20 border border-amber-500/40 p-3 rounded-xl flex justify-between items-center text-xs font-bold text-amber-300 shadow-lg";
            editBadge.innerHTML = `
                <span class="flex items-center gap-1.5">
                    <i class="fa-solid fa-pen-to-square text-amber-400"></i>
                    登録済みレース (${record.venue} ${record.raceNo}) の再修正・編集モード中
                </span>
                <button type="button" onclick="cancelEditingMode()" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-gray-200 rounded-lg text-xs font-bold border border-slate-700">
                    新規作成に戻る
                </button>
            `;

            const submitBtn = document.getElementById('form-submit-btn');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fa-solid fa-arrows-rotate"></i> 修正内容・手書きメモを上書き保存する';
                submitBtn.className = "w-full py-4 bg-gradient-to-r from-amber-600 via-orange-600 to-amber-700 hover:opacity-90 text-white font-extrabold rounded-xl shadow-xl transition text-base flex items-center justify-center gap-2";
            }

            closeModal();
        }

        function cancelEditingMode() {
            editingRecordId = null;
            const editBadge = document.getElementById('editing-mode-badge');
            if (editBadge) editBadge.remove();

            document.getElementById('ticket-rows-container').innerHTML = '';
            addTicketRow();
            document.getElementById('input-ticket-batch').value = '';
            document.getElementById('input-winning-combination').value = '';
            clearCanvas();
            selectedSites = [];
            selectedTrend = '';
            updateSiteButtons();
            selectTrend('');
            setResult(true);

            const submitBtn = document.getElementById('form-submit-btn');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> レース結果・買い目を保存する';
                submitBtn.className = "w-full py-4 bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:from-blue-500 hover:to-indigo-600 text-white font-extrabold rounded-xl shadow-xl transition text-base flex items-center justify-center gap-2";
            }
        }

        // Form Submit Handler (Create or Update)
        function handleFormSubmit(e) {
            e.preventDefault();

            if (selectedSites.length === 0) {
                alert('荒れ予想を挙げたサイト（B, Y, N）を1つ以上選択してください。');
                return;
            }
            if (!selectedTrend) {
                alert('レースの荒れ度（難易度）を選択してください。');
                return;
            }

            const ticketRows = [];
            document.querySelectorAll('#ticket-rows-container > div').forEach(row => {
                const type = row.querySelector('.ticket-type').value;
                const combo = row.querySelector('.ticket-combo').value;
                const amount = parseInt(row.querySelector('.ticket-amount').value || 0);
                const odds = row.querySelector('.ticket-odds').value;
                if (combo) {
                    ticketRows.push({ type, combo, amount, odds });
                }
            });

            const batchText = document.getElementById('input-ticket-batch').value;
            const investment = parseInt(document.getElementById('input-investment').value) || 0;
            const payout = isWinResult ? (parseInt(document.getElementById('input-payout').value) || 0) : 0;

            // Canvas Check
            let canvasData = null;
            const pixelData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
            let hasDrawing = false;
            for (let i = 3; i < pixelData.length; i += 4) {
                if (pixelData[i] > 0) {
                    hasDrawing = true;
                    break;
                }
            }
            if (hasDrawing) {
                canvasData = canvas.toDataURL();
            }

            const patternKey = getPatternKey(selectedSites);

            if (editingRecordId) {
                // Update Existing Record
                const idx = raceRecords.findIndex(r => r.id === editingRecordId);
                if (idx > -1) {
                    raceRecords[idx] = {
                        ...raceRecords[idx],
                        date: document.getElementById('input-date').value,
                        venue: document.getElementById('input-venue').value,
                        raceNo: document.getElementById('input-raceNo').value,
                        sites: [...selectedSites],
                        patternKey: patternKey,
                        overlapCount: selectedSites.length,
                        trend: selectedTrend,
                        tickets: ticketRows,
                        batchText: batchText,
                        winningCombo: document.getElementById('input-winning-combination').value || '',
                        handwriting: canvasData,
                        investment: investment,
                        isWin: isWinResult,
                        payout: payout,
                        profit: payout - investment,
                        updatedAt: Date.now()
                    };
                }
                alert('レース記録と手書きメモを更新しました！');
            } else {
                // Insert New Record
                const record = {
                    id: Date.now().toString(),
                    date: document.getElementById('input-date').value,
                    venue: document.getElementById('input-venue').value,
                    raceNo: document.getElementById('input-raceNo').value,
                    sites: [...selectedSites],
                    patternKey: patternKey,
                    overlapCount: selectedSites.length,
                    trend: selectedTrend,
                    tickets: ticketRows,
                    batchText: batchText,
                    winningCombo: document.getElementById('input-winning-combination').value || '',
                    handwriting: canvasData,
                    investment: investment,
                    isWin: isWinResult,
                    payout: payout,
                    profit: payout - investment,
                    createdAt: Date.now()
                };
                raceRecords.unshift(record);
                alert('新規レース記録を保存しました！');
            }

            cancelEditingMode();
            updateAll();
            switchTab('dashboard');
        }

        // Helper to get Pattern Key
        function getPatternKey(sitesArray) {
            if (!sitesArray || sitesArray.length === 0) return null;
            const sorted = [...sitesArray].sort();
            return sorted.join('_');
        }

        // Ticket Rows Builder
        function addTicketRow(betType = '3連単', combo = '', amount = 100, odds = '') {
            const container = document.getElementById('ticket-rows-container');
            const rowId = 't-row-' + Date.now() + '-' + Math.random().toString(36).substr(2, 4);

            const row = document.createElement('div');
            row.id = rowId;
            row.className = "flex flex-wrap sm:flex-nowrap items-center gap-2 bg-slate-950/80 p-2 rounded-xl border border-slate-800";

            row.innerHTML = `
                <select class="ticket-type bg-slate-900 border border-slate-700 text-xs text-white rounded-lg px-2 py-1.5 focus:outline-none w-24">
                    <option value="3連単" ${betType === '3連単' ? 'selected' : ''}>3連単</option>
                    <option value="3連複" ${betType === '3連複' ? 'selected' : ''}>3連複</option>
                    <option value="2連単" ${betType === '2連単' ? 'selected' : ''}>2連単</option>
                    <option value="2連複" ${betType === '2連複' ? 'selected' : ''}>2連複</option>
                    <option value="ワイド" ${betType === 'ワイド' ? 'selected' : ''}>ワイド</option>
                    <option value="単勝" ${betType === '単勝' ? 'selected' : ''}>単勝</option>
                </select>
                <input type="text" placeholder="買い目 (例: 1-2-3)" value="${combo}" class="ticket-combo bg-slate-900 border border-slate-700 text-xs text-white rounded-lg px-2.5 py-1.5 focus:outline-none flex-1 min-w-[120px]">
                <div class="flex items-center gap-1 w-28">
                    <span class="text-[10px] text-gray-500">¥</span>
                    <input type="number" placeholder="金額" value="${amount}" min="100" step="100" oninput="recalculateTotalBet()" class="ticket-amount bg-slate-900 border border-slate-700 text-xs text-white rounded-lg px-2 py-1.5 focus:outline-none w-full">
                </div>
                <div class="flex items-center gap-1 w-20">
                    <span class="text-[10px] text-gray-500">倍</span>
                    <input type="number" placeholder="オッズ" value="${odds}" step="0.1" class="ticket-odds bg-slate-900 border border-slate-700 text-xs text-white rounded-lg px-2 py-1.5 focus:outline-none w-full">
                </div>
                <button type="button" onclick="removeTicketRow('${rowId}')" class="text-gray-500 hover:text-red-400 p-1">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            `;

            container.appendChild(row);
            recalculateTotalBet();
        }

        function removeTicketRow(rowId) {
            const container = document.getElementById('ticket-rows-container');
            if (container.children.length > 1) {
                const el = document.getElementById(rowId);
                if (el) el.remove();
                recalculateTotalBet();
            } else {
                alert('少なくとも1つの買い目行が必要です。');
            }
        }

        function recalculateTotalBet() {
            let total = 0;
            document.querySelectorAll('.ticket-amount').forEach(inp => {
                total += parseInt(inp.value || 0);
            });
            if (total > 0) {
                document.getElementById('input-investment').value = total;
            }
        }

        // Navigation Tabs
        function switchTab(tabName) {
            document.getElementById('tab-dashboard').classList.add('hidden');
            document.getElementById('tab-input').classList.add('hidden');
            document.getElementById('tab-records').classList.add('hidden');

            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('border-blue-500', 'text-blue-400');
                btn.classList.add('border-transparent', 'text-gray-400');
            });

            document.getElementById(`tab-${tabName}`).classList.remove('hidden');
            const activeBtn = document.getElementById(`tab-${tabName}-btn`);
            activeBtn.classList.add('border-blue-500', 'text-blue-400');
            activeBtn.classList.remove('border-transparent', 'text-gray-400');

            if (tabName === 'input') {
                setTimeout(setupCanvas, 100);
            }
        }

        function toggleSite(site) {
            const idx = selectedSites.indexOf(site);
            if (idx > -1) {
                selectedSites.splice(idx, 1);
            } else {
                selectedSites.push(site);
            }
            updateSiteButtons();
        }

        function updateSiteButtons() {
            ['B', 'Y', 'N'].forEach(s => {
                const btn = document.getElementById(`site-btn-${s}`);
                if (selectedSites.includes(s)) {
                    btn.classList.add('border-blue-500', 'bg-blue-500/20');
                    btn.classList.remove('border-slate-800', 'bg-slate-900');
                } else {
                    btn.classList.remove('border-blue-500', 'bg-blue-500/20');
                    btn.classList.add('border-slate-800', 'bg-slate-900');
                }
            });

            const pKey = getPatternKey(selectedSites);
            const badge = document.getElementById('overlap-count-badge');
            if (pKey && PATTERNS[pKey]) {
                const info = PATTERNS[pKey];
                badge.textContent = `[${info.group}] ${info.label}`;
                badge.className = `${info.text} font-bold px-3 py-1 rounded-lg ${info.bg} border ${info.border}`;
            } else {
                badge.textContent = 'サイトを選択してください';
                badge.className = 'text-gray-400 font-medium px-3 py-1 rounded-lg bg-slate-800 border border-slate-700';
            }
        }

        function selectTrend(trend) {
            selectedTrend = trend;
            const map = { '荒れ': 'are', '普通': 'futsu', '固い': 'katai' };
            ['荒れ', '普通', '固い'].forEach(t => {
                const btn = document.getElementById(`trend-btn-${map[t]}`);
                if (t === trend) {
                    btn.classList.add('border-blue-500', 'bg-blue-500/20', 'text-white');
                    btn.classList.remove('border-slate-800', 'bg-slate-900', 'text-gray-400');
                } else {
                    btn.classList.remove('border-blue-500', 'bg-blue-500/20', 'text-white');
                    btn.classList.add('border-slate-800', 'bg-slate-900', 'text-gray-400');
                }
            });
        }

        function setResult(isWin) {
            isWinResult = isWin;
            const winBtn = document.getElementById('result-btn-win');
            const loseBtn = document.getElementById('result-btn-lose');
            const payoutInput = document.getElementById('input-payout');

            if (isWin) {
                winBtn.className = "py-2 rounded-xl border font-bold text-xs transition border-emerald-500 bg-emerald-500/20 text-emerald-400";
                loseBtn.className = "py-2 rounded-lg border font-bold text-xs transition border-slate-700 bg-slate-800 text-gray-400";
            } else {
                winBtn.className = "py-2 rounded-lg border font-bold text-xs transition border-slate-700 bg-slate-800 text-gray-400";
                loseBtn.className = "py-2 rounded-xl border font-bold text-xs transition border-red-500 bg-red-500/20 text-red-400";
                payoutInput.value = 0;
            }
        }

        function addInvestment(amount) {
            const el = document.getElementById('input-investment');
            el.value = parseInt(el.value || 0) + amount;
        }

        // Stats Update & History Rendering
        function updateAll() {
            saveRecordsToStorage();
            calculateStats();
            renderRecords();
            updateChart();
            document.getElementById('record-count-badge').textContent = raceRecords.length;
        }

        function calculateStats() {
            const totalCount = raceRecords.length;
            let totalInvest = 0;
            let totalPayout = 0;
            let totalWins = 0;

            const patternStats = {};
            Object.keys(PATTERNS).forEach(pk => {
                patternStats[pk] = { count: 0, invest: 0, payout: 0, wins: 0 };
            });

            const trendStats = {
                '荒れ': { count: 0, invest: 0, payout: 0, wins: 0 },
                '普通': { count: 0, invest: 0, payout: 0, wins: 0 },
                '固い': { count: 0, invest: 0, payout: 0, wins: 0 }
            };

            raceRecords.forEach(r => {
                totalInvest += r.investment;
                totalPayout += r.payout;
                if (r.isWin) totalWins++;

                const pk = r.patternKey || getPatternKey(r.sites);
                if (patternStats[pk]) {
                    patternStats[pk].count++;
                    patternStats[pk].invest += r.investment;
                    patternStats[pk].payout += r.payout;
                    if (r.isWin) patternStats[pk].wins++;
                }

                if (trendStats[r.trend]) {
                    trendStats[r.trend].count++;
                    trendStats[r.trend].invest += r.investment;
                    trendStats[r.trend].payout += r.payout;
                    if (r.isWin) trendStats[r.trend].wins++;
                }
            });

            const totalProfit = totalPayout - totalInvest;
            const totalReturn = totalInvest > 0 ? ((totalPayout / totalInvest) * 100).toFixed(1) : '0.0';
            const totalHitRate = totalCount > 0 ? ((totalWins / totalCount) * 100).toFixed(1) : '0.0';

            document.getElementById('stat-total-races').textContent = totalCount;
            document.getElementById('stat-total-invest').textContent = `¥${totalInvest.toLocaleString()}`;
            document.getElementById('stat-total-payout').textContent = `¥${totalPayout.toLocaleString()}`;
            
            const profitEl = document.getElementById('stat-total-profit');
            profitEl.textContent = `${totalProfit >= 0 ? '+' : ''}¥${totalProfit.toLocaleString()}`;
            profitEl.className = `number-font text-3xl font-bold ${totalProfit >= 0 ? 'text-emerald-400' : 'text-red-400'}`;

            document.getElementById('stat-total-return').textContent = `${totalReturn}%`;
            document.getElementById('stat-total-hitrate').textContent = `的中率 ${totalHitRate}%`;

            Object.keys(PATTERNS).forEach(pk => {
                const st = patternStats[pk];
                const ret = st.invest > 0 ? ((st.payout / st.invest) * 100).toFixed(1) : '0.0';
                const hit = st.count > 0 ? ((st.wins / st.count) * 100).toFixed(1) : '0.0';
                const prof = st.payout - st.invest;

                const retEl = document.getElementById(`pat-${pk}-return`);
                const hitEl = document.getElementById(`pat-${pk}-hit`);
                const countEl = document.getElementById(`pat-${pk}-count`);
                const profEl = document.getElementById(`pat-${pk}-profit`);

                if (retEl) retEl.textContent = `${ret}%`;
                if (hitEl) hitEl.textContent = `${hit}%`;
                if (countEl) countEl.textContent = `${st.count}件`;
                if (profEl) {
                    profEl.textContent = `${prof >= 0 ? '+' : ''}¥${prof.toLocaleString()}`;
                    profEl.className = `number-font ${pk === 'B_Y_N' ? 'text-2xl font-bold' : ''} ${prof >= 0 ? 'text-emerald-400' : 'text-red-400'}`;
                }
            });

            // Table Body
            const tbody = document.getElementById('pattern-table-body');
            tbody.innerHTML = '';
            
            Object.keys(PATTERNS).forEach(pk => {
                const info = PATTERNS[pk];
                const st = patternStats[pk];
                const ret = st.invest > 0 ? ((st.payout / st.invest) * 100).toFixed(1) : '0.0';
                const hit = st.count > 0 ? ((st.wins / st.count) * 100).toFixed(1) : '0.0';
                const prof = st.payout - st.invest;

                const tr = document.createElement('tr');
                tr.className = "hover:bg-slate-900/80 transition";
                tr.innerHTML = `
                    <td class="p-2.5 font-bold ${info.text}">${info.label}</td>
                    <td class="p-2.5 text-gray-400">${info.group}</td>
                    <td class="p-2.5 text-right font-bold text-white">${st.count}</td>
                    <td class="p-2.5 text-right text-emerald-400 font-bold">${st.wins}</td>
                    <td class="p-2.5 text-right font-bold text-emerald-400">${hit}%</td>
                    <td class="p-2.5 text-right font-mono text-gray-300">¥${st.invest.toLocaleString()}</td>
                    <td class="p-2.5 text-right font-mono text-gray-300">¥${st.payout.toLocaleString()}</td>
                    <td class="p-2.5 text-right font-mono font-bold ${prof >= 0 ? 'text-emerald-400' : 'text-red-400'}">${prof >= 0 ? '+' : ''}¥${prof.toLocaleString()}</td>
                    <td class="p-2.5 text-right font-mono font-black text-sm ${parseFloat(ret) >= 100 ? 'text-amber-400' : 'text-blue-400'}">${ret}%</td>
                `;
                tbody.appendChild(tr);
            });

            const trendMap = { '荒れ': 'are', '普通': 'futsu', '固い': 'katai' };
            ['荒れ', '普通', '固い'].forEach(t => {
                const key = trendMap[t];
                const st = trendStats[t];
                const ret = st.invest > 0 ? ((st.payout / st.invest) * 100).toFixed(1) : '0.0';
                const hit = st.count > 0 ? ((st.wins / st.count) * 100).toFixed(1) : '0.0';

                document.getElementById(`trend-${key}-return`).textContent = `${ret}%`;
                document.getElementById(`trend-${key}-summary`).textContent = `${st.count}件 (的中率 ${hit}%)`;
                
                const barWidth = Math.min(parseFloat(ret), 200) / 2;
                document.getElementById(`trend-${key}-bar`).style.width = `${barWidth}%`;
            });
        }

        function renderRecords() {
            const container = document.getElementById('records-container');
            container.innerHTML = '';

            const fPattern = document.getElementById('filter-pattern').value;
            const fTrend = document.getElementById('filter-trend').value;
            const fWin = document.getElementById('filter-win').value;

            const filtered = raceRecords.filter(r => {
                const pk = r.patternKey || getPatternKey(r.sites);
                if (fPattern !== 'ALL' && pk !== fPattern) return false;
                if (fTrend !== 'ALL' && r.trend !== fTrend) return false;
                if (fWin === 'WIN' && !r.isWin) return false;
                if (fWin === 'LOSE' && r.isWin) return false;
                return true;
            });

            if (filtered.length === 0) {
                container.innerHTML = `
                    <div class="text-center py-12 bg-byn-card border border-byn-border rounded-2xl text-gray-400">
                        <i class="fa-solid fa-receipt text-3xl mb-2 block text-gray-600"></i>
                        条件に合致するレース履歴がありません
                    </div>
                `;
                return;
            }

            filtered.forEach(r => {
                const pk = r.patternKey || getPatternKey(r.sites);
                const pInfo = PATTERNS[pk] || { label: r.sites.join(' & '), text: 'text-gray-300', bg: 'bg-slate-800' };

                const card = document.createElement('div');
                card.className = "bg-byn-card border border-byn-border rounded-2xl p-4 sm:p-5 shadow-lg flex flex-col md:flex-row justify-between gap-4 transition hover:border-slate-700";

                const siteBadges = r.sites.map(s => {
                    const colorMap = { 'B': 'bg-blue-500/20 text-blue-400 border-blue-500/30', 'Y': 'bg-amber-500/20 text-amber-400 border-amber-500/30', 'N': 'bg-pink-500/20 text-pink-400 border-pink-500/30' };
                    return `<span class="px-2 py-0.5 rounded-md text-xs font-black border ${colorMap[s]}">${s}</span>`;
                }).join(' ');

                const trendTagMap = {
                    '荒れ': '<span class="px-2 py-0.5 rounded text-xs font-semibold bg-red-500/20 text-red-400 border border-red-500/30"><i class="fa-solid fa-volcano"></i> 荒れ</span>',
                    '普通': '<span class="px-2 py-0.5 rounded text-xs font-semibold bg-amber-500/20 text-amber-400 border border-amber-500/30"><i class="fa-solid fa-scale-balanced"></i> 普通</span>',
                    '固い': '<span class="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"><i class="fa-solid fa-shield-halved"></i> 固い</span>'
                };

                const resultBadge = r.isWin 
                    ? `<span class="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"><i class="fa-solid fa-circle-check"></i> 的中</span>`
                    : `<span class="px-3 py-1 rounded-full text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/30"><i class="fa-solid fa-circle-xmark"></i> 不的中</span>`;

                let ticketsHTML = '';
                if (r.tickets && r.tickets.length > 0) {
                    ticketsHTML = r.tickets.map(t => 
                        `<span class="inline-flex items-center gap-1 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded text-xs text-gray-200">
                            <span class="text-[10px] text-amber-400 font-bold">${t.type}</span>
                            <span class="font-bold text-white">${t.combo}</span>
                            <span class="text-[10px] text-gray-400">¥${t.amount.toLocaleString()}</span>
                            ${t.odds ? `<span class="text-[10px] text-emerald-400">(${t.odds}倍)</span>` : ''}
                        </span>`
                    ).join(' ');
                }

                const raceRoi = r.investment > 0 ? ((r.payout / r.investment) * 100).toFixed(1) : '0.0';

                card.innerHTML = `
                    <div class="space-y-3 flex-1">
                        <div class="flex flex-wrap items-center gap-2">
                            <span class="text-xs text-gray-400">${r.date}</span>
                            <span class="text-sm font-black text-white px-2.5 py-0.5 bg-slate-800 rounded-lg border border-slate-700">${r.venue} ${r.raceNo}</span>
                            <div class="flex items-center gap-1">${siteBadges}</div>
                            <span class="px-2 py-0.5 rounded text-xs font-bold ${pInfo.bg} ${pInfo.text} border border-slate-700">${pInfo.label}</span>
                            ${trendTagMap[r.trend] || ''}
                        </div>

                        <div class="space-y-1">
                            <div class="text-xs text-gray-400 font-semibold">購入買い目一覧:</div>
                            <div class="flex flex-wrap gap-1.5">${ticketsHTML || '<span class="text-xs text-gray-400">なし</span>'}</div>
                            ${r.batchText ? `<div class="text-xs text-gray-300 italic bg-slate-900/50 p-1.5 rounded border border-slate-800/80">メモ: ${r.batchText}</div>` : ''}
                            ${r.winningCombo ? `<div class="text-xs text-emerald-400 font-bold mt-1"><i class="fa-solid fa-trophy mr-1"></i>決定着順: ${r.winningCombo}</div>` : ''}
                        </div>
                    </div>

                    <div class="flex flex-col sm:flex-row md:flex-col items-start sm:items-center md:items-end justify-between md:justify-center gap-3 border-t md:border-t-0 border-byn-border pt-3 md:pt-0">
                        <div class="flex items-center gap-2">
                            ${r.handwriting ? `
                                <button onclick="openModal('${r.handwriting}', '${r.id}')" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs text-pink-400 rounded-lg border border-slate-700 flex items-center gap-1 shadow">
                                    <i class="fa-solid fa-image"></i> 手書き表示
                                </button>
                            ` : ''}
                            ${resultBadge}
                        </div>

                        <div class="text-left md:text-right">
                            <div class="text-xs text-gray-400">
                                投資 ¥${r.investment.toLocaleString()} / 払戻 ¥${r.payout.toLocaleString()}
                                <span class="ml-1 text-blue-400 font-bold">(回収率 ${raceRoi}%)</span>
                            </div>
                            <div class="number-font text-2xl font-black ${r.profit >= 0 ? 'text-emerald-400' : 'text-red-400'}">
                                ${r.profit >= 0 ? '+' : ''}¥${r.profit.toLocaleString()}
                            </div>
                        </div>

                        <div class="flex items-center gap-2">
                            <button onclick="editRecord('${r.id}')" class="px-3 py-1 bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/40 text-xs font-bold rounded-lg transition flex items-center gap-1">
                                <i class="fa-solid fa-pen-to-square"></i> 修正・再手書き
                            </button>
                            <button onclick="deleteRecord('${r.id}')" class="text-xs text-gray-500 hover:text-red-400 transition p-1">
                                <i class="fa-solid fa-trash-can"></i>
                            </button>
                        </div>
                    </div>
                `;

                container.appendChild(card);
            });
        }

        function openModal(imgData, recordId) {
            document.getElementById('modalImg').src = imgData;
            const modalEditBtn = document.getElementById('modalEditBtn');
            if (recordId) {
                modalEditBtn.onclick = function() { editRecord(recordId); };
                modalEditBtn.classList.remove('hidden');
            } else {
                modalEditBtn.classList.add('hidden');
            }
            document.getElementById('imageModal').classList.remove('hidden');
        }

        function closeModal() {
            document.getElementById('imageModal').classList.add('hidden');
        }

        function deleteRecord(id) {
            if (confirm('このレース記録を削除しますか？')) {
                raceRecords = raceRecords.filter(r => r.id !== id);
                updateAll();
            }
        }

        // Chart.js Setup
        function initChart() {
            const ctxChart = document.getElementById('patternChart').getContext('2d');
            const patternKeys = Object.keys(PATTERNS);
            const patternLabels = patternKeys.map(k => PATTERNS[k].label);

            chartInstance = new Chart(ctxChart, {
                type: 'bar',
                data: {
                    labels: patternLabels,
                    datasets: [
                        {
                            label: '回収率 (ROI %)',
                            data: [0, 0, 0, 0, 0, 0, 0],
                            backgroundColor: '#3b82f6',
                            borderRadius: 6,
                        },
                        {
                            label: '的中率 (%)',
                            data: [0, 0, 0, 0, 0, 0, 0],
                            backgroundColor: '#10b981',
                            borderRadius: 6,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#94a3b8', font: { family: 'Noto Sans JP', weight: 'bold' } } }
                    },
                    scales: {
                        x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: '#1e293b' } },
                        y: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' }, beginAtZero: true }
                    }
                }
            });
        }

        function updateChart() {
            if (!chartInstance) return;

            const patternKeys = Object.keys(PATTERNS);
            const patternStats = {};
            patternKeys.forEach(pk => patternStats[pk] = { invest: 0, payout: 0, count: 0, wins: 0 });

            raceRecords.forEach(r => {
                const pk = r.patternKey || getPatternKey(r.sites);
                if (patternStats[pk]) {
                    patternStats[pk].invest += r.investment;
                    patternStats[pk].payout += r.payout;
                    patternStats[pk].count++;
                    if (r.isWin) patternStats[pk].wins++;
                }
            });

            const returns = patternKeys.map(pk => patternStats[pk].invest > 0 ? parseFloat(((patternStats[pk].payout / patternStats[pk].invest) * 100).toFixed(1)) : 0);
            const hits = patternKeys.map(pk => patternStats[pk].count > 0 ? parseFloat(((patternStats[pk].wins / patternStats[pk].count) * 100).toFixed(1)) : 0);

            chartInstance.data.datasets[0].data = returns;
            chartInstance.data.datasets[1].data = hits;
            chartInstance.update();
        }

        function saveRecordsToStorage() {
            localStorage.setItem('byn_race_analyzer_v3', JSON.stringify(raceRecords));
        }

        function loadRecordsFromStorage() {
            const data = localStorage.getItem('byn_race_analyzer_v3') || localStorage.getItem('byn_race_analyzer_v2');
            if (data) {
                try {
                    raceRecords = JSON.parse(data);
                    raceRecords.forEach(r => {
                        if (!r.patternKey && r.sites) {
                            r.patternKey = getPatternKey(r.sites);
                        }
                    });
                } catch(e) {
                    raceRecords = [];
                }
            }
        }

        function clearAllData() {
            if (confirm('すべてのデータが初期化されます。よろしいですか？')) {
                raceRecords = [];
                updateAll();
            }
        }

        // PWA Functions
        function setupPWA() {
            const svgIcon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512"><rect width="512" height="512" rx="128" fill="#080c14"/><path d="M64 64h384v384H64z" fill="none"/><text x="50%" y="45%" dominant-baseline="central" text-anchor="middle" fill="#ffffff" font-family="sans-serif" font-weight="900" font-size="160">BYN</text><text x="50%" y="75%" dominant-baseline="central" text-anchor="middle" fill="#3b82f6" font-family="sans-serif" font-weight="700" font-size="50">ANALYZER</text></svg>`;
            const iconUrl = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgIcon)));

            let appleIcon = document.querySelector('link[rel="apple-touch-icon"]');
            if (!appleIcon) {
                appleIcon = document.createElement('link');
                appleIcon.rel = 'apple-touch-icon';
                document.head.appendChild(appleIcon);
            }
            appleIcon.href = iconUrl;

            const manifest = {
                name: "BYN Race Analyzer",
                short_name: "BYN Race",
                description: "B/Y/N予想サイト重複＆手書き収支分析ツール",
                start_url: window.location.href,
                display: "standalone",
                background_color: "#080c14",
                theme_color: "#080c14",
                icons: [
                    { src: iconUrl, sizes: "512x512", type: "image/svg+xml", purpose: "any maskable" }
                ]
            };

            const manifestBlob = new Blob([JSON.stringify(manifest)], { type: 'application/json' });
            const manifestUrl = URL.createObjectURL(manifestBlob);
            
            let manifestLink = document.querySelector('link[rel="manifest"]');
            if (!manifestLink) {
                manifestLink = document.createElement('link');
                manifestLink.rel = 'manifest';
                document.head.appendChild(manifestLink);
            }
            manifestLink.href = manifestUrl;
        }

        function openPwaModal() { document.getElementById('pwaModal').classList.remove('hidden'); }
        function closePwaModal() { document.getElementById('pwaModal').classList.add('hidden'); }

        // OCR Functions
        function openOcrModal() { document.getElementById('ocrModal').classList.remove('hidden'); }
        function closeOcrModal() { document.getElementById('ocrModal').classList.add('hidden'); }

        async function handleOcrFiles(files) {
            if (!files || files.length === 0) return;

            const previewBox = document.getElementById('ocrImagePreviews');
            const progressBox = document.getElementById('ocrProgressBox');
            const resultsBox = document.getElementById('ocrResultsBox');
            const statusText = document.getElementById('ocrProgressStatus');
            const percentText = document.getElementById('ocrProgressPercent');
            const progressBar = document.getElementById('ocrProgressBar');

            previewBox.innerHTML = '';
            previewBox.classList.remove('hidden');
            progressBox.classList.remove('hidden');
            resultsBox.classList.add('hidden');

            let combinedText = '';

            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'w-16 h-16 object-cover rounded-lg border border-slate-700 shadow';
                    previewBox.appendChild(img);
                };
                reader.readAsDataURL(file);

                statusText.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-emerald-400"></i> 画像 ${i+1}/${files.length} を解析中...`;
                percentText.textContent = '0%';
                progressBar.style.width = '0%';

                try {
                    const worker = await Tesseract.createWorker('jpn+eng');
                    const ret = await worker.recognize(file);
                    combinedText += '\n' + ret.data.text;
                    await worker.terminate();
                } catch (err) {
                    console.error('OCR error:', err);
                }
            }

            statusText.textContent = '解析完了!';
            percentText.textContent = '100%';
            progressBar.style.width = '100%';

            parseAndShowOcrResults(combinedText);
        }

        function parseAndShowOcrResults(text) {
            const resultsBox = document.getElementById('ocrResultsBox');
            resultsBox.classList.remove('hidden');

            document.getElementById('ocr-res-raw').value = text.trim();

            const raceMatch = text.match(/(\d{1,2})\s*[RRｒｒ]/i);
            document.getElementById('ocr-res-raceNo').value = raceMatch ? raceMatch[1] + 'R' : '';

            const payout3Match = text.match(/3連単\s*[^\d]*?([\d,]+)\s*円/);
            document.getElementById('ocr-res-payout3').value = payout3Match ? payout3Match[1].replace(/,/g, '') : '';

            const payout2Match = text.match(/2車単\s*[^\d]*?([\d,]+)\s*円/);
            document.getElementById('ocr-res-payout2').value = payout2Match ? payout2Match[1].replace(/,/g, '') : '';

            const comboMatch = text.match(/(\d)\s*[^\d\n]*?[\-\u2010-\u2015\u2212\uFF0D〜ー]\s*(\d)\s*[^\d\n]*?[\-\u2010-\u2015\u2212\uFF0D〜ー]\s*(\d)/);
            if (comboMatch) {
                document.getElementById('ocr-res-combo').value = `${comboMatch[1]}-${comboMatch[2]}-${comboMatch[3]}`;
            } else {
                const digits = text.match(/\b([1-9])\b/g);
                if (digits && digits.length >= 3) {
                    document.getElementById('ocr-res-combo').value = digits.slice(0, 3).join('-');
                } else {
                    document.getElementById('ocr-res-combo').value = '';
                }
            }
        }

        function applyOcrToForm() {
            const raceNo = document.getElementById('ocr-res-raceNo').value;
            const combo = document.getElementById('ocr-res-combo').value;
            const payout3 = document.getElementById('ocr-res-payout3').value;
            const payout2 = document.getElementById('ocr-res-payout2').value;

            if (raceNo) document.getElementById('input-raceNo').value = raceNo;

            const chosenPayout = payout3 || payout2 || '0';
            document.getElementById('input-payout').value = chosenPayout;

            let comboText = combo;
            if (payout3) comboText += ` (3連単 ${parseInt(payout3).toLocaleString()}円)`;
            if (payout2) comboText += ` (2車単 ${parseInt(payout2).toLocaleString()}円)`;

            document.getElementById('input-winning-combination').value = comboText;

            if (parseInt(chosenPayout) > 0) setResult(true);

            closeOcrModal();
            switchTab('input');
            alert('解析結果をフォームに反映しました！内容をご確認の上保存してください。');
        }

        // CSV Export/Import
        function exportCSV() {
            if (raceRecords.length === 0) {
                alert('出力対象のデータが存在しません。');
                return;
            }

            let csv = 'ID,日付,開催場,レース番号,推奨サイト,パターンキー,重複数,難易度,買い目JSON,一括メモ,投資額,的中フラグ,払戻金,純利益,決定着順\n';
            raceRecords.forEach(r => {
                const sitesStr = r.sites.join('|');
                const pk = r.patternKey || getPatternKey(r.sites);
                const ticketsJson = JSON.stringify(r.tickets || []).replace(/"/g, '""');
                csv += `"${r.id}","${r.date}","${r.venue}","${r.raceNo}","${sitesStr}","${pk}",${r.overlapCount},"${r.trend}","${ticketsJson}","${(r.batchText||'').replace(/"/g, '""')}",${r.investment},${r.isWin ? 1 : 0},${r.payout},${r.profit},"${(r.winningCombo||'').replace(/"/g, '""')}"\n`;
            });

            const blob = new Blob([new Uint8Array([0xEF, 0xBB, 0xBF]), csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `BYN_Pattern_Analysis_${new Date().toISOString().split('T')[0]}.csv`;
            link.click();
        }

        function importCSV(e) {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(evt) {
                try {
                    const text = evt.target.result;
                    const lines = text.split('\n');
                    let importedCount = 0;

                    for (let i = 1; i < lines.length; i++) {
                        const line = lines[i].trim();
                        if (!line) continue;

                        const matches = line.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g);
                        if (matches && matches.length >= 11) {
                            const clean = matches.map(m => m.replace(/^"|"$/g, '').replace(/""/g, '"'));
                            
                            const sites = clean[4] ? clean[4].split('|') : [];
                            const pk = clean[5] || getPatternKey(sites);
                            let tickets = [];
                            try { tickets = JSON.parse(clean[8] || '[]'); } catch(e){}

                            const record = {
                                id: clean[0] || Date.now().toString() + i,
                                date: clean[1] || new Date().toISOString().split('T')[0],
                                venue: clean[2] || '不明',
                                raceNo: clean[3] || '1R',
                                sites: sites,
                                patternKey: pk,
                                overlapCount: parseInt(clean[6]) || sites.length,
                                trend: clean[7] || '荒れ',
                                tickets: tickets,
                                batchText: clean[9] || '',
                                investment: parseInt(clean[10]) || 0,
                                isWin: clean[11] === '1',
                                payout: parseInt(clean[12]) || 0,
                                profit: parseInt(clean[13]) || 0,
                                winningCombo: clean[14] || '',
                                createdAt: Date.now()
                            };
                            raceRecords.push(record);
                            importedCount++;
                        }
                    }

                    updateAll();
                    alert(`${importedCount}件のデータをCSVから取り込みました！`);
                } catch(err) {
                    alert('CSVの読み込みに失敗しました。フォーマットをご確認ください。');
                }
            };
            reader.readAsText(file);
        }

        function loadSampleData() {
            if (raceRecords.length > 0 && !confirm('既存のデータに7パターンのサンプルデータ（7件）を追加しますか？')) {
                return;
            }

            const samples = [
                {
                    id: 's-byn-1', date: '2026-10-20', venue: '平塚競輪', raceNo: '11R', sites: ['B', 'Y', 'N'], patternKey: 'B_Y_N', overlapCount: 3, trend: '荒れ',
                    tickets: [{ type: '3連単', combo: '1-2-3', amount: 500, odds: '96.0' }], batchText: '3サイト全一致の特大荒れ気配レース', winningCombo: '1-2-3 (96.0倍)', investment: 1000, isWin: true, payout: 48000, profit: 47000, createdAt: Date.now() - 70000
                },
                {
                    id: 's-by-2', date: '2026-10-20', venue: '立川', raceNo: '10R', sites: ['B', 'Y'], patternKey: 'B_Y', overlapCount: 2, trend: '普通',
                    tickets: [{ type: '3連単', combo: '2-4-5', amount: 1000, odds: '18.5' }], batchText: 'B&Yのペア。4着でハズレ', winningCombo: '2-5-7', investment: 1000, isWin: false, payout: 0, profit: -1000, createdAt: Date.now() - 60000
                },
                {
                    id: 's-yn-3', date: '2026-10-21', venue: '小田原', raceNo: '12R', sites: ['Y', 'N'], patternKey: 'Y_N', overlapCount: 2, trend: '荒れ',
                    tickets: [{ type: '3連単', combo: '3-7-1', amount: 1000, odds: '52.0' }], batchText: 'Y&N重複で見事的中！', winningCombo: '3-7-1 (52.0倍)', investment: 1000, isWin: true, payout: 52000, profit: 51000, createdAt: Date.now() - 50000
                },
                {
                    id: 's-bn-4', date: '2026-10-21', venue: '松戸', raceNo: '09R', sites: ['B', 'N'], patternKey: 'B_N', overlapCount: 2, trend: '固い',
                    tickets: [{ type: '2連単', combo: '1-2', amount: 1000, odds: '4.2' }], batchText: 'B&N本命予想', winningCombo: '1-2', investment: 1000, isWin: true, payout: 4200, profit: 3200, createdAt: Date.now() - 40000
                },
                {
                    id: 's-b-5', date: '2026-10-21', venue: '京王閣', raceNo: '11R', sites: ['B'], patternKey: 'B', overlapCount: 1, trend: '荒れ',
                    tickets: [{ type: '3連単', combo: '5-1-2', amount: 1000, odds: '150.0' }], batchText: 'B単独穴予想。ハズレ', winningCombo: '1-5-2', investment: 1000, isWin: false, payout: 0, profit: -1000, createdAt: Date.now() - 30000
                },
                {
                    id: 's-y-6', date: '2026-10-21', venue: '川崎', raceNo: '08R', sites: ['Y'], patternKey: 'Y', overlapCount: 1, trend: '普通',
                    tickets: [{ type: '3連複', combo: '1=3=5', amount: 1000, odds: '15.0' }], batchText: 'Y単独推奨', winningCombo: '1-3-5', investment: 1000, isWin: true, payout: 15000, profit: 14000, createdAt: Date.now() - 20000
                },
                {
                    id: 's-n-7', date: '2026-10-21', venue: '取手', raceNo: '07R', sites: ['N'], patternKey: 'N', overlapCount: 1, trend: '荒れ',
                    tickets: [{ type: '3連単', combo: '4-2-7', amount: 1000, odds: '80.0' }], batchText: 'N単独穴', winningCombo: '2-4-7', investment: 1000, isWin: false, payout: 0, profit: -1000, createdAt: Date.now() - 10000
                }
            ];

            raceRecords = [...samples, ...raceRecords];
            updateAll();
            alert('サンプルデータを投入しました！パターン別の違いをご確認ください。');
        }
    </script>
</body>
</html>
```
