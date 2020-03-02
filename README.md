# Supernatural Kills

Death data from the Supernatural TV show.

Source: http://www.supernaturalwiki.com/Table_of_Death

## Scraping and Playing with Data

```python
from supernatural import Supernatural

# Instantiate the class
sn = Supernatural()

# Force the download of the raw data
sn.download(force=True)

# Parse that data
sn.parse()

# Access to the data of episode 2 of season 14
print(sn.kills["14.02"])

# Dump all episodes data
sn.dump()

# Export JSON data
sn.export_json()
```
