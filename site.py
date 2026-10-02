import os
import json
import secrets
import hashlib
import base64
import urllib.parse
import urllib.request
from flask import Flask, redirect, request, session, render_template_string

# =========================================================
# ZAFER ORDUSU - SITE
# =========================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    secrets.token_hex(32)
)

SITE_URL = os.environ.get(
    "SITE_URL",
    ""
).rstrip("/")


# =========================================================
# ROBLOX OAUTH
# =========================================================

ROBLOX_CLIENT_ID = os.environ.get(
    "ROBLOX_CLIENT_ID",
    ""
)

ROBLOX_CLIENT_SECRET = os.environ.get(
    "ROBLOX_CLIENT_SECRET",
    ""
)

ROBLOX_AUTHORIZE_URL = (
    "https://apis.roblox.com/oauth/v1/authorize"
)

ROBLOX_TOKEN_URL = (
    "https://apis.roblox.com/oauth/v1/token"
)

ROBLOX_USERINFO_URL = (
    "https://apis.roblox.com/oauth/v1/userinfo"
)


# =========================================================
# DISCORD OAUTH
# =========================================================

DISCORD_CLIENT_ID = os.environ.get(
    "DISCORD_CLIENT_ID",
    ""
)

DISCORD_CLIENT_SECRET = os.environ.get(
    "DISCORD_CLIENT_SECRET",
    ""
)

DISCORD_AUTHORIZE_URL = (
    "https://discord.com/oauth2/authorize"
)

DISCORD_TOKEN_URL = (
    "https://discord.com/api/oauth2/token"
)

DISCORD_API = (
    "https://discord.com/api"
)


# =========================================================
# GRUP AYARLARI
#
# Daha sonra main.py /ayarlar sistemi buraya gerçek
# verileri sağlayacak.
#
# Yapı:
#
# {
#     "Discord Sunucu ID": {
#         "name": "Sunucu adı",
#         "groups": [
#             {
#                 "id": "Roblox grup ID",
#                 "name": "Grup adı"
#             }
#         ]
#     }
# }
# =========================================================

GROUP_CONFIG_FILE = "group_config.json"


def load_group_config():

    if not os.path.exists(GROUP_CONFIG_FILE):
        return {}

    try:

        with open(
            GROUP_CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return {}


# =========================================================
# HTTP YARDIMCI
# =========================================================

def http_request(
    url,
    method="GET",
    data=None,
    headers=None
):

    if headers is None:
        headers = {}

    if data is not None:

        if isinstance(data, dict):

            data = urllib.parse.urlencode(
                data
            ).encode()

        request = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method=method
        )

    else:

        request = urllib.request.Request(
            url,
            headers=headers,
            method=method
        )

    with urllib.request.urlopen(
        request,
        timeout=20
    ) as response:

        return json.loads(
            response.read().decode()
        )


# =========================================================
# PKCE
# =========================================================

def generate_code_verifier():

    return secrets.token_urlsafe(64)


def generate_code_challenge(
    verifier
):

    digest = hashlib.sha256(
        verifier.encode()
    ).digest()

    return base64.urlsafe_b64encode(
        digest
    ).decode().rstrip("=")


# =========================================================
# ROBLOX LOGIN
# =========================================================

@app.route("/login/roblox")
def login_roblox():

    if not ROBLOX_CLIENT_ID:

        return """
        <h2>Roblox OAuth ayarlanmadı.</h2>
        <p>ROBLOX_CLIENT_ID environment variable eksik.</p>
        """, 500

    if not SITE_URL:

        return """
        <h2>SITE_URL ayarlanmadı.</h2>
        """, 500

    state = secrets.token_urlsafe(32)

    verifier = generate_code_verifier()

    challenge = generate_code_challenge(
        verifier
    )

    session["roblox_state"] = state

    session["roblox_verifier"] = verifier

    redirect_uri = (
        SITE_URL
        + "/oauth/roblox/callback"
    )

    params = {

        "client_id":
            ROBLOX_CLIENT_ID,

        "redirect_uri":
            redirect_uri,

        "response_type":
            "code",

        "scope":
            "openid profile",

        "state":
            state,

        "code_challenge":
            challenge,

        "code_challenge_method":
            "S256"
    }

    url = (
        ROBLOX_AUTHORIZE_URL
        + "?"
        + urllib.parse.urlencode(
            params
        )
    )

    return redirect(url)


