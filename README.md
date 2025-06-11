
# YouTube Comments Crawler

一个基于 Selenium 的 YouTube 视频评论爬虫工具，能够自动获取指定视频的评论数据并保存为 JSON 格式。

## 功能特性

- 🤖 **智能反检测**: 采用多种策略降低被 YouTube 检测的风险
- 🎯 **精准爬取**: 获取评论内容、作者、点赞数、发布时间等完整信息
- 📱 **人性化操作**: 模拟真实用户行为，包括随机滚动和延迟
- 💾 **数据保存**: 自动将评论数据保存为 JSON 文件
- 🔧 **灵活配置**: 支持无头模式、代理设置等多种配置选项
- 📊 **进度显示**: 实时显示爬取进度和日志记录

## 系统要求

- Python 3.7+
- Chrome 浏览器
- 稳定的网络连接

## 安装依赖

```bash
pip install selenium webdriver-manager
```

## 快速开始

### 1. 基本使用

```python
from youtube_crawl import YouTubeSeleniumScraper

# 创建爬虫实例
scraper = YouTubeSeleniumScraper()

# 设置要爬取的视频ID (从YouTube URL中获取)
VIDEO_ID = "fK85SQzm0Z0"  # 例如: https://www.youtube.com/watch?v=fK85SQzm0Z0

try:
    # 打开视频
    if scraper.open_video(VIDEO_ID):
        # 获取评论 (默认最多300条)
        comments = scraper.get_video_comments(max_comments=100)
        
        # 保存到文件
        if comments:
            filename = scraper.save_comments_to_file(comments, VIDEO_ID)
            print(f"成功保存 {len(comments)} 条评论到 {filename}")
        else:
            print("未获取到评论")
            
finally:
    scraper.close()
```

### 2. 高级配置

```python
# 使用无头模式和代理
scraper = YouTubeSeleniumScraper(
    headless=True,           # 后台运行，不显示浏览器窗口
    use_proxy=True,          # 使用代理
    proxy="127.0.0.1:8080"   # 代理服务器地址
)

# 自定义爬取参数
comments = scraper.get_video_comments(
    max_comments=500,        # 最大评论数量
    scroll_pause_time=4      # 滚动间隔时间(秒)
)
```

## 获取视频ID

从 YouTube 视频链接中提取ID:

- 完整链接: `https://www.youtube.com/watch?v=fK85SQzm0Z0`
- 视频ID: `fK85SQzm0Z0`

## 输出格式

评论数据将保存为 JSON 格式，包含以下字段:

```json
[
    {
        "author": "用户名",
        "content": "评论内容",
        "likes": 123,
        "time": "1天前"
    }
]
```

## 反检测机制

本工具采用多种策略避免被检测:

- **随机User-Agent**: 模拟不同浏览器和设备
- **人性化行为**: 随机滚动、延迟和窗口大小
- **浏览器指纹修改**: 移除自动化标识
- **渐进式加载**: 模拟真实用户浏览行为

## 日志记录

程序会自动生成日志文件 `youtube_scraper.log`，记录:

- 爬取进度和状态
- 错误信息和异常处理
- 性能统计和调试信息

## 注意事项

### ⚠️ 使用限制

- **遵守YouTube服务条款**: 仅用于研究和学习目的
- **适度使用**: 避免频繁请求导致IP被封
- **尊重版权**: 不要将爬取的内容用于商业用途

### 🛠️ 常见问题

**Q: 程序运行缓慢怎么办？**
A: 可以调整 `scroll_pause_time` 参数，但过快可能被检测

**Q: 无法获取评论？**
A: 检查视频是否禁用评论，或网络连接是否稳定

**Q: Chrome驱动问题？**
A: 程序会自动下载匹配的ChromeDriver，确保Chrome浏览器已安装

## 项目结构

```
youtube_crawl.py          # 主程序文件
youtube_scraper.log       # 日志文件
comments_[ID]_[时间].json # 输出的评论数据
```

## 开发信息

- **作者**: Xieyiw
- **创建时间**: 2025/5/8
- **Python版本**: 3.7+
- **主要依赖**: Selenium, WebDriver Manager

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和平台服务条款。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

---

如果这个项目对您有帮助，请给个 ⭐ Star！
