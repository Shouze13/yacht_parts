import scrapy
import re


class YachtSpider(scrapy.Spider):
    name = "yacht"
    start_urls = ["https://yacht-parts.ru/catalog/"]

    def parse(self, response):
        for i in response.css("""a[href="/catalog/other_brands/"] + div.menu_level_3"""):
            brands = { " ".join(re.findall(r'\b[A-Za-z]+\b',j)) for j in i.css("div.menu_level_3 a::text").getall()}
        for category in response.css("div.menu_level_2.clearfix"):
            category_name = category.css("a::text").get()
            # if category_name not in ["Брендовый раздел", "Каталог Osculati"]:
            for sub in category.css("div.menu_level_3 a::attr(href)"):
                sub_page = response.urljoin(str(sub))   
                yield scrapy.Request(sub_page, callback = self.parse_products, meta={"category":  category_name, "brands": brands})
        

    def parse_products(self, response):
        category_name = response.meta.get("category", "Неизвестная категория")
        brands = response.meta.get("brands")
        for product in response.css("div.list_item_wrapp.item_wrap"):
            for i in brands:
                if i in product.css("""div.desc_name span[itemprop="name"]::text""").get():
                    brand = i
                    break
                else:
                    brand = "Неизвестный бренд"
            yield { 
            "Категория": category_name,
            "Наименование товара": product.css("""div.desc_name span[itemprop="name"]::text""").get(),
            "Артикул": product.css("table.props_list.prod span::text").getall()[1].split(),
            "Бренд": brand,
            "Цена": product.css("div.price.discount span::text").get(),
            "Описание": product.css("div.preview_text::text").get(),
            "Ссылки на изображения": response.urljoin(product.css("""img[style="display:none;"]::attr(src)""").get())
            }