# =========================================================
# ROBLOX CALLBACK
# =========================================================

@app.route(
    "/oauth/roblox/callback"
)
def roblox_callback():

    returned_state = request.args.get(
        "state"
    )

    saved_state = session.get(
        "roblox_state"
    )

    if (
        not returned_state
        or returned_state != saved_state
    ):

        return """
        <h2>Roblox doğrulaması başarısız.</h2>
        <p>Güvenlik doğrulaması geçersiz.</p>
        """, 400

    code = request.args.get(
        "code"
    )

    if not code:

        return """
        <h2>Roblox girişi iptal edildi.</h2>
        """, 400

    verifier = session.get(
        "roblox_verifier"
    )

    redirect_uri = (
        SITE_URL
        + "/oauth/roblox/callback"
    )

    token_data = {

        "client_id":
            ROBLOX_CLIENT_ID,

        "client_secret":
            ROBLOX_CLIENT_SECRET,

        "grant_type":
            "authorization_code",

        "code":
            code,

        "code_verifier":
            verifier,

        "redirect_uri":
            redirect_uri
    }

    try:

        token = http_request(
            ROBLOX_TOKEN_URL,
            method="POST",
            data=token_data,
            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded"
            }
        )

        access_token = token.get(
            "access_token"
        )

        if not access_token:

            return """
            <h2>Roblox erişim anahtarı alınamadı.</h2>
            """, 400

        user = http_request(
            ROBLOX_USERINFO_URL,
            headers={
                "Authorization":
                    "Bearer "
                    + access_token
            }
        )

        session["roblox"] = {

            "id":
                user.get("sub"),

            "username":
                user.get(
                    "preferred_username"
                ),

            "display_name":
                user.get(
                    "name"
                ),

            "avatar":
                user.get(
                    "picture"
                )
        }

        session["roblox_access_token"] = (
            access_token
        )

        return redirect("/")

    except Exception as error:

        return (
            "<h2>Roblox bağlantı hatası</h2>"
            "<p>"
            + str(error)
            + "</p>"
        ), 500


# =========================================================
# DISCORD LOGIN
# =========================================================

@app.route("/login/discord")
def login_discord():

    if not DISCORD_CLIENT_ID:

        return """
        <h2>Discord OAuth ayarlanmadı.</h2>
        <p>DISCORD_CLIENT_ID eksik.</p>
        """, 500

    state = secrets.token_urlsafe(32)

    session["discord_state"] = state

    redirect_uri = (
        SITE_URL
        + "/oauth/discord/callback"
    )

    params = {

        "client_id":
            DISCORD_CLIENT_ID,

        "redirect_uri":
            redirect_uri,

        "response_type":
            "code",

        "scope":
            "identify guilds",

        "state":
            state
    }

    url = (
        DISCORD_AUTHORIZE_URL
        + "?"
        + urllib.parse.urlencode(
            params
        )
    )

    return redirect(url)


# =========================================================
# DISCORD CALLBACK
# =========================================================

