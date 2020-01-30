# scp_fetcher_bs4
Fetch information about _almost_ every SCP from SCP Wiki pages.

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
usage: scp_fetcher_bs4 [-h] -u URL [-p] [-v]

Fetch SCP-related information from a given SCP Wiki page

optional arguments:
  -h, --help         show this help message and exit
  -u URL, --url URL  the URL of the Wiki page to fetch from
  -p, --porcelain    machine-readable output
  -v, --verbose      be more verbose


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
ERROR:root:Exception caught: no object id definition! Is the format correct?

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