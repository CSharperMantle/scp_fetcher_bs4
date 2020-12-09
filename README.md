# scp_fetcher_bs4
Fetch information about _almost_ every SCP from SCP Wiki pages, as well as page source!

## Introduction
`scp-fetcher-bs4` is a multi-purpose information gatherer for Wikidot-hosted SCP Foundation Wiki. Powered by `requests`,
`bs4` and `selenium`, `scp-fetcher-bs4` can handle a large variety of SCPs and

## Features
* One-key SCP information fetcher
* Complete support for ACS (Anomaly Classification System) documents
* Growing support for many non-ACS formats
* Complete support for page source fetching (authentication required)
* Support for batch processing

## Installation
Use `requirements.txt` or `setup.py` to install dependencies.

Webdrivers are needed to enable page source fetching. Please refer to
[the Selenium docs](https://www.selenium.dev/documentation/en/selenium_installation/installing_webdriver_binaries/) for
more information about installing webdrivers.

Currently `scp-fetcher-bs4` supports 2 widely-adopted browsers: Chrome & Firefox.

## Examples

### 1. Using code
```python
from scp_fetcher_bs4.scp_info import SCPInfo, SCPParsingError
import requests


_TEMPLATE = """
Information about SCP-{0}:
\tObject Class: {1}
"""


def fetch_scp_173():
    """
    Fetch the information about SCP-173 from http://scp-wiki.wikidot.com
    """
    req = requests.get('http://scp-wiki.wikidot.com/scp-173')
    text = req.text
    req.close()

    try:
        scp_info = SCPInfo.from_html_page(text)
    except SCPParsingError:
        raise
    print(_TEMPLATE.format(scp_info.id, scp_info.object_class))


if __name__ == '__main__':
    fetch_scp_173()

```

### 2. Using CLI

```text
> python scp_fetcher_bs4 -h
Fetch SCP-related information from a given SCP Wiki page

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     the URL of the Wiki page to fetch from
  -p, --porcelain       machine-readable output
  -v, --verbose         be more verbose
  -f, --force-continue  do not stop when an error occurs. No effects with
                        porcelain run
  -s, --fetch-only-source
                        fetch the page source with Selenium
  -d DRIVER, --driver DRIVER
                        webdriver used by Selenium

> python scp_fetcher_bs4 -u http://scp-wiki.wikidot.com/scp-173
Information about SCP-173:
        Object Class: euclid


> python scp_fetcher_bs4 -u http://scp-wiki.wikidot.com/scp-4971
Information about SCP-4971:
        Clearance Level: 4/secret
        Containment Class: esoteric
        Secondary Class: cernunnos
        Disruption Class: ekhi
        Risk Class: danger



> python scp_fetcher_bs4 -u http://scp-wiki.wikidot.com/scp-4958 -p
<SCPInfo 4958 1 keter True none ekhi notice>

> python scp_fetcher_bs4 -u http://scp-wiki.wikidot.com/scp-682 -u http://scp-wiki.wikidot.com/scp-4064 -v
INFO:root:fetching http://scp-wiki.wikidot.com/scp-682
Information about SCP-682:
        Object Class: keter

INFO:root:fetching http://scp-wiki.wikidot.com/scp-4064
Information about SCP-4064:
        Clearance Level: 4/secret
        Containment Class: keter
        Secondary Class: none
        Disruption Class: dark
        Risk Class: warning


> python scp_fetcher_bs4 -u http://www.github.com
ERROR:root:Exception caught: no object id definition! Is the page an SCP with correct format?


> python scp_fetcher_bs4 -u http://scp-wiki-cn.wikidot.com/statement-on-disabling-offset -s -d firefox
Please login in the newly opened browser window. This app will NOT record any of your passwords, username and so on. Press ENTER when finished.>

Source code for page '关于新增迭代页（offset）及内容方面限制的说明':
---BEGIN SOURCE CODE---
++ 一.关于迭代

经管理组讨论，由于以下几个理由，迭代页（即offset功能）将被限制在一般条目（即SCP-CN各序列）中限制使用。

# 版面过于复杂导致条目自身文案的可读性下降，不利于信息的正常传播。
# offset（迭代）对wiki统计和支持有缺陷，在技术上不便于统计管理
# 迭代有滥用趋势，不利于新点子的创造发掘。

综上所述，即日起，**在普通条目中将禁止以一切形式使用多于3个迭代页**（条目本身算一个页面，即最高不能超过offset/2）。

+++ 细则

# 此限制仅在正式条目中生效，不影响诸如J/EX/故事/个人页面等其他页面。 **不影响已发布的条目。**
# 迭代页也包括使用CSS或javascrpit来实现的类似效果，但具体是否超过3页限制则视乎情况具体分析。
# 迭代次数限制与文本长度无关，空迭代页或跳转也计为1页；同时对应地，无论多么长的文本只要迭代页数符合要求就不受影响。
# 对于特别喜欢迭代页的创作需求，未来在特殊情况下会放开关于迭代的限制（如使用特定的tag等）

++ 二、关于内容限制的变更

以下禁止内容即日生效。已有的内容将逐渐被删除或被编辑掉。

# 禁止正面描写自杀、自残行为。
# 禁止模仿中华人民共和国政府公告或政府机关/职务名称的文本。

以下内容不再被提倡，并可能在极端情况下被编辑。
强烈推荐用隐晦的临床语气配合黑条███或[数据删除]来达到类似或更优的描写效果。这也是其他语言社群一贯的主流策略。

# 涉及直接描写血腥、猎奇的。
# 直接涉及生殖相关行为及人类器官的
# 对精神健康有不良导向的

以上新限制将应用在包括但不限于条目、故事、个人主页、设定中心，甚至是部分翻译和艺作/图片。

**SCP基金会不是一个创作非常容易的题材，它甚至不是一个纯粹的中文题材，它有相对于其他题材很高的门槛和难度。如果你因为其他人设法帮你降低了某些门槛就试图去按你的兴趣改变
所有标准，那么委婉地说，其他的创作题材显然更适合您。**
---END OF SOURCE CODE---

ERROR:root:Exception caught: unknown page type! Is the page an SCP with correct format?


```

## Supported formats
### 1. Classical
Classical formats are the oldest Wiki page format.

E.g.: [SCP-173](http://scp-wiki.wikidot.com/scp-173)

**Key feature:**

```html
<p>
    <strong>Item #:</strong>
    SCP-173
</p>
<p>
    <strong>Object Class:</strong>
    Euclid
</p>
```

### 2. Anomaly Classification System

A enhancement to the classical object class system.

> ACS is a new classification system that adds further depth to the already existing Object Class system.
> It is not intended to replace the current Object Class system. 
> It is only meant to enhance it.

E.g.: [SCP-4971](http://scp-wiki.wikidot.com/scp-4971)

**Key feature:**

```html
<div class="anom-bar-container item-4971 clear-4 esoteric cernunnos ekhi danger {$american}">
...
</div>
```

### 3. Semi-classical _(partial support)_

A format which has classical features and an additional Clearance Level.

E.g.: [SCP-4973](http://scp-wiki.wikidot.com/scp-4973)

**Key feature:**

```html
<div>
    <span class="ocb-text">Item #:</span>
    <!-- There's a space here! -->
    <span class="ocb-text">SCP-4973</span>
</div>
...
<div class="leveltext-container">
    <div>Level 4/4973</div>
    <div>CLASSIFIED</div>
</div>
```

**Item # and Object Class support only, for now.**

## License
```text
Copyright (C) 2020-2021 Rong "Mantle" Bao (CSharperMantle)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/ .
```

## Copyright notice on SCP Foundation-related content
[The SCP Foundation Wiki](http://scp-wiki.wikidot.com) and contents are licensed under 
a [Creative Commons Attribution-ShareAlike 3.0 Unported License](https://creativecommons.org/licenses/by-sa/3.0/).

## TODO list
* [ ] Finish implementing other types of SCPs
* [ ] Switch to XPath or else to beautify the identification process
