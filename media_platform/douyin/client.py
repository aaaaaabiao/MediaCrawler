import asyncio
import copy
import urllib.parse
from typing import Any, Callable, Dict, List, Optional

import execjs
import httpx
from playwright.async_api import BrowserContext, Page

from tools import utils
from var import request_keyword_var

from .exception import *
from .field import *
import json


class DOUYINClient:
    def __init__(
            self,
            timeout=30,
            proxies=None,
            *,
            headers: Dict,
            playwright_page: Optional[Page],
            cookie_dict: Dict
    ):
        self.proxies = proxies
        self.timeout = timeout
        self.headers = headers
        self._host = "https://www.douyin.com"
        self.playwright_page = playwright_page
        self.cookie_dict = cookie_dict

    async def __process_req_params(self, params: Optional[Dict] = None, headers: Optional[Dict] = None):
        if not params:
            return
        headers = headers or self.headers
        local_storage: Dict = await self.playwright_page.evaluate("() => window.localStorage")  # type: ignore
        douyin_js_obj = execjs.compile(open('libs/douyin.js').read())
        common_params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "cookie_enabled": "true",
            "browser_language": "zh-CN",
            "browser_platform": "Win32",
            "browser_name": "Firefox",
            "browser_version": "110.0",
            "browser_online": "true",
            "engine_name": "Gecko",
            "os_name": "Windows",
            "os_version": "10",
            "engine_version": "109.0",
            "platform": "PC",
            "screen_width": "1920",
            "screen_height": "1200",
            # " webid": douyin_js_obj.call("get_web_id"),
            # "msToken": local_storage.get("xmst"),
            # "msToken": "abL8SeUTPa9-EToD8qfC7toScSADxpg6yLh2dbNcpWHzE0bT04txM_4UwquIcRvkRb9IU8sifwgM1Kwf1Lsld81o9Irt2_yNyUbbQPSUO8EfVlZJ_78FckDFnwVBVUVK",
        }
        params.update(common_params)
        query = '&'.join([f'{k}={v}' for k, v in params.items()])
        x_bogus = douyin_js_obj.call('sign', query, headers["User-Agent"])
        params["X-Bogus"] = x_bogus
        # print(x_bogus, query)

    async def request(self, method, url, **kwargs):
        async with httpx.AsyncClient(proxies=self.proxies) as client:
            response = await client.request(
                method, url, timeout=self.timeout,
                **kwargs
            )
            try:
                return response.json()
            except Exception as e:
                raise DataFetchError(f"{e}, {response.text}")

    async def get(self, uri: str, params: Optional[Dict] = None, headers: Optional[Dict] = None):
        await self.__process_req_params(params, headers)
        headers = headers or self.headers
        return await self.request(method="GET", url=f"{self._host}{uri}", params=params, headers=headers)

    async def post(self, uri: str, data: dict, headers: Optional[Dict] = None):
        await self.__process_req_params(data, headers)
        headers = headers or self.headers
        return await self.request(method="POST", url=f"{self._host}{uri}", data=data, headers=headers)

    @staticmethod
    async def pong(browser_context: BrowserContext) -> bool:
        _, cookie_dict = utils.convert_cookies(await browser_context.cookies())
        # todo send some api to test login status
        return cookie_dict.get("LOGIN_STATUS") == "1"

    async def update_cookies(self, browser_context: BrowserContext):
        cookie_str, cookie_dict = utils.convert_cookies(await browser_context.cookies())
        self.headers["Cookie"] = cookie_str
        self.cookie_dict = cookie_dict

    async def search_info_by_keyword(
            self,
            keyword: str,
            offset: int = 0,
            search_channel: SearchChannelType = SearchChannelType.GENERAL,
            sort_type: SearchSortType = SearchSortType.GENERAL,
            publish_time: PublishTimeType = PublishTimeType.UNLIMITED
    ):
        """
        DouYin Web Search API
        :param keyword:
        :param offset:
        :param search_channel:
        :param sort_type:
        :param publish_time: ·
        :return:
        """
        params = {
            "keyword": keyword,
            "search_channel": search_channel.value,
            "sort_type": sort_type.value,
            "publish_time": publish_time.value,
            "search_source": "normal_search",
            "query_correct_type": "1",
            "is_filter_search": "0",
            "offset": offset,
            "count": 10  # must be set to 10
        }
        referer_url = "https://www.douyin.com/search/" + keyword
        headers = copy.copy(self.headers)
        headers["Referer"] = urllib.parse.quote(referer_url, safe=':/')
        return await self.get("/aweme/v1/web/general/search/single/", params, headers=headers)

    async def get_video_by_id(self, aweme_id: str) -> Any:
        """
        DouYin Video Detail API
        :param aweme_id:
        :return:
        """
        params = {
            "aweme_id": aweme_id
        }
        headers = copy.copy(self.headers)
        # headers["Cookie"] = "s_v_web_id=verify_lol4a8dv_wpQ1QMyP_xemd_4wON_8Yzr_FJa8DN1vdY2m;"
        del headers["Origin"]
        res = await self.get("/aweme/v1/web/aweme/detail/", params, headers)
        utils.logger.info(f"get_video_by_id aweme_id:{aweme_id}")
        return res.get("aweme_detail", {})

    async def get_video_by_user_id(self, user_id: str) -> Any:
        """
        DouYin Video Detail API
        :param aweme_id:
        :return:
        """

        max_cursor = 0
        aweme_res = []

        while True:
            params = {
                "sec_user_id": user_id,
                "max_cursor": max_cursor,
                "count": 18
            }
            headers = copy.copy(self.headers)
            # headers["Cookie"] = "s_v_web_id=verify_lol4a8dv_wpQ1QMyP_xemd_4wON_8Yzr_FJa8DN1vdY2m;"
            del headers["Origin"]
            res = await self.get("/aweme/v1/web/aweme/post", params, headers)
            aweme_list = res['aweme_list']
            max_cursor = res['max_cursor']
            has_more = res["has_more"]
            utils.logger.info(
                f"user_id_aweme_detail: max_cursor:{utils.get_time_str_from_unix_time(max_cursor)}, total:{len(aweme_res)}")
            for aweme in aweme_list:
                try:
                    aweme_id = aweme['aweme_id']
                    aweme_detail = await self.get_video_by_id(aweme_id)
                    aweme_res.append(aweme_detail)
                except Exception as ex:
                    utils.logger.error(f"[DOUYINClient.get_video_by_user_id] error, ex:{ex}, aweme:{aweme}")
            if has_more != 1:
                break
        return {
            "user_id": user_id,
            "awemes": aweme_res
        }

    async def get_aweme_comments(self, aweme_id: str, cursor: int = 0):
        """get note comments

        """
        uri = "/aweme/v1/web/comment/list/"
        params = {
            "aweme_id": aweme_id,
            "cursor": cursor,
            "count": 20,
            "item_type": 0
        }
        keywords = request_keyword_var.get()
        referer_url = "https://www.douyin.com/search/" + keywords + '?aid=3a3cec5a-9e27-4040-b6aa-ef548c2c1138&publish_time=0&sort_type=0&source=search_history&type=general'
        headers = copy.copy(self.headers)
        headers["Referer"] = urllib.parse.quote(referer_url, safe=':/')
        return await self.get(uri, params)

    async def get_aweme_all_comments(
            self,
            aweme_id: str,
            crawl_interval: float = 1.0,
            is_fetch_sub_comments=False,
            callback: Optional[Callable] = None,
            max_comments: int = None,  # 新增参数来限制评论数
            keywords: List[str] = None  # 新增参数，用于关键字筛选
    ):
        """
        获取帖子的所有评论，包括子评论
        :param aweme_id: 帖子ID
        :param crawl_interval: 抓取间隔
        :param is_fetch_sub_comments: 是否抓取子评论
        :param callback: 回调函数，用于处理抓取到的评论
        :param max_comments: 最大评论数限制，如果为0，则不限制评论数
        :param keywords: 需要过滤的关键字列表
        :return: 评论列表
        """
        result = []
        comments_has_more = 1
        comments_cursor = 0
        collected_comments_count = 0  # 已收集的评论数

        while comments_has_more and (
                max_comments is None or collected_comments_count < max_comments or max_comments == 0):
            comments_res = await self.get_aweme_comments(aweme_id, comments_cursor)
            comments_has_more = comments_res.get("has_more", 0)
            comments_cursor = comments_res.get("cursor", 0)
            comments = comments_res.get("comments", [])
            if not comments:
                continue

            # 在添加评论到结果列表之前进行关键字筛选
            if keywords:
                filtered_comments = []
                for comment in comments:
                    if any(keyword in comment.get("text", "") for keyword in keywords):
                        filtered_comments.append(comment)
            else:
                filtered_comments = comments

            # 如果设置了最大评论数限制，并且不为0，只添加未超过该限制的评论
            if max_comments is not None and max_comments > 0:
                remaining_quota = max_comments - collected_comments_count
                comments_to_add = filtered_comments[:remaining_quota]
                result.extend(comments_to_add)
                collected_comments_count += len(comments_to_add)
            else:
                result.extend(filtered_comments)
                collected_comments_count += len(filtered_comments)

            if callback:  # 如果有回调函数，就执行回调函数
                await callback(aweme_id, comments)

            # 如果已经达到最大评论数（且最大评论数不为0），或者不需要子评论，结束循环
            if max_comments is not None and 0 < max_comments <= collected_comments_count:
                break

            await asyncio.sleep(crawl_interval)
            if not is_fetch_sub_comments:
                continue
            # todo fetch sub comments
        return result
