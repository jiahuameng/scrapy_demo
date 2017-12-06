# -*- coding: utf-8 -*-
import json
import scrapy
import js2xml
from ..items import HuabanImgItem


class HuabanSpider(scrapy.Spider):
    name = 'huaban'
    allowed_domains = ['huaban.com']
    url = 'http://huaban.com/favorite/beauty/'
    async_url = 'http://huaban.com/favorite/beauty/?max={}&limit=100&wfl=1'
    start_urls = [url]
    download_url = 'http://img.hb.aicdn.com/'
    json_headers = {
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept': 'application/json',
        'X-Request': 'JSON',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
    }

    def parse(self, response):
        jscode = response.xpath('//script[contains(., "app.page = app.pag")]/text()').extract_first()
        if jscode:
            parsed_js = js2xml.parse(jscode)
            pin_ids = parsed_js.xpath('//property[@name="pin_id"]/number/@value')
            max_pin_id = max([int(pin) for pin in pin_ids]) if pin_ids else None
            print max_pin_id
            if max_pin_id:
                yield scrapy.Request(
                    self.async_url.format(max_pin_id), callback=self.parse_json, headers=self.json_headers)

    def parse_json(self, response):
        content = json.loads(response.body)
        if content:
            pins = content.get('pins', [])
            pin_ids = [pin['pin_id'] for pin in pins if pin.get('pin_id')]
            next_pin_id = min([int(pin) for pin in pin_ids]) if pin_ids else None
            image_urls = ['{}{}'.format(self.download_url, pin.get('file', {}).get('key'))
                          for pin in pins if pin.get('file') and pin.get('file', {}).get('key')]
            item = HuabanImgItem()
            item['image_urls'] = image_urls
            yield item
            print next_pin_id
            # if next_pin_id:
            #     yield scrapy.Request(
            #         self.async_url.format(next_pin_id), callback=self.parse_json, headers=self.json_headers)

