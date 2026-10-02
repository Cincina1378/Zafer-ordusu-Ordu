from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Dynex | Yönetim Paneli</title>

    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: Arial, Helvetica, sans-serif;
        }

        body {
            background: #080b12;
            color: #ffffff;
            min-height: 100vh;
        }

        .navbar {
            height: 72px;
            border-bottom: 1px solid #1c2230;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 6%;
            background: rgba(8, 11, 18, 0.95);
        }

        .logo {
            font-size: 25px;
            font-weight: 800;
            color: #ffffff;
        }

        .logo span {
            color: #5865f2;
        }

        .nav-buttons {
            display: flex;
            gap: 12px;
        }

        .btn {
            border: none;
            border-radius: 10px;
            padding: 11px 18px;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            transition: 0.2s;
        }

        .btn:hover {
            transform: translateY(-2px);
        }

        .btn-primary {
            background: #5865f2;
            color: white;
        }

        .btn-secondary {
            background: #151a26;
            color: #dce0ff;
            border: 1px solid #252c3c;
        }

        .hero {
            min-height: calc(100vh - 72px);
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 70px 20px;
        }

        .hero-content {
            max-width: 850px;
        }

        .badge {
            display: inline-block;
            padding: 8px 14px;
            border-radius: 30px;
            background: rgba(88, 101, 242, 0.12);
            border: 1px solid rgba(88, 101, 242, 0.35);
            color: #9da5ff;
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 22px;
        }

        h1 {
            font-size: clamp(42px, 8vw, 78px);
            line-height: 1;
            margin-bottom: 22px;
        }

        h1 span {
            color: #5865f2;
        }

        .hero p {
            color: #9299aa;
            font-size: 18px;
            line-height: 1.7;
            max-width: 650px;
            margin: auto;
        }

        .hero-buttons {
            margin-top: 32px;
            display: flex;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
        }

        .big-btn {
            padding: 14px 24px;
            font-size: 15px;
        }

        .dashboard {
            display: none;
            min-height: 100vh;
        }

        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            bottom: 0;
            width: 250px;
            background: #0c1019;
            border-right: 1px solid #1c2230;
            padding: 24px 16px;
        }

        .side-logo {
            padding: 10px 14px 28px;
            font-size: 23px;
            font-weight: 800;
        }

        .side-logo span {
            color: #5865f2;
        }

        .menu-title {
            color: #626b7e;
            font-size: 11px;
            font-weight: 800;
            margin: 15px 14px 8px;
            text-transform: uppercase;
        }

        .menu-item {
            width: 100%;
            border: none;
            background: transparent;
            color: #9da5b6;
            padding: 13px 14px;
            text-align: left;
            border-radius: 9px;
            margin-bottom: 4px;
            cursor: pointer;
            font-size: 14px;
        }

        .menu-item:hover,
        .menu-item.active {
            background: #171d2b;
            color: white;
        }

        .main {
            margin-left: 250px;
            padding: 40px;
        }

        .top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 35px;
        }

        .top h2 {
            font-size: 28px;
        }

        .profile {
            background: #111722;
            border: 1px solid #222a39;
            padding: 10px 15px;
            border-radius: 10px;
            color: #cbd1df;
        }

        .cards {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 18px;
            margin-bottom: 30px;
        }

        .card {
            background: #0e131d;
            border: 1px solid #1e2635;
            border-radius: 14px;
            padding: 22px;
        }

        .card-title {
            color: #7e8799;
            font-size: 13px;
            margin-bottom: 12px;
        }

        .card-value {
            font-size: 30px;
            font-weight: 800;
        }

        .card-info {
            color: #5865f2;
            font-size: 12px;
            margin-top: 8px;
        }

        .section {
            background: #0e131d;
            border: 1px solid #1e2635;
            border-radius: 14px;
            padding: 25px;
            margin-bottom: 20px;
        }

        .section h3 {
            margin-bottom: 8px;
        }

        .section p {
            color: #7f8798;
            line-height: 1.6;
        }

        .server {
            margin-top: 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #111722;
            border: 1px solid #222a39;
            border-radius: 12px;
            padding: 16px;
        }

        .server-left {
            display: flex;
            align-items: center;
            gap: 13px;
        }

        .server-icon {
            width: 45px;
            height: 45px;
            border-radius: 12px;
            background: #5865f2;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
        }

        .server-name {
            font-weight: 700;
        }

        .server-status {
            color: #65d68b;
            font-size: 12px;
            margin-top: 4px;
        }

        @media (max-width: 800px) {
            .navbar {
                padding: 0 20px;
            }

            .nav-buttons .btn-secondary {
                display: none;
            }

            .cards {
                grid-template-columns: 1fr;
            }

            .sidebar {
                width: 70px;
                padding: 15px 8px;
            }

            .side-logo {
                font-size: 0;
                text-align: center;
            }

            .side-logo span {
                font-size: 23px;
            }

            .menu-title {
                display: none;
            }

            .menu-item {
                text-align: center;
                font-size: 0;
            }

            .menu-item:first-letter {
                font-size: 18px;
            }

            .main {
                margin-left: 70px;
                padding: 22px 15px;
            }
        }
    </style>
</head>

