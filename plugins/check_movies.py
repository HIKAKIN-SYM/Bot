# Compatible with Python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from datetime import datetime
import requests
import dateutil.parser
import importlib.util
from pychroner import PluginMeta, PluginType


@PluginMeta(PluginType.Schedule, multipleMinute=10)
def do(plugin_api):
    now = datetime.now()
    logger = plugin_api.getLogger()
    config = plugin_api.config.secret.hikakin_sym
    user_db_path = os.path.join(plugin_api.dirs.cache, "hikakin_movies.db")
    twitter = plugin_api.getTwitterAccount("HIKAKIN_SYM").getTweepyHandler(retry_count=5, retry_delay=10)
    spec = importlib.util.spec_from_file_location("sym", os.path.join(os.path.dirname(os.path.abspath(__file__)), "sym.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sym = mod.Symmetry(api_key=config["cloudvision_key"], save_dir=plugin_api.dirs.cache, logger=logger)

    """ ヒカキン関連チャンネルID
    HIKAKIN: UClLV6D8S4CrVJL64-aQvwTw
    HikakinTV: UCZf__ehlCEBPop-_sldpBUQ
    HikakinGames: UCX1xppLvuj03ubLio8jslyA
    HikakinBlog: UCQMoeRP9SDaFipXDBIp3pFA
    SeikinTV: UCg4nOl7_gtStrLwF0_xoV0A(こいつはヒカキンじゃねえから除外)

    channelIDs = ["UClLV6D8S4CrVJL64-aQvwTw", "UCZf__ehlCEBPop-_sldpBUQ", "UCX1xppLvuj03ubLio8jslyA",
                  "UCQMoeRP9SDaFipXDBIp3pFA"]

    # チャンネルIDから投稿動画のプレイリストを取得する場合
    target = "https://www.googleapis.com/youtube/v3/channels"
    playlist_ids = []
    params = {}
    params["key"] = setting["auth"]["youtube_key"]
    params["part"] = "contentDetails"

    for i in channelIDs:
        params["id"] = i
        r = requests.get(target, params=params).json()
        playlistId = r["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        playlist_ids.append(playlistId)
    """

    playlist_ids = [
        'UUlLV6D8S4CrVJL64-aQvwTw',
        'UUZf__ehlCEBPop-_sldpBUQ',
        'UUX1xppLvuj03ubLio8jslyA',
        'UUQMoeRP9SDaFipXDBIp3pFA'
    ]

    target = "https://www.googleapis.com/youtube/v3/playlistItems"
    playlists = []
    params = {"key": config["youtube_key"], "part": "snippet", "maxResults": 10}

    for i in playlist_ids:  # プレイリストIDを使い投稿動画を取得
        params["playlistId"] = i
        r = requests.get(target, params=params)
        r.raise_for_status()
        playlists.append(r.json())

    with sqlite3.connect(user_db_path, check_same_thread=False) as db:
        if not db.execute("SELECT * FROM sqlite_master WHERE name = ?", ("movies",)).fetchone():
            logger.info("動画の初回登録を開始します。")
            db.execute("CREATE TABLE movies(video_id TEXT, title TEXT, thumb TEXT, published_at TEXT, created_at TEXT)")
            for playlist in playlists:
                for item in playlist["items"]:
                    published_at = dateutil.parser.parse(item["snippet"]["publishedAt"])
                    thumb = max([[d["width"], d["url"]] for types, d in item["snippet"]["thumbnails"].items()], key=lambda x: x[0])[1]
                    data = [item["snippet"]["resourceId"]["videoId"], item["snippet"]["title"], thumb, published_at, now]
                    db.execute('INSERT INTO movies VALUES (?, ?, ?, ?, ?)', data)
                    logger.info("挿入: {}/{}".format(item["snippet"]["resourceId"]["videoId"], item["snippet"]["title"]))

        else:
            for playlist in playlists:
                for item in playlist["items"]:
                    sql = 'SELECT * FROM movies WHERE video_id = ?'
                    query = db.execute(sql, (item["snippet"]["resourceId"]["videoId"],)).fetchone()

                    if not query:
                        published_at = dateutil.parser.parse(item["snippet"]["publishedAt"])
                        thumb = max([[d["width"], d["url"]] for types, d in item["snippet"]["thumbnails"].items()], key=lambda x: x[0])[1]
                        sql = 'INSERT INTO movies VALUES (?, ?, ?, ?, ?)'
                        data = (item["snippet"]["resourceId"]["videoId"], item["snippet"]["title"], thumb, published_at, now)
                        db.execute(sql, data)
                        db.commit()
                        logger.info("挿入: {}/{}".format(item["snippet"]["resourceId"]["videoId"], item["snippet"]["title"]))

                        logger.info("『{}』の顔認識を開始します。".format(item["snippet"]["title"]))
                        sym_result = sym.do(thumb)

                        logger.info(thumb)

                        for c, n in enumerate(sym_result):
                            logger.info("{}枚目のアップロードを開始します。".format(c + 1))
                            media_ids = [twitter.media_upload(m).media_id_string for m in n]
                            twitter.update_status(status="", media_ids=media_ids)
                            logger.info("アップロードを完了しました。")
                        [[os.remove(m) for m in n if os.path.exists(m)] for n in sym_result]
