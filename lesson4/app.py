from lxml import etree
# import requests

tree =etree.parse("src/web_page.html")
# title_element = tree.find("body/ul/li")
# list_item = tree.findall("body/ul/li")
# # print(title_element.text)
# # print(list_item)
# for li in list_item: 
#     a = li.find("a")
#     if a is not None:
#         print(f'{li.text.strip()} {a.text}')
#     else:
#         print(li.text)
title_element = tree.xpath("//title")
print(title_element[0].text)
title_element = tree.xpath("//p/text()")[0]
print(title_element)