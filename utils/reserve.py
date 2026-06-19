def _get_page_token(self, url, require_value=True):
        # 预先设置 Session 的适配器，增加重试机制，防止高并发丢包
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        adapter = HTTPAdapter(max_retries=Retry(total=2, backoff_factor=0.1))
        self.requests.mount("https://", adapter)
        
        # 极简 Headers，避免过大的包头被服务器识别为特征
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Connection": "keep-alive"
        }

        # 核心：循环内不打印日志，不进行不必要的计算，只专注获取数据
        for i in range(3): 
            try:
                # 设置极短超时，高并发下如果 1 秒没回包，基本就没戏了
                response = self.requests.get(url=url, headers=headers, timeout=1.0)
                if response.status_code != 200:
                    continue
                    
                html = response.text
                # 直接正则提取，不使用任何复杂逻辑
                token_match = re.search(r'id="submit_enc"\s+value="([^"]+)"', html)
                token = token_match.group(1) if token_match else None
                
                value = ""
                if require_value:
                    val_match = re.search(r'id="algorithm"\s+value="([^"]+)"', html)
                    value = val_match.group(1) if val_match else ""
                
                if token:
                    return token, value
                
            except Exception:
                continue
                
        return None, None
