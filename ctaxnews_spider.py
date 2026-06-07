import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

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
                
                # 【新增防御】过滤掉侧边栏的老旧专题、汇编，以及带有 action=subject 的目录页
                if 'action=subject' in href or '汇编' in title or '专辑' in title:
                    continue
                # 【新增防御】直接过滤掉标题中明显带有旧年份的内容
                if any(year in title for year in ['2014', '2015', '2016', '2017', '2018']):
                    continue
                    
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
        
        for a_tag in soup.select('a'):
            title = a_tag.text.strip()
            href = a_tag.get('href', '')
            if title and '号' in title and len(title) > 10: 
                # 【新增防御】过滤掉网页底部的 ICP 备案、公网安备、版权声明等系统词汇
                if any(kw in title for kw in ['ICP', '公网安备', '版权', '主办', '技术支持']):
                    continue
                
                full_url = href if href.startswith('http') else "https://fgk.chinatax.gov.cn" + href
                news_items.append({
                    "title": title,
                    "url": full_url,
                    "source": "国家税务总局",
                    "category": "policy",
                    "publishedAt": datetime.now().strftime("%Y-%m-%d") 
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
                
                # 【关键优化】税屋的首页分为多个区块，不要限制特定的路径。
                # 只要它是装在 li 列表里、以 .html 结尾的正式内容页链接，并且标题足够长，就全部抓取。
                if title and len(title) > 8 and href.endswith('.html'):
                    full_url = href if href.startswith('http') else "https://www.shui5.cn" + href
                    news_items.append({
                        "title": title,
                        "url": full_url,
                        "source": "税屋",
                        "category": "policy",
                        "publishedAt": datetime.now().strftime("%Y-%m-%d")
                    })
                    
        # 去重（因为推荐和资讯区块可能有重复的文章）
        unique_news = []
        seen_urls = set()
        for item in news_items:
            if item["url"] not in seen_urls:
                unique_news.append(item)
                seen_urls.add(item["url"])
                
        return unique_news[:15]
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

def save_to_json(data, filename="tax_news.json"):
    """
    将整合后的所有新闻数据保存为 JSON 文件
    """
    try:
        # ensure_ascii=False 保证中文正常显示，indent=2 让生成的 JSON 有良好的排版格式
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 成功！已将 {len(data)} 条财税动态保存至本地文件: {filename}")
    except Exception as e:
        print(f"\n❌ 保存 JSON 文件失败: {e}")

# ==========================================
# 本地测试代码
# ==========================================
if __name__ == "__main__":
    print("开始执行财税新闻爬虫矩阵...\n")
    
    # 建立一个空列表，用于装载所有站点的结果
    all_tax_news = []
    
    # 1. 抓取税务报
    ctax_result = crawl_ctaxnews()
    all_tax_news.extend(ctax_result) # 汇总数据
    print(f"【中国税务报】共抓取到 {len(ctax_result)} 条头版新闻。")
        
    print("-" * 40)
    
    # 2. 抓取会计视野
    esnai_result = crawl_esnai_law()
    all_tax_news.extend(esnai_result)
    print(f"【会计视野法规库】共抓取到 {len(esnai_result)} 条最新政策法规。")
        
    print("-" * 40)
    
    # 3. 抓取国家税务总局
    chinatax_result = crawl_chinatax()
    all_tax_news.extend(chinatax_result)
    print(f"【国家税务总局】共抓取到 {len(chinatax_result)} 条政策。")
    
    print("-" * 40)
    
    # 4. 抓取税屋
    shui5_result = crawl_shui5()
    all_tax_news.extend(shui5_result)
    print(f"【税屋】共抓取到 {len(shui5_result)} 条政策。")
    
    print("-" * 40)
    
    # 5. 抓取财政部
    mof_result = crawl_mof()
    all_tax_news.extend(mof_result)
    print(f"【财政部】共抓取到 {len(mof_result)} 条政策。")
    
    print("=" * 50)
    
    # 最后一步：统一保存为 JSON 文件
    save_to_json(all_tax_news)