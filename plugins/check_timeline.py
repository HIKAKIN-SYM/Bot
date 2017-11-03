# Compatible with Python3
# -*- coding: utf-8 -*-

import os
import importlib.util
from pychroner import PluginMeta, PluginType


@PluginMeta(PluginType.TwitterTimeline, twitterAccount="HIKAKIN_SYM")
def do(plugin_api, stream):
    logger = plugin_api.getLogger()
    config = plugin_api.config.secret.hikakin_sym
    twitter = plugin_api.getTwitterAccount("HIKAKIN_SYM").getTweepyHandler(retry_count=5, retry_delay=10)
    spec = importlib.util.spec_from_file_location("sym", os.path.join(os.path.dirname(os.path.abspath(__file__)), "sym.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sym = mod.Symmetry(api_key=config["cloudvision_key"], save_dir=plugin_api.dirs.cache, logger=logger)

    if stream["user"]["screen_name"].lower() == "hikakin":
        result = stream.get("extended_entities", stream.get("entities", {})).get("media")
        if result is not None:
            logger.info("Twitterにて新しい画像付きツイートを検出しました。")
            for i in result:
                img_url = i.get("media_url_https")

                if img_url is not None:
                    sym_result = sym.do(img_url)
                    for c, n in enumerate(sym_result):
                        text = ""
                        media_ids = [twitter.media_upload(m).media_id_string for m in n]
                        twitter.update_status(status=text, media_ids=media_ids)
                    [[os.remove(m) for m in n if os.path.exists(m)] for n in sym_result]

        else:
            logger.info("ツイートに画像が添付されていませんでした。")
