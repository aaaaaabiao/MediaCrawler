# 基础配置
PLATFORM = "wb"
KEYWORDS = "python,golang"
LOGIN_TYPE = "qrcode"  # qrcode or phone or cookie
COOKIES = "abRequestId=ea50858d-dfc4-57e3-86ab-1ffeccd7276f; a1=18c5bf0ed9deddlk5ts5qxej2x23jypp545brjjqn30000182415; webId=a2c5bc7e83fc8cc41a12067b77fa659f; gid=yYS2Di8i282jyYS2Di8df4VVjfdff1T29M2A2AICdVJCJDq8qVvUUF888yYJ4y28KKfiK4Jf; webBuild=3.21.2; web_session=0400697c486075066853e4bdbe374b1a432e82; websectiga=3fff3a6f9f07284b62c0f2ebf91a3b10193175c06e4f71492b60e056edcdebb2; sec_poison_id=15868c15-71f3-4edb-a7d5-c892644674b0; xsecappid=xhs-pc-web; unread={%22ub%22:%226583c47a000000000801f606%22%2C%22ue%22:%226586553d0000000038030e41%22%2C%22uc%22:21}"
CRAWLER_TYPE = "detail"

# 是否开启 IP 代理
ENABLE_IP_PROXY = False

# 代理IP池数量
IP_PROXY_POOL_COUNT = 2

# 重试时间
RETRY_INTERVAL = 60 * 30  # 30 minutes

# 无头浏览器的标识，True:开启 False 关闭（会打开一个浏览器）
HEADLESS = False

# 是否保存登录状态
SAVE_LOGIN_STATE = False

# 用户浏览器缓存的浏览器文件配置
USER_DATA_DIR = "%s_user_data_dir"  # %s will be replaced by platform name

# 爬取视频/帖子的数量控制
CRAWLER_MAX_NOTES_COUNT = 20

# 并发爬虫数量控制
MAX_CONCURRENCY_NUM = 4

# 每个视频/帖子抓取评论最大条数 (为0则不限制)
MAX_COMMENTS_PER_POST = 10

# 评论关键词筛选(只会留下包含关键词的评论,为空不限制)
COMMENT_KEYWORDS = [
    # "真棒"
    # ........................
]

# 指定小红书需要爬虫的笔记ID列表
XHS_SPECIFIED_ID_LIST = [
    "6586596c0000000006020f08"
    # ........................
]

# 指定小红书需要爬虫的用户列表
XHS_USER_ID_LIST = [
    "643384a4000000000d01a16c"
    # ........................
]

# 指定抖音需要爬取的ID列表
DY_SPECIFIED_ID_LIST = [
    "7314926791997607231"
    # ........................
]

# 指定快手平台需要爬取的ID列表
KS_SPECIFIED_ID_LIST = []

# 指定B站平台需要爬取的视频bvid列表
BILI_SPECIFIED_ID_LIST = [
    "BV1d54y1g7db",
    "BV1Sz4y1U77N",
    "BV14Q4y1n7jz",
    # ........................
]

# 指定微博平台需要爬取的帖子列表
WEIBO_SPECIFIED_ID_LIST = [
    "4982041758140155",
    # ........................
]