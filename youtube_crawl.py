
# _*_ coding : uft-8 _*_
# @Time : 2025/5/8 19:07
# @Auther : Xieyiw
# @File : youtube_crawl
# @Project : PythonProject2
from jedi.inference.value.instance import SelfName
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

import time
import random
import json
import re
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='../youtube_scraper.log'
)


class YouTubeSeleniumScraper:
    """使用Selenium访问YouTube视频并获取评论的类"""

    def __init__(self, headless=False, use_proxy=False, proxy=None):
        """初始化Selenium浏览器配置

        Args:
            headless: 是否使用无头模式
            use_proxy: 是否使用代理
            proxy: 代理服务器地址 (格式: "ip:port")
        """
        self.options = Options()

        # 基础配置 - 降低被检测风险
        self.options.add_argument("--disable-blink-features=AutomationControlled")  # 禁用自动化控制特征
        self.options.add_argument("--disable-infobars")  # 禁用信息栏
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"],)  # 排除自动化开关
        self.options.add_experimental_option("useAutomationExtension", False)  # 不使用自动化扩展

        # 添加随机UA - 重要反检测措施
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15"
        ]
        self.options.add_argument(f"user-agent={random.choice(user_agents)}")

        # 添加更多随机浏览器指纹参数
        self.options.add_argument(f"--window-size={random.randint(1050, 1200)},{random.randint(800, 950)}")

        # 设置语言偏好 (可以根据需要调整)
        self.options.add_argument("--lang=zh-CN,zh;q=0.9,en;q=0.8")

        # 无头模式配置 (可选)
        if headless:
            self.options.add_argument("--headless")  # 无头模式

        # 代理设置 (可选，但对于防止IP被封非常有用)
        if use_proxy and proxy:
            self.options.add_argument(f'--proxy-server={proxy}')
            logging.info(f"使用代理: {proxy}")

        # 初始化WebDriver
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

        # 修改navigator.webdriver标志，降低被检测可能性
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # 设置页面加载超时
        self.driver.set_page_load_timeout(30)

        logging.info("浏览器初始化完成")

    def human_like_delay(self, min_seconds=1, max_seconds=3):
        """模拟人类行为的随机延迟"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay

    def random_scroll(self, min_scrolls=3, max_scrolls=7, min_distance=300, max_distance=800):
        """执行随机滚动，模拟真实用户浏览行为"""
        num_scrolls = random.randint(min_scrolls, max_scrolls)

        for _ in range(num_scrolls):
            # 随机滚动距离
            scroll_distance = random.randint(min_distance, max_distance)

            # 这里是用了javascript实现滚动操作，f"window.scrollBy(x:水平滚动,y：竖直滚动);"
            self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")

            self.human_like_delay(1, 2)

    def open_video(self, video_id):
        """打开YouTube视频并等待加载

        Args:
            video_id: YouTube视频ID

        Returns:
            bool: 视频是否成功加载
        """
        url = f"https://www.youtube.com/watch?v={video_id}"
        logging.info(f"尝试打开视频: {url}")

        try:
            # 随机化访问行为
            self.driver.get("https://www.youtube.com/")
            self.human_like_delay(2, 4)

            # 搜索栏输入视频ID
            self.driver.get(url)

            # 等待视频播放器加载
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "movie_player"))
            )

            # 调整音量 (模拟用户行为)
            self.human_like_delay()
            try:
                # 尝试暂停视频 (降低资源使用)，执行了视频暂停源代码
                self.driver.execute_script(
                    "document.querySelector('video').pause();"
                )
            except:
                pass

            # 执行一些随机滚动，查看视频说明等；可写参数，默认用方法中的参数
            self.random_scroll(2, 4)

            # 启动title方法，获取html源码中<head>中的<title>标签内容(有且只有一个)
            video_title = self.driver.title
            # 日志记录视频名称
            logging.info(f"成功加载视频: {video_title}")

            return True

        except TimeoutException:
            logging.error(f"视频加载超时: {video_id}")
            return False
        except Exception as e:
            logging.error(f"打开视频时出错: {str(e)}")
            return False

    def get_video_comments(self, max_comments=300, scroll_pause_time=3.5):
        """获取当前打开视频的评论

        Args:
            max_comments: 最大获取评论数量
            scroll_pause_time: 每次滚动后等待的秒数

        Returns:
            list: 评论列表
        """
        comments = []
        # 标记变量
        comment_section_found = False

        try:
            # 滚动到评论区
            self.driver.execute_script("window.scrollBy(0, 600);")
            self.human_like_delay()

            # 等待评论区加载 - YouTube使用#comments作为评论区ID
            try:
                comment_section = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-comments#comments"))
                )
                comment_section_found = True
            except TimeoutException:
                logging.warning("未找到评论区，视频可能禁用了评论")
                return []

            if comment_section_found:
                # 通过元素定位滚动到评论区(更精确)，并确保它被激活，arguments[0]表示占位符——comment_section中的第一个元素——指定位到的评论区
                self.driver.execute_script("arguments[0].scrollIntoView();", comment_section)
                self.human_like_delay(1, 2)

                # 现在开始滚动加载更多评论
                last_comment_count = 0
                retry_count = 0

                # 初始comments=[],参数为零
                while len(comments) < max_comments and retry_count < 5:
                    # 收集当前可见的评论框架，包括评论，ID，点赞数，时间，comment_elements返回列表
                    # 每滚动刷新出新页面，comment_elements会从初始页面一直统计到最新页面，由此comment_elements会不断增加
                    comment_elements = self.driver.find_elements(By.CSS_SELECTOR, "ytd-comment-thread-renderer")

                    # 如果找到新评论，处理它们。每次向下滚动600像素，一次性获取到的评论不一定为20条。如果收集到的评论数量大于最新评论数量：
                    if len(comment_elements) > last_comment_count:

                        #初始range(最新评论数量:0,收集评论数量:1～20)
                        for i in range(last_comment_count, len(comment_elements)):
                            if i >= len(comment_elements):
                                break

                            try:
                                comment_element = comment_elements[i]

                                # 提取作者信息
                                author = comment_element.find_element(By.CSS_SELECTOR, "#author-text").text.strip()

                                # 提取评论内容
                                comment_content = comment_element.find_element(By.CSS_SELECTOR,
                                                                               "#content-text").text.strip()

                                # 提取点赞数
                                try:
                                    like_element = comment_element.find_element(By.CSS_SELECTOR, "#vote-count-middle")
                                    likes_text = like_element.text.strip()
                                    # 处理不同格式的点赞数
                                    if likes_text:
                                        if '万' in likes_text:
                                            likes = float(likes_text.replace('万', '')) * 10000
                                        else:
                                            # 使用正则表达式，将非数字内容替换为空格，if处理后的字符串如果非空 > 转换为整数 > 否则为0
                                            likes = int(re.sub(r'[^\d]', '', likes_text))\
                                                if re.sub(r'[^\d]', '', likes_text) else 0
                                    else:
                                        likes = 0
                                except:
                                    likes = 0

                                # 提取评论时间
                                try:
                                    time_element = comment_element.find_element(By.CSS_SELECTOR, "#published-time-text")
                                    comment_time = time_element.text.strip()
                                except:
                                    comment_time = "未知时间"

                                comment_data = {
                                    "author": author,
                                    "content": comment_content,
                                    "likes": likes,
                                    "time": comment_time
                                }
                                # 往comments列表中不断加入字典,20,40,60,80,100
                                comments.append(comment_data)

                                # 如果达到目标数量则停止
                                if len(comments) >= max_comments:
                                    break

                            except Exception as e:
                                logging.warning(f"处理评论时出错: {str(e)}")

                        # 更新计数器
                        last_comment_count = len(comment_elements)
                        retry_count = 0  # 重置重试计数器
                    else:
                        retry_count += 1
                        self.driver.execute_script("window.scrollBy(0, 1000);")
                        # 增加随机等待时间
                        self.human_like_delay(scroll_pause_time, scroll_pause_time + 2)

                    # 显示进度
                    logging.info(f"已获取 {len(comments)}/{max_comments} 条评论")

                    # 以人类方式滚动获取更多评论
                    self.driver.execute_script("window.scrollBy(0, 600);")

                    # 随机停顿，模拟用户阅读行为
                    self.human_like_delay(scroll_pause_time - 1, scroll_pause_time + 1)

                logging.info(f"评论获取完成，共 {len(comments)} 条")

        except Exception as e:
            logging.error(f"获取评论时出错: {str(e)}")

        return comments

    def save_comments_to_file(self, comments, video_id):
        """将评论保存到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comments_{video_id}_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            # 将数据转换成json格式，indent表示每层缩紧四个空格
            json.dump(comments, f, ensure_ascii=False, indent=4)

        logging.info(f"评论已保存到文件: {filename}")
        return filename

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logging.info("浏览器已关闭")


# 使用示例
if __name__ == "__main__":
    VIDEO_ID = "fK85SQzm0Z0"  # 替换为目标视频ID

    try:
        # 创建爬虫实例 (设置headless=True可以隐藏浏览器窗口)
        scraper = YouTubeSeleniumScraper(headless=False, use_proxy=False)

        # 打开视频
        if scraper.open_video(VIDEO_ID):
            # 获取评论 (最多获取100条)
            comments = scraper.get_video_comments(max_comments=300)

            # 保存评论
            if comments:
                scraper.save_comments_to_file(comments, VIDEO_ID)

                # 显示前5条评论
                print(f"\n获取到 {len(comments)} 条评论，前5条如下:")
                for i, comment in enumerate(comments[:5]):
                    print(f"\n--- 评论 {i + 1} ---")
                    print(f"作者: {comment['author']}")
                    print(f"内容: {comment['content']}")
                    print(f"点赞: {comment['likes']}")
                    print(f"时间: {comment['time']}")
            else:
                print("没有获取到评论")

    except Exception as e:
        logging.error(f"程序运行错误: {str(e)}")

    finally:
        scraper.close()