@app.route(
    "/oauth/discord/callback"
)
def discord_callback():

    state = request.args.get(
        "state"
    )

    if state != session.get(
        "discord_state"
    ):

        return """
        <h2>Discord doğrulaması başarısız.</h2>
        """, 400

    code = request.args.get(
        "code"
    )

    if not code:

        return """
        <h2>Discord girişi iptal edildi.</h2>
        """, 400

    redirect_uri = (
        SITE_URL
        + "/oauth/discord/callback"
    )

    token_data = {

        "client_id":
            DISCORD_CLIENT_ID,

        "client_secret":
            DISCORD_CLIENT_SECRET,

        "grant_type":
            "authorization_code",

        "code":
            code,

        "redirect_uri":
            redirect_uri
    }

    try:

        token = http_request(
            DISCORD_TOKEN_URL,
            method="POST",
            data=token_data,
            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded"
            }
        )

        access_token = token.get(
            "access_token"
        )

        if not access_token:

            return """
            <h2>Discord erişim anahtarı alınamadı.</h2>
            """, 400

        user = http_request(
            DISCORD_API + "/users/@me",
            headers={
                "Authorization":
                    "Bearer "
                    + access_token
            }
        )

        guilds = http_request(
            DISCORD_API + "/users/@me/guilds",
            headers={
                "Authorization":
                    "Bearer "
                    + access_token
            }
        )

        session["discord"] = {

            "id":
                user.get("id"),

            "username":
                user.get("username"),

            "global_name":
                user.get("global_name"),

            "avatar":
                user.get("avatar")
        }

        session["discord_guilds"] = guilds

        return redirect("/")

    except Exception as error:

        return (
            "<h2>Discord bağlantı hatası</h2>"
            "<p>"
            + str(error)
            + "</p>"
        ), 500


# =========================================================
# ANA SAYFA
# =========================================================