<body>

    <!-- ANA SAYFA -->

    <div id="home">

        <nav class="navbar">
            <div class="logo">
                Dynex<span>.</span>
            </div>

            <div class="nav-buttons">
                <button class="btn btn-secondary" onclick="showDashboard()">
                    Yönetim Paneli
                </button>

                <button class="btn btn-primary" onclick="showDashboard()">
                    Başla
                </button>
            </div>
        </nav>

        <section class="hero">

            <div class="hero-content">

                <div class="badge">
                    DYNEX YÖNETİM PLATFORMU
                </div>

                <h1>
                    Botlarını <span>tek yerden</span> yönet.
                </h1>

                <p>
                    Discord botlarını, Roblox bağlantılarını ve sunucu
                    ayarlarını tek bir modern yönetim panelinden kontrol et.
                </p>

                <div class="hero-buttons">

                    <button
                        class="btn btn-primary big-btn"
                        onclick="showDashboard()">
                        Yönetim Paneline Gir
                    </button>

                    <button
                        class="btn btn-secondary big-btn"
                        onclick="showDashboard()">
                        Daha Fazla
                    </button>

                </div>

            </div>

        </section>

    </div>


    <!-- YÖNETİM PANELİ -->

    <div id="dashboard" class="dashboard">

        <aside class="sidebar">

            <div class="side-logo">
                Dynex<span>.</span>
            </div>

            <div class="menu-title">
                Genel
            </div>

            <button
                class="menu-item active"
                onclick="openPage('dashboardPage')">
                🏠 Ana Sayfa
            </button>

            <button
                class="menu-item"
                onclick="openPage('botsPage')">
                🤖 Botlar
            </button>

            <button
                class="menu-item"
                onclick="openPage('serversPage')">
                🛡️ Sunucular
            </button>

            <div class="menu-title">
                Hesap
            </div>

            <button
                class="menu-item"
                onclick="openPage('robloxPage')">
                🎮 Roblox Hesaplarım
            </button>

            <button
                class="menu-item"
                onclick="openPage('settingsPage')">
                ⚙️ Ayarlar
            </button>

        </aside>


        <main class="main">

            <!-- DASHBOARD -->

            <div id="dashboardPage">

                <div class="top">

                    <div>
                        <h2>Hoş geldin 👋</h2>
                    </div>

                    <div class="profile">
                        Dynex Kullanıcısı
                    </div>

                </div>


                <div class="cards">

                    <div class="card">
                        <div class="card-title">
                            Aktif Botlar
                        </div>

                        <div class="card-value">
                            0
                        </div>

                        <div class="card-info">
                            Henüz bot eklenmedi
                        </div>
                    </div>


                    <div class="card">
                        <div class="card-title">
                            Discord Sunucuları
                        </div>

                        <div class="card-value">
                            0
                        </div>

                        <div class="card-info">
                            Bağlı sunucu bulunmuyor
                        </div>
                    </div>


                    <div class="card">
                        <div class="card-title">
                            Roblox Hesapları
                        </div>

                        <div class="card-value">
                            0
                        </div>

                        <div class="card-info">
                            Hesap bağlanmadı
                        </div>
                    </div>

                </div>


                <div class="section">

                    <h3>Dynex'e Hoş Geldin</h3>

                    <p>
                        Bu panel üzerinden Discord botlarını,
                        sunucularını ve Roblox bağlantılarını
                        yönetebileceksin.
                    </p>

                </div>


                <div class="section">

                    <h3>Bağlı Sunucular</h3>

                    <div class="server">

                        <div class="server-left">

                            <div class="server-icon">
                                D
                            </div>

                            <div>
                                <div class="server-name">
                                    Henüz sunucu bağlanmadı
                                </div>

                                <div class="server-status">
                                    Bekleniyor
                                </div>
                            </div>

                        </div>

                    </div>

                </div>

            </div>


            <!-- BOTLAR -->

            <div id="botsPage" style="display:none">

                <div class="top">
                    <h2>Botlar</h2>

                    <button class="btn btn-primary">
                        + Bot Oluştur
                    </button>
                </div>

                <div class="section">

                    <h3>Discord Botların</h3>

                    <p>
                        Burada oluşturduğun ve yönettiğin Discord
                        botları görünecek.
                    </p>

                </div>

            </div>


            <!-- SUNUCULAR -->

            <div id="serversPage" style="display:none">

                <div class="top">
                    <h2>Sunucular</h2>
                </div>

                <div class="section">

                    <h3>Discord Sunucuları</h3>

                    <p>
                        Botlarının bulunduğu Discord sunucuları
                        burada listelenecek.
                    </p>

                </div>

            </div>


            <!-- ROBLOX -->

            <div id="robloxPage" style="display:none">

                <div class="top">
                    <h2>Roblox Hesaplarım</h2>
                </div>

                <div class="section">

                    <h3>Roblox Hesabı Bağla</h3>

                    <p>
                        Roblox hesabın henüz bağlanmadı.
                        İlerleyen aşamada resmi Roblox bağlantısı
                        buraya eklenecek.
                    </p>

                    <br>

                    <button class="btn btn-primary">
                        Roblox Hesabı Bağla
                    </button>

                </div>

            </div>


            <!-- AYARLAR -->

            <div id="settingsPage" style="display:none">

                <div class="top">
                    <h2>Ayarlar</h2>
                </div>

                <div class="section">

                    <h3>Hesap Ayarları</h3>

                    <p>
                        Dynex hesap ve platform ayarları burada
                        yönetilecek.
                    </p>

                </div>

            </div>

        </main>

    </div>


    <script>

        function showDashboard() {

            document.getElementById("home").style.display = "none";

            document.getElementById("dashboard").style.display = "block";

        }


        function openPage(page) {

            const pages = [
                "dashboardPage",
                "botsPage",
                "serversPage",
                "robloxPage",
                "settingsPage"
            ];

            pages.forEach(function(id) {

                document.getElementById(id).style.display = "none";

            });

            document.getElementById(page).style.display = "block";

        }

    </script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
