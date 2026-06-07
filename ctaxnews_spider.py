import requests
from bs4 import BeautifulSoup
from datetime import datetime

def crawl_ctaxnews():
    """
    抓取《中国税务报》电子报头版的最新新闻
    自动处理日期动态变化的 URL
    """
    # 1. 自动获取今天的日期，拼装成 202606/05 这种格式
    today_str = datetime.now().strftime("%Y%m/%d")
    
    # 2. 动态生成今天的头版 (node_01) 链接
    url = f"https://www.ctaxnews.net.cn/paper/pc/layout/{today_str}/node_01.html"
    
    # 伪装成浏览器，防止被拦截
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    news_items = []
    try:
        print(f"正在抓取中国税务报: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8' 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        base_url = url.rsplit('/', 1)[0] + '/'
        
        for a_tag in soup.select('a'):
            href = a_tag.get('href', '')
            if 'content_' in href:
                title = a_tag.text.strip()
                if title: 
                    full_url = base_url + href
                    news_items.append({
                        "title": title,
                        "url": full_url,
                        "source": "中国税务报",
                        "category": "news",
                        "publishedAt": datetime.now().strftime("%Y-%m-%d")
                    })
                    
        # 去重
        unique_news = []
        seen_urls = set()
        for item in news_items:
            if item["url"] not in seen_urls:
                unique_news.append(item)
                seen_urls.add(item["url"])
                
        return unique_news

    except Exception as e:
        print(f"抓取中国税务报失败: {e}")
        return []

def crawl_esnai_law():
    """
    抓取《中国会计视野-法规库》首页最新收录的法规政策
    URL: https://law.esnai.cn/
    """
    url = "https://law.esnai.cn/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    news_items = []
    try:
        print(f"正在抓取会计视野法规库: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        # 确保中文不乱码
        response.encoding = response.apparent_encoding 
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 遍历所有链接，寻找法规标题
        for a_tag in soup.select('a'):
            href = a_tag.get('href', '')
            title = a_tag.text.strip()
            
            # 过滤逻辑：
            # 1. 标题存在且长度大于8个字符（规避短词和导航栏）
            # 2. 必须包含具体的链接
            if title and len(title) > 8 and href and href != '#':
                # 拼接完整绝对路径
                if href.startswith('/'):
                    full_url = "https://law.esnai.cn" + href
                elif not href.startswith('http'):
                    full_url = "https://law.esnai.cn/" + href
                else:
                    full_url = href
                
                news_items.append({
                    "title": title,
                    "url": full_url,
                    "source": "中国会计视野",
                    "category": "policy", # 归类为政策法规
                    "publishedAt": datetime.now().strftime("%Y-%m-%d")
                })
        
        # 去重：按标题去重，因为有时候首页会有重复的推荐链接
        unique_news = []
        seen_titles = set()
        for item in news_items:
            if item["title"] not in seen_titles:
                unique_news.append(item)
                seen_titles.add(item["title"])
                
        # 首页数据可能很多，返回前20条最新政策即可
        return unique_news[:20]

    except Exception as e:
        print(f"抓取会计视野失败: {e}")
        return []

def crawl_chinatax():
    """
    抓取《国家税务总局-政策法规库》最新文件
    URL: https://fgk.chinatax.gov.cn/zcfgk/c100006/listflfg.html
    注意：政府网站可能有强反爬或动态加载，此处为基础结构。
    """
    url = "https://fgk.chinatax.gov.cn/zcfgk/c100006/listflfg.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://fgk.chinatax.gov.cn/"
    }
    news_items = []
    try:
        print(f"正在抓取国家税务总局: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 假设列表在一个特定的 ul 或 div 中（需根据实际DOM微调）
        for a_tag in soup.select('a'):
            title = a_tag.text.strip()
            href = a_tag.get('href', '')
            if title and '号' in title and len(title) > 10: # 政策文件通常带文号且较长
                full_url = href if href.startswith('http') else "https://fgk.chinatax.gov.cn" + href
                news_items.append({
                    "title": title,
                    "url": full_url,
                    "source": "国家税务总局",
                    "category": "policy",
                    "publishedAt": datetime.now().strftime("%Y-%m-%d") # 实际情况应从DOM提取日期
                })
        return news_items[:15]
    except Exception as e:
        print(f"抓取国家税务总局失败: {e}")
        return []

def crawl_shui5():
    """
    抓取《税屋》最新政策 (民间权威汇总站)
    URL: https://www.shui5.cn/
    """
    url = "https://www.shui5.cn/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    news_items = []
    try:
        print(f"正在抓取税屋: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gb2312' # 税屋通常是GBK/GB2312编码
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for li in soup.select('li'):
            a_tag = li.find('a')
            if a_tag:
                title = a_tag.text.strip()
                href = a_tag.get('href', '')
                if title and len(title) > 8 and '/article/' in href:
                    full_url = href if href.startswith('http') else "https://www.shui5.cn" + href
                    news_items.append({
                        "title": title,
                        "url": full_url,
                        "source": "税屋",
                        "category": "policy",
                        "publishedAt": datetime.now().strftime("%Y-%m-%d")
                    })
        return news_items[:15]
    except Exception as e:
        print(f"抓取税屋失败: {e}")
        return []

def crawl_mof():
    """
    抓取《财政部-政策发布》
    URL: https://www.mof.gov.cn/zhengwuxinxi/zhengcefabu/
    """
    url = "https://www.mof.gov.cn/zhengwuxinxi/zhengcefabu/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    news_items = []
    try:
        print(f"正在抓取财政部: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for a_tag in soup.select('a'):
            title = a_tag.get('title') or a_tag.text.strip()
            href = a_tag.get('href', '')
            # 过滤带日期的链接，如 ./202606/t20260607_xxxx.htm
            if title and len(title) > 10 and './' in href and '.htm' in href:
                full_url = url + href[2:]
                news_items.append({
                    "title": title,
                    "url": full_url,
                    "source": "财政部",
                    "category": "policy",
                    "publishedAt": datetime.now().strftime("%Y-%m-%d")
                })
        return news_items[:10]
    except Exception as e:
        print(f"抓取财政部失败: {e}")
        return []

# ==========================================
# 本地测试代码
# ==========================================
if __name__ == "__main__":
    print("开始执行财税新闻爬虫矩阵...\n")
    
    # 1. 测试税务报
    ctax_result = crawl_ctaxnews()
    print(f"【中国税务报】共抓取到 {len(ctax_result)} 条头版新闻：")
    for news in ctax_result[:3]:  # 只打印前3条预览
        print(f" - [{news['category']}] {news['title']}\n   {news['url']}")
        
    print("\n" + "-"*50 + "\n")
    
    # 2. 测试会计视野
    esnai_result = crawl_esnai_law()
    print(f"【会计视野法规库】共抓取到 {len(esnai_result)} 条最新政策法规：")
    for news in esnai_result[:3]: # 只打印前3条预览
        print(f" - [{news['category']}] {news['title']}\n   {news['url']}")
        
    print("\n" + "-"*50 + "\n")
    
    # 3. 测试新增站点
    chinatax_result = crawl_chinatax()
    print(f"【国家税务总局】共抓取到 {len(chinatax_result)} 条政策：")
    
    shui5_result = crawl_shui5()
    print(f"【税屋】共抓取到 {len(shui5_result)} 条政策：")
    
    mof_result = crawl_mof()
    print(f"【财政部】共抓取到 {len(mof_result)} 条政策：")