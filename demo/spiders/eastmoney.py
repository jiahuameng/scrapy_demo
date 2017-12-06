# -*- coding: utf-8 -*-
import re
import scrapy
import numpy as np
from ..items import MacroDataItem


class EastmoneySpider(scrapy.Spider):
    name = 'eastmoney'
    allowed_domains = ['eastmoney.com']
    start_urls = [
        'http://www.eastmoney.com'
    ]
    data_url = 'http://datainterface.eastmoney.com/EM_DataCenter/XML.aspx?type=GJZB&style=ZGZB&mkt={}&r={}&code=&name=&stat='
    type_dict = {
        'cpi': 19,  # 居民消费价格指数
        'gdp': 20,  # 国内生产总值
        'pmi': 21,  # 采购经理人指数
        'ppi': 22,  # 工业品出厂价格指数
        'fdi': 15,  # 外商直接投资
        'gyzjz': 0,  # 工业增加值
        'hjwh': 16,  # 外汇黄金
        'xzxd': 7,  # 新增信贷
        'gdzctz': 12,  # 固定资产投资
        'hbgyl': 11,  # 货币供应量
        'hgjck': 1,  # 海关进出口
    }

    def parse(self, response):
        for type, mkt in self.type_dict.iteritems():
            yield scrapy.Request(self.data_url.format(mkt, np.random.random()), callback=self.parse_data,
                                 meta={'type': type})

    def parse_data(self, response):
        type = response.meta.get('type')
        series = response.xpath('series/value/text()').extract()
        cpis = response.xpath('//graph[@gid="1"]/value/text()').extract()
        data = {self._format_series(s, type): cpi for s, cpi in zip(series, cpis)}
        yield MacroDataItem(name=type, data=data)

    def _format_series(self, s, type):
        if type in ['gdp']:
            return self._format_quarter(s)
        else:
            return self._format_month(s)

    def _format_month(self, s):
        m = re.match(ur'(\d+)年(\d+)月', s, re.I)
        year, month = (int(m.group(1)), int(m.group(2))) if m else (None, None)
        return '{:02d}.{:02d}'.format(year, month) if year and month else ''

    def _format_quarter(self, s):
        m = re.match(ur'(\d+)年((\d+)|(\d)-(\d))季度', s, re.I)
        year, quarter = (int(m.group(1)), int(m.group(3)) if m.group(3) else int(m.group(5))) if m else (None, None)
        return '{:02d}.{:02d}'.format(year, quarter) if year and quarter else ''