HTML = r"""
<!DOCTYPE html>

<html lang="tr">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width,initial-scale=1.0"
>

<title>Zafer Ordusu</title>

<style>

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    background: #080808;

    color: white;

    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}

button {

    font: inherit;
}

.sidebar {

    position: fixed;

    left: 0;
    top: 0;
    bottom: 0;

    width: 250px;

    background: #0d0d0d;

    border-right:
        1px solid #242424;

    padding: 22px 15px;
}

.logo {

    display: flex;

    align-items: center;

    gap: 12px;

    padding:
        8px 10px 28px;
}

.logo-icon {

    width: 42px;
    height: 42px;

    border-radius: 50%;

    background: #ffd21f;

    color: #111;

    display: grid;

    place-items: center;

    font-weight: 900;
}

.logo-title {

    font-weight: 800;

    font-size: 17px;
}

.logo-sub {

    color: #777;

    font-size: 11px;

    margin-top: 3px;
}

.nav {

    display: flex;

    flex-direction: column;

    gap: 6px;
}

.nav button {

    border: 0;

    background: transparent;

    color: #999;

    text-align: left;

    padding: 13px;

    border-radius: 10px;

    cursor: pointer;
}

.nav button:hover,
.nav button.active {

    background: #191919;

    color: white;
}

.nav button.active {

    border-left:
        3px solid #ffd21f;
}

.main {

    margin-left: 250px;

    padding: 30px;

    max-width: 1450px;
}

.top {

    display: flex;

    align-items: center;

    justify-content: space-between;

    margin-bottom: 25px;
}

.top h1 {

    margin: 0;

    font-size: 28px;
}

.top p {

    margin-top: 7px;

    color: #777;
}

.profile {

    display: flex;

    align-items: center;

    gap: 10px;

    background: #111;

    border:
        1px solid #252525;

    padding: 8px 12px;

    border-radius: 12px;
}

.avatar {

    width: 34px;
    height: 34px;

    border-radius: 50%;

    display: grid;

    place-items: center;

    background: #ffd21f;

    color: #111;

    font-weight: 800;
}

.page {

    display: none;
}

.page.active {

    display: block;
}

.hero {

    background:
        linear-gradient(
            135deg,
            #171717,
            #0d0d0d
        );

    border:
        1px solid #292929;

    border-radius: 20px;

    padding: 32px;

    margin-bottom: 18px;
}

.hero h2 {

    margin: 0 0 10px;

    font-size: 32px;
}

.hero p {

    color: #999;

    max-width: 720px;

    line-height: 1.6;
}

.buttons {

    display: flex;

    gap: 10px;

    flex-wrap: wrap;

    margin-top: 22px;
}

.btn {

    border: 0;

    border-radius: 10px;

    padding: 12px 17px;

    cursor: pointer;

    font-weight: 750;
}

.yellow {

    background: #ffd21f;

    color: #111;
}

.dark {

    background: #1a1a1a;

    color: white;

    border:
        1px solid #303030;
}

.cards {

    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 16px;
}

.card {

    background: #101010;

    border:
        1px solid #242424;

    border-radius: 16px;

    padding: 22px;
}

.card-title {

    color: #777;

    font-size: 14px;
}

.card-value {

    margin-top: 10px;

    font-size: 25px;

    font-weight: 800;
}

.panel {

    background: #101010;

    border:
        1px solid #242424;

    border-radius: 16px;

    padding: 23px;
}

.panel h2 {

    margin-top: 0;
}

.muted {

    color: #777;

    line-height: 1.5;
}

.account-box {

    display: flex;

    align-items: center;

    gap: 15px;

    padding: 18px;

    background: #151515;

    border:
        1px solid #292929;

    border-radius: 14px;

    margin-top: 20px;
}

.roblox-avatar {

    width: 60px;
    height: 60px;

    border-radius: 14px;

    object-fit: cover;

    background: #222;
}

.server {

    background: #151515;

    border:
        1px solid #292929;

    border-radius: 14px;

    padding: 18px;

    margin-top: 12px;

    cursor: pointer;
}

.server:hover {

    border-color: #ffd21f;
}

.server.selected {

    border-color: #ffd21f;

    box-shadow:
        0 0 0 1px #ffd21f;
}

.server-name {

    font-weight: 800;

    font-size: 17px;
}

.server-id {

    color: #666;

    font-size: 12px;

    margin-top: 5px;
}

.group {

    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 15px;

    padding: 16px 0;

    border-bottom:
        1px solid #222;
}

.group:last-child {

    border-bottom: 0;
}

.empty {

    text-align: center;

    color: #777;

    padding: 45px 15px;
}

.status {

    margin-top: 15px;

    padding: 12px 15px;

    border-radius: 10px;

    background: #171717;

    color: #aaa;
}

@media(max-width:800px) {

    .sidebar {

        display: none;
    }

    .main {

        margin-left: 0;

        padding: 18px;
    }

    .cards {

        grid-template-columns: 1fr;
    }

    .profile {

        display: none;
    }
}

</style>

</head>

<body>

<aside class="sidebar">

    <div class="logo">

        <div class="logo-icon">
            ★
        </div>

        <div>

            <div class="logo-title">
                Zafer Ordusu
            </div>

            <div class="logo-sub">
                Yönetim Platformu
            </div>

        </div>

    </div>

    <nav class="nav">

        <button
            class="active"
            onclick="page('home',this)"
        >
            ⌂ Ana Sayfa
        </button>

        <button
            onclick="page('roblox',this)"
        >
            ◈ Roblox Hesabım
        </button>

        <button
            onclick="page('discord',this)"
        >
            ◉ Discord Hesabım
        </button>

        <button
            onclick="page('servers',this)"
        >
            ▣ Sunucular
        </button>

        <button
            onclick="page('groups',this)"
        >
            ◆ Gruplar
        </button>

    </nav>

</aside>


<main class="main">

    <header class="top">

        <div>

            <h1 id="title">
                Ana Sayfa
            </h1>

            <p>
                Zafer Ordusu yönetim platformu
            </p>

        </div>

        <div class="profile">

            <div
                class="avatar"
                id="profileAvatar"
            >
                ?
            </div>

            <span id="profileName">
                Hesap bağlı değil
            </span>

        </div>

    </header>


    <!-- ANA SAYFA -->

    <section
        id="home"
        class="page active"
    >

        <div class="hero">

            <h2>
                Zafer Ordusu
            </h2>

            <p>
                Roblox hesabını ve Discord hesabını bağla.
                Daha sonra bulunduğun Discord sunucusunu
                seçerek o sunucu için yapılandırılmış
                Roblox gruplarını yönet.
            </p>

            <div class="buttons">

                <button
                    class="btn yellow"
                    onclick="pageByName('roblox')"
                >
                    Roblox Hesabı Bağla
                </button>

                <button
                    class="btn dark"
                    onclick="pageByName('discord')"
                >
                    Discord Hesabı Bağla
                </button>

                <button
                    class="btn dark"
                    onclick="pageByName('servers')"
                >
                    Sunucularımı Gör
                </button>

            </div>

        </div>


        <div class="cards">

            <div class="card">

                <div class="card-title">
                    Roblox Hesabı
                </div>

                <div
                    class="card-value"
                    id="homeRoblox"
                >
                    Bağlı değil
                </div>

            </div>


            <div class="card">

                <div class="card-title">
                    Discord Hesabı
                </div>

                <div
                    class="card-value"
                    id="homeDiscord"
                >
                    Bağlı değil
                </div>

            </div>


            <div class="card">

                <div class="card-title">
                    Seçili Sunucu
                </div>

                <div
                    class="card-value"
                    id="homeServer"
                >
                    Seçilmedi
                </div>

            </div>

        </div>

    </section>


    <!-- ROBLOX -->

    <section
        id="roblox"
        class="page"
    >

        <div class="panel">

            <h2>
                Roblox Hesabım
            </h2>

            <p class="muted">
                Roblox hesabını bağlamak için aşağıdaki
                butona bas. Roblox giriş ekranına
                yönlendirileceksin ve girişten sonra
                tekrar bu siteye döneceksin.
            </p>

            <div
                id="robloxAccount"
            ></div>

            <div class="buttons">

                <button
                    class="btn yellow"
                    onclick="location.href='/login/roblox'"
                    id="robloxConnect"
                >
                    Roblox Hesabı Bağla
                </button>

                <button
                    class="btn dark"
                    onclick="logout('roblox')"
                    id="robloxDisconnect"
                    style="display:none"
                >
                    Roblox Bağlantısını Kaldır
                </button>

            </div>

        </div>

    </section>


    <!-- DISCORD -->

    <section
        id="discord"
        class="page"
    >

        <div class="panel">

            <h2>
                Discord Hesabım
            </h2>

            <p class="muted">
                Discord hesabını bağladıktan sonra
                hesabının bulunduğu ve botun erişebildiği
                sunucular listelenecek.
            </p>

            <div
                id="discordAccount"
            ></div>

            <div class="buttons">

                <button
                    class="btn yellow"
                    onclick="location.href='/login/discord'"
                    id="discordConnect"
                >
                    Discord Hesabı Bağla
                </button>

                <button
                    class="btn dark"
                    onclick="logout('discord')"
                    id="discordDisconnect"
                    style="display:none"
                >
                    Discord Bağlantısını Kaldır
                </button>

            </div>

        </div>

    </section>


    <!-- SUNUCULAR -->

    <section
        id="servers"
        class="page"
    >

        <div class="panel">

            <h2>
                Discord Sunucuları
            </h2>

            <p class="muted">
                Discord hesabının bulunduğu sunucular.
                Bot tarafından /ayarlar üzerinden
                yapılandırılmış Roblox grupları olan
                sunucular burada kullanılabilir.
            </p>

            <div id="serverList"></div>

        </div>

    </section>


    <!-- GRUPLAR -->

    <section
        id="groups"
        class="page"
    >

        <div class="panel">

            <h2>
                Roblox Grupları
            </h2>

            <p
                class="muted"
                id="groupText"
            >
                Önce bir Discord sunucusu seç.
            </p>

            <div id="groupList"></div>

        </div>

    </section>

</main>


<script>

let data = {
    roblox: null,
    discord: null,
    guilds: [],
    selectedGuild: null,
    groups: []
};


function page(id, button) {

    document
        .querySelectorAll(".page")
        .forEach(
            x => x.classList.remove("active")
        );

    document
        .getElementById(id)
        .classList.add("active");

    document
        .querySelectorAll(".nav button")
        .forEach(
            x => x.classList.remove("active")
        );

    if(button) {
        button.classList.add("active");
    }

    const titles = {

        home: "Ana Sayfa",

        roblox: "Roblox Hesabım",

        discord: "Discord Hesabım",

        servers: "Sunucular",

        groups: "Gruplar"

    };

    document
        .getElementById("title")
        .textContent =
        titles[id];

    if(id === "servers") {
        renderServers();
    }

    if(id === "groups") {
        renderGroups();
    }
}


function pageByName(id) {

    const buttons =
        document.querySelectorAll(
            ".nav button"
        );

    const index = {

        home: 0,

        roblox: 1,

        discord: 2,

        servers: 3,

        groups: 4

    };

    page(
        id,
        buttons[index[id]]
    );
}


function render() {

    if(data.roblox) {

        document
            .getElementById("homeRoblox")
            .textContent =
            data.roblox.username ||
            data.roblox.display_name;

        document
            .getElementById("robloxAccount")
            .innerHTML = `

                <div class="account-box">

                    <img
                        class="roblox-avatar"
                        src="${escapeHtml(
                            data.roblox.avatar || ""
                        )}"
                    >

                    <div>

                        <strong>
                            ${escapeHtml(
                                data.roblox.username ||
                                data.roblox.display_name
                            )}
                        </strong>

                        <div class="muted">
                            Roblox ID:
                            ${escapeHtml(
                                String(
                                    data.roblox.id
                                )
                            )}
                        </div>

                    </div>

                </div>
            `;

        document
            .getElementById(
                "robloxConnect"
            )
            .style.display =
            "none";

        document
            .getElementById(
                "robloxDisconnect"
            )
            .style.display =
            "inline-block";

        document
            .getElementById(
                "profileName"
            )
            .textContent =
            data.roblox.username ||
            data.roblox.display_name;

    }


    if(data.discord) {

        document
            .getElementById("homeDiscord")
            .textContent =
            data.discord.global_name ||
            data.discord.username;

        document
            .getElementById("discordAccount")
            .innerHTML = `

                <div class="account-box">

                    <div class="avatar">
                        D
                    </div>

                    <div>

                        <strong>
                            ${escapeHtml(
                                data.discord.global_name ||
                                data.discord.username
                            )}
                        </strong>

                        <div class="muted">
                            Discord ID:
                            ${escapeHtml(
                                String(
                                    data.discord.id
                                )
                            )}
                        </div>

                    </div>

                </div>
            `;

        document
            .getElementById(
                "discordConnect"
            )
            .style.display =
            "none";

        document
            .getElementById(
                "discordDisconnect"
            )
            .style.display =
            "inline-block";
    }


    renderServers();
}


function renderServers() {

    const box =
        document.getElementById(
            "serverList"
        );

    if(!data.discord) {

        box.innerHTML = `
            <div class="empty">
                Önce Discord hesabını bağlamalısın.
                <br><br>
                <button
                    class="btn yellow"
                    onclick="pageByName('discord')"
                >
                    Discord Hesabı Bağla
                </button>
            </div>
        `;

        return;
    }


    if(!data.guilds.length) {

        box.innerHTML = `
            <div class="empty">
                Discord hesabının bulunduğu
                sunucu bulunamadı.
            </div>
        `;

        return;
    }


    box.innerHTML =
        data.guilds.map(
            guild => `

                <div
                    class="server ${
                        data.selectedGuild &&
                        data.selectedGuild.id === guild.id
                        ? "selected"
                        : ""
                    }"
                    onclick="selectGuild('${guild.id}')"
                >

                    <div class="server-name">
                        ${escapeHtml(
                            guild.name
                        )}
                    </div>

                    <div class="server-id">
                        Sunucu ID:
                        ${escapeHtml(
                            guild.id
                        )}
                    </div>

                </div>

            `
        ).join("");
}


async function selectGuild(id) {

    const guild =
        data.guilds.find(
            x => x.id === id
        );

    if(!guild) {
        return;
    }

    data.selectedGuild = guild;

    document
        .getElementById(
            "homeServer"
        )
        .textContent =
        guild.name;

    try {

        const response =
            await fetch(
                "/api/groups/" + id
            );

        const result =
            await response.json();

        data.groups =
            result.groups || [];

    } catch {

        data.groups = [];

    }

    renderServers();

    renderGroups();

    pageByName("groups");
}


function renderGroups() {

    const list =
        document.getElementById(
            "groupList"
        );

    const text =
        document.getElementById(
            "groupText"
        );


    if(!data.selectedGuild) {

        text.textContent =
            "Önce bir Discord sunucusu seç.";

        list.innerHTML = `
            <div class="empty">
                Sunucu seçilmedi.
            </div>
        `;

        return;
    }


    text.textContent =
        data.selectedGuild.name +
        " sunucusu için /ayarlar üzerinden yapılandırılmış Roblox grupları.";


    if(!data.groups.length) {

        list.innerHTML = `
            <div class="empty">
                Bu sunucuda henüz Roblox grubu
                yapılandırılmamış.
            </div>
        `;

        return;
    }


    list.innerHTML =
        data.groups.map(
            group => `

                <div class="group">

                    <div>

                        <strong>
                            ${escapeHtml(
                                group.name
                            )}
                        </strong>

                        <div class="muted">
                            Grup ID:
                            ${escapeHtml(
                                String(
                                    group.id
                                )
                            )}
                        </div>

                    </div>

                    <button
                        class="btn yellow"
                        onclick="chooseGroup('${group.id}')"
                    >
                        Seç
                    </button>

                </div>

            `
        ).join("");
}


function chooseGroup(id) {

    const group =
        data.groups.find(
            x => String(x.id) === String(id)
        );

    if(!group) {
        return;
    }

    alert(
        group.name +
        " seçildi."
    );
}


async function logout(type) {

    await fetch(
        "/api/logout/" + type,
        {
            method: "POST"
        }
    );

    location.reload();
}


async function load() {

    try {

        const response =
            await fetch(
                "/api/me"
            );

        const result =
            await response.json();

        data.roblox =
            result.roblox || null;

        data.discord =
            result.discord || null;

        data.guilds =
            result.guilds || [];

        render();

    } catch(error) {

        console.log(error);

    }
}


function escapeHtml(value) {

    return String(value)
        .replace(
            /[&<>"']/g,
            char => ({
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            }[char])
        );
}


load();

</script>

</body>

</html>
"""


# =========================================================
# ANA SAYFA ROUTE
# =========================================================

@app.route("/")
def index():

    return render_template_string(
        HTML
    )


# =========================================================
# API - KULLANICI
# =========================================================

@app.route("/api/me")
def api_me():

    return {

        "roblox":
            session.get("roblox"),

        "discord":
            session.get("discord"),

        "guilds":
            session.get(
                "discord_guilds",
                []
            )

    }


# =========================================================
# API - SUNUCU GRUPLARI
# =========================================================

@app.route(
    "/api/groups/<guild_id>"
)
def api_groups(guild_id):

    configs = load_group_config()

    guild_config = configs.get(
        str(guild_id),
        {}
    )

    return {

        "groups":
            guild_config.get(
                "groups",
                []
            )

    }


# =========================================================
# LOGOUT
# =========================================================

@app.route(
    "/api/logout/roblox",
    methods=["POST"]
)
def logout_roblox():

    session.pop(
        "roblox",
        None
    )

    session.pop(
        "roblox_access_token",
        None
    )

    return {
        "ok": True
    }


@app.route(
    "/api/logout/discord",
    methods=["POST"]
)
def logout_discord():

    session.pop(
        "discord",
        None
    )

    session.pop(
        "discord_guilds",
        None
    )

    return {
        "ok": True
    }


# =========================================================
# RENDER
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            "10000"
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